"""
image_handler.py: contains class definition for loading images
"""

from typing import Union
from threading import Thread, Event
import concurrent.futures
from PIL import Image, ImageTk
from .common import is_valid_file

def get_image(path:str, width:int, height:int, keep_ratio:bool = True):
    """
    loads image with ImageTK library
    The loaded image is resized based on the provided width and height
    Args:
        path (str): the image directory
        width (int): the new width of the image
        height (int): the new height of the image
        keep_ratio (bool): whether to retain the original ratio when resizing
    """
    if not is_valid_file(path):
        return None, path

    img = Image.open(path)

    # Resize the image to fit the target dimensions while preserving aspect ratio
    if keep_ratio:
        aspect_ratio = img.width / img.height

        if width / aspect_ratio <= height:
            new_width = width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = height
            new_width = int(new_height * aspect_ratio)

        w = max(1, new_width)
        h = max(1, new_height)
    else:
        w = max(1, width)
        h = max(1, height)

    return ImageTk.PhotoImage(img.resize((w, h), Image.Resampling.LANCZOS)), path

class ImageHandler(Thread):
    """
    This class inherits from thread
    loads images async
    on_finish callback called when all images have been loaded
    """
    def __init__(
        self,
        directory:Union[str, list],
        width:int,
        height:int,
        on_finish:callable,
        keep_ratio:bool=True
    ):
        super().__init__()
        self.directory = directory
        self.width = width
        self.height = height
        self.on_finish = on_finish
        self.keep_ratio = keep_ratio
        self.daemon = False
        self._stop_event = Event()
        self.start()

    def run(self):
        if isinstance(self.directory, str):
            image, path = get_image(self.directory, self.width, self.height, self.keep_ratio)
            self.on_finish(image)
        elif isinstance(self.directory, list):
            result = [None] * len(self.directory)
            futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for d in self.directory:
                    futures.append(executor.submit(
                        get_image,
                        d,
                        self.width,
                        self.height,
                        self.keep_ratio
                        )
                    )

            for future in concurrent.futures.as_completed(futures):
                image, path = future.result()
                index = self.directory.index(path)
                result[index] = image

            self.on_finish(result)

    def stop(self):
        """
        stop process
        """
        self._stop_event.set()
