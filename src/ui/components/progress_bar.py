import threading
import queue
from functools import partial
import tkinter as tk
from tkinter import ttk
from src.ui.base import set_text

class ProgressBar:
    def __init__(self, root, parent):
        self.root = root
        self.parent = parent
        self.progress_queue = queue.Queue()
        self.progress_cnt = 0 # finished count
        self.progress_lock = threading.Lock()
        self.progress_max = 0 # total count
        self.construct()

    def update(self, pb:ttk.Progressbar, label:ttk.Label, q:queue, event):
        perc = round(q.get()/self.progress_max, 2) * 100.0
        if perc <= 100.0:
            pb['value'] = perc
            formatted_number = "{:.2f}%".format(perc)
            set_text(label, formatted_number)

    def construct(self):
        self.progressbar = ttk.Progressbar(self.parent, mode="determinate", orient="horizontal", length=200)
        self.progressbar.pack(side=tk.LEFT)
        
        self.l_progress = tk.Label(self.parent, text="")
        self.l_progress.pack(side=tk.LEFT)

        self.update_handler = partial(self.update, self.progressbar, self.l_progress, self.progress_queue)
        self.root.bind('<<Progress>>', self.update_handler)

    def on_update(self):
        with self.progress_lock:
            self.progress_cnt += 1
            self.progress_queue.put(self.progress_cnt)
            self.root.event_generate('<<Progress>>')