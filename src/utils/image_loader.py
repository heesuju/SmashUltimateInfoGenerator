import os
import requests
import hashlib
import weakref
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap

CACHE_DIR = "data/cache/thumbnails"

class ImageWorker(QThread):
    finished = pyqtSignal(str, str) # url, local_path
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            if not self.url:
                self.finished.emit(self.url, "")
                return

            # Ensure cache directory exists
            if not os.path.exists(CACHE_DIR):
                os.makedirs(CACHE_DIR)
                
            # Generate filename from hash of URL
            filename = hashlib.md5(self.url.encode()).hexdigest() + ".jpg" # Assume jpg for simple gamebanana thumbs
            local_path = os.path.join(CACHE_DIR, filename)
            
            # Check if exists
            if os.path.exists(local_path):
                self.finished.emit(self.url, local_path)
                return
                
            # Download
            with requests.Session() as session:
                session.trust_env = False
                response = session.get(self.url, stream=True, timeout=10)
                
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    self.finished.emit(self.url, local_path)
                else:
                    self.finished.emit(self.url, "")
        except Exception as e:
            print(f"Error downloading image {self.url}: {e}")
            self.finished.emit(self.url, "")

class ImageLoader(QObject):
    _instance = None
    image_ready = pyqtSignal(str, str) # url, local_path
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self.active_downloads = {} # url -> worker
        self.pending_callbacks = {} # url -> list[callbacks]
        self.download_queue = []  # Queue of URLs waiting to download
        self.max_concurrent_downloads = 3  # Limit concurrent downloads
        
    def load_image(self, url: str, callback, widget=None):
        """
        Load an image from URL. 
        callback(local_path) will be called when ready.
        widget: Optional QWidget to track - if destroyed, callback is skipped.
        """
        if not url:
            callback("")
            return

        filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
        local_path = os.path.join(CACHE_DIR, filename)
        if os.path.exists(local_path):
            callback(local_path)
            return

        if url not in self.pending_callbacks:
            self.pending_callbacks[url] = []
        
        # Store weak reference to widget if provided, for validity check later
        if widget is not None:
            widget_ref = weakref.ref(widget)
        else:
            widget_ref = None
        self.pending_callbacks[url].append((callback, widget_ref))
        
        if url not in self.active_downloads and url not in self.download_queue:
            self.download_queue.append(url)
            self._process_queue()
    
    def cancel_callback(self, url: str, callback):
        """
        Cancel a pending callback for a specific URL.
        Called when a widget is being destroyed to prevent callbacks to dead objects.
        """
        if url in self.pending_callbacks:
            self.pending_callbacks[url] = [
                (cb, ref) for cb, ref in self.pending_callbacks[url] 
                if cb != callback
            ]
            # Clean up empty entries
            if not self.pending_callbacks[url]:
                del self.pending_callbacks[url]
    
    def cancel_all_for_widget(self, widget):
        """
        Cancel all pending callbacks for a specific widget.
        """
        for url in list(self.pending_callbacks.keys()):
            self.pending_callbacks[url] = [
                (cb, ref) for cb, ref in self.pending_callbacks[url]
                if ref is None or (ref() is not None and ref() is not widget)
            ]
            if not self.pending_callbacks[url]:
                del self.pending_callbacks[url]
            
    def _process_queue(self):
        """Start downloads from queue up to max concurrent limit"""
        while (len(self.active_downloads) < self.max_concurrent_downloads and 
               len(self.download_queue) > 0):
            url = self.download_queue.pop(0)
            worker = ImageWorker(url)
            worker.finished.connect(self._on_download_finished)
            self.active_downloads[url] = worker
            worker.start()
            
    def _on_download_finished(self, url, local_path):
        if url in self.active_downloads:
            del self.active_downloads[url]
            
        if url in self.pending_callbacks:
            callbacks = self.pending_callbacks.pop(url)
            for cb, widget_ref in callbacks:
                # Check if widget is still valid before calling callback
                if widget_ref is not None:
                    widget = widget_ref()
                    if widget is None:
                        # Widget was destroyed, skip this callback
                        continue
                try:
                    cb(local_path)
                except RuntimeError:
                    # Widget was deleted, ignore
                    pass
        
        self._process_queue()
