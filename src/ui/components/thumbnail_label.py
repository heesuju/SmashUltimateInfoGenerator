from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt6.QtCore import Qt, QSize, QRunnable, QThreadPool, QObject, pyqtSignal
from functools import lru_cache
import requests

class ImageCache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageCache, cls).__new__(cls)
            cls._instance.cache = {}
        return cls._instance

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        # Simple size limit could be added here
        if len(self.cache) > 100:
            # Remove the first item (FIFO-ish behavior for dicts in Python 3.7+)
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value

    def remove(self, path):
        """Remove all cache entries related to a path"""
        keys_to_remove = [k for k in self.cache.keys() if k[0] == path]
        for k in keys_to_remove:
            self.cache.pop(k, None)

class WorkerSignals(QObject):
    result = pyqtSignal(object)

class ImageWorker(QRunnable):
    def __init__(self, path, size):
        super().__init__()
        self.path = path
        self.size = size
        self.signals = WorkerSignals()

    def run(self):
        if not self.path:
            self.signals.result.emit(None)
            return

        if self.path.startswith("http"):
            try:
                response = requests.get(self.path, timeout=10)
                if response.status_code == 200:
                    image = QImage.fromData(response.content)
                else:
                    image = QImage()
            except Exception as e:
                # print(f"Error downloading image: {e}")
                image = QImage()
        else:
            image = QImage(self.path)

        if image.isNull():
            self.signals.result.emit(None)
            return

        # Scale image keeping aspect ratio
        scaled = image.scaled(
            self.size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Make black background canvas
        canvas = QImage(self.size, QImage.Format.Format_ARGB32)
        canvas.fill(QColor("black"))
        
        # Center image onto black canvas
        painter = QPainter(canvas)
        x = (self.size.width() - scaled.width()) // 2
        y = (self.size.height() - scaled.height()) // 2
        painter.drawImage(x, y, scaled)
        painter.end()

        self.signals.result.emit(QPixmap.fromImage(canvas))

class ThumbnailLabel(QLabel):
    def __init__(self, width=320, height=200, parent=None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background-color: black;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thread_pool = QThreadPool.globalInstance()
        self.cache = ImageCache()
        self.current_path = None

    def set_thumbnail(self, path:str):
        self.current_path = path

        if not path:
            self.clear_thumbnail()
            return
            
        cache_key = (path, self.width(), self.height())
        cached_pixmap = self.cache.get(cache_key)
        
        if cached_pixmap:
            self.setPixmap(cached_pixmap)
            return

        # Show loading state or placeholder (just black for now)
        self.clear_thumbnail()
        
        worker = ImageWorker(path, self.size())
        worker.signals.result.connect(lambda pixmap: self.on_image_loaded(pixmap, path))
        self.thread_pool.start(worker)

    def on_image_loaded(self, pixmap, path):
        # Only update if the path matches the currently requested path
        # This prevents race conditions where a newer request finishes after an older one
        if path != self.current_path:
            return

        if pixmap:
            cache_key = (path, self.width(), self.height())
            self.cache.set(cache_key, pixmap)
            self.setPixmap(pixmap)
        else:
            self.clear_thumbnail()

    def clear_thumbnail(self):
        empty = QPixmap(self.size())
        empty.fill(QColor("black"))
        self.setPixmap(empty)