import tkinter as tk
import defs
import os
from threading import Thread
from PIL import Image, ImageTk

class ImageResize(Thread):
    def __init__(self, directory, width, height, callback):
        super().__init__()
        self.callback = callback
        self.directory = directory
        self.width = width
        self.height = height

    def set_image(self):
        image_path =  self.directory    
        if not image_path or not os.path.exists(image_path):
            return

        label_width = self.width
        label_height = self.height
        resized_image = self.resize_image(image_path, label_width, label_height)
        image = ImageTk.PhotoImage(resized_image)
        self.callback(image)

    def resize_image(self, image_path, target_width, target_height):
        img = Image.open(image_path)
        aspect_ratio = img.width / img.height
        
        # Resize the image to fit the target dimensions while preserving aspect ratio
        if target_width / aspect_ratio <= target_height:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(new_height * aspect_ratio)

        w = max(1, new_width)
        h = max(1, new_height)

        return img.resize((w, h), Image.Resampling.LANCZOS)
    
    def run(self):
        self.set_image()