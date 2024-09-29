from tkinter import ttk
from PIL import ImageTk
import tkinter as tk
import tkinter.font as font
from defs import PAD_H, PAD_V
from . import PATH_ICON
from .common_ui import get_text, set_text, validate_page
import math
import os
from common import clamp

class Paging:
    def __init__(self, root, callback=None) -> None:
        self.root = root
        self.cur_page = 1
        self.total_pages = 1
        self.page_size = 30
        self.callback = callback
        self.open()

    def open(self):
        icon_left = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'left.png'))
        icon_right = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'right.png'))
        
        self.frame = tk.Frame(self.root, width=10)
        self.frame.pack(padx=10, pady=10, fill=tk.X)
        self.frame.columnconfigure(index=1, weight=1, uniform="equal")

        left_frame = tk.Frame(self.frame)
        left_frame.grid(row=0, column=0, sticky=tk.EW)

        vcmd = (self.root.register(validate_page)) 
        
        label_page = tk.Label(left_frame, text="Page:", width=4)
        label_page.pack(side=tk.LEFT, padx=(0, PAD_H))
        self.entry_page = ttk.Entry(left_frame, width=4, validate='all', validatecommand=(vcmd, '%P'))
        self.entry_page.pack(side=tk.LEFT, padx=(0, PAD_H))
        self.entry_page.bind("<Return>", self.on_page_submitted)

        self.btn_left = tk.Button(left_frame, image=icon_left, relief=tk.FLAT, cursor='hand2', command=self.prev_page)
        self.btn_left.image = icon_left
        self.btn_left.pack(side=tk.RIGHT)

        right_frame = tk.Frame(self.frame)
        right_frame.grid(row=0, column=2, sticky=tk.EW)

        self.btn_right = tk.Button(right_frame, image = icon_right, relief=tk.FLAT, cursor='hand2', command=self.next_page)
        self.btn_right.image = icon_right
        self.btn_right.pack(side=tk.LEFT)

        self.frame_paging = tk.Frame(self.frame, width=2)
        self.frame_paging.grid(row=0, column=1)
        
        self.l_page = tk.Label(right_frame, text="", width=8)
        self.l_page.pack(side=tk.RIGHT, padx=(PAD_H * 2,0))
    
    def show_paging(self):
        for child in self.frame_paging.winfo_children():
            child.destroy()

        if self.total_pages <= 0: 
            return

        prev = 0
        for index, n in enumerate(get_pages(self.cur_page, self.total_pages)):
            if index > 0 and prev+1 != n:
                label = tk.Label(self.frame_paging, text="...", width=2)
                label.grid(row=0, column=n-1)    
            
            btn = tk.Button(self.frame_paging, text=n, relief=tk.FLAT, cursor='hand2', command=lambda number=n: self.change_page(number), width=2)
            if self.cur_page == n:
                btn["font"]= font.Font(weight="bold")
                btn["fg"]= "#6563FF"
            btn.grid(row=0, column=n)
            prev = n

    def change_page(self, number):
        self.cur_page = number
        if self.callback is not None:
            self.callback()

    def next_page(self):
        self.cur_page = clamp(self.cur_page+1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def prev_page(self):
        self.cur_page = clamp(self.cur_page-1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def update(self, num:int):
        self.total_pages = math.ceil(num/self.page_size)
        print(f"found {num} items")
        self.show_paging()
        start, end = self.get_range(num)
        n_count = end - start
        self.l_page.config(text=f"{n_count} of {num}")
        set_text(self.entry_page, self.cur_page)
        return start, end

    def get_range(self, num:int):
        start = (self.cur_page-1) * self.page_size
        end = clamp(self.cur_page * self.page_size, start, num)
        return start, end
    
    def on_page_submitted(self, event):
        new_page = get_text(self.entry_page)
        if new_page:
            page_num = int(new_page)
            self.cur_page = clamp(page_num, 1, self.total_pages)
            self.change_page(self.cur_page)

def get_pages(current_page=1, total_pages=1, max_size=5):
    out_arr = []
    half = math.floor(max_size/2)
    min = clamp(current_page-half, 1, total_pages)
    max = clamp(current_page+half, 1, total_pages)
    if current_page-half < 1:
        max -= (current_page-half - 1)
    elif current_page+half > total_pages:
        min -= (current_page+half - total_pages)

    if total_pages < max_size:
        min = 1
        max = total_pages
        
    for n in range(min, max+1):
        out_arr.append(n) 
    
    if 1 not in out_arr:
        out_arr.append(1)
    
    if total_pages not in out_arr:
        out_arr.append(total_pages)
    
    out_arr.sort()
    return out_arr