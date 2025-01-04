import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES
from PIL import ImageTk
from typing import Union
from .checkbox_treeview import Treeview
from src.utils.image_handler import ImageHandler

class ImageTreeview(Treeview):
    def __init__(self, root, parent, columns:list, on_drag_drop:callable=None, on_selected:callable=None, on_double_clicked:callable=None, 
                 on_escape:callable=None, on_space:callable=None, on_return:callable=None, on_up:callable=None, on_down:callable=None, 
                 on_right:callable=None, on_left:callable=None, show_header:bool=True) -> None:

        self.thumbnails = []    
        self.img_dirs = []
        self.image_handler = None

        self.root = root
        self.parent = parent
        self.columns = columns
        self.on_drag_drop = on_drag_drop
        self.on_selected = on_selected
        self.on_double_clicked = on_double_clicked
        self.on_escape = on_escape
        self.on_space = on_space
        self.on_return = on_return
        self.on_up = on_up
        self.on_down = on_down
        self.on_right = on_right
        self.on_left = on_left
        self.show_header = show_header
        
        self.widget = None
        self.pos_x = 0
        self.pos_y = 0

        self.construct()

    def construct(self):
        style = ttk.Style(self.root)
        style.configure("Treeview", rowheight=20)
        style.configure("Custom.Treeview", background="white", foreground="Black", rowheight=20)
        style.map('Custom.Treeview', background=[('selected','lightblue')],foreground=[('selected','Black')])
        style.configure("Custom1.Treeview",background="white", foreground="Black", rowheight=60)
        style.map('Custom1.Treeview', background=[('selected','lightblue')],foreground=[('selected','Black')])
        heading_config = ("headings", "tree") if self.show_header else ("tree")
        column_names = []
        display_columns = []

        for n, col in enumerate(self.columns):
            if n > 0:
                column_names.append(col["name"])
                if col.get("show", False):
                    display_columns.append(col["name"])
        
        self.widget = ttk.Treeview(self.parent, style="Custom1.Treeview", columns=column_names, displaycolumns=display_columns, show=heading_config)
        
        def treeview_sort_column(tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)

            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            tv.heading(col, command=lambda: \
                    treeview_sort_column(tv, col, not reverse))

        for n, col in enumerate(self.columns):
            stretch = tk.YES if col.get("stretch", False) else tk.NO
            
            if n == 0:
                self.widget.column(f"#{n}", minwidth=col.get("minwidth"), width=col.get("width"), stretch=stretch)
                self.widget.heading(f"#{n}", text=col.get("name", ""))
            else:
                self.widget.column(col.get("name", ""), minwidth=col.get("minwidth"), width=col.get("width"), stretch=stretch)
        

        for col in display_columns:
            self.widget.heading(col, text=col, command=lambda _col=col: \
                                  treeview_sort_column(self.widget, _col, False))
        
        self.widget.pack(padx=10, fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.widget, orient="vertical", command=self.widget.yview)
        self.widget.configure(yscrollcommand=self.scrollbar.set)
        
        if self.on_drag_drop is not None:
            self.widget.drop_target_register(DND_FILES)
            self.widget.dnd_bind('<<Drop>>', lambda e: self.on_drag_drop(e.data))

        if self.on_selected is not None:
            self.widget.bind('<<TreeviewSelect>>', self.on_selected)
        
        self.widget.bind('<Button-1>', self.on_clicked)

        if self.on_escape is not None:
            self.widget.bind('<Escape>', self.on_escape)

        if self.on_double_clicked is not None:
            self.widget.bind("<Double-1>", self.on_double_clicked)

        if self.on_space is not None:
            self.widget.bind("<space>", self.on_space)

        if self.on_return is not None:
            self.widget.bind("<Return>", self.on_return)

        if self.on_up is not None:
            self.widget.bind('<Up>', self.on_up)

        if self.on_down is not None:
            self.widget.bind('<Down>', self.on_down)

        if self.on_left is not None:
            self.widget.bind('<Left>', self.on_left)

        if self.on_right is not None:
            self.widget.bind('<Right>', self.on_right)

        self.scrollbar.pack(side="right", fill="y")

        return self.widget
    
    def on_clicked(self, event):
        self.pos_x = event.x
        self.pos_y = event.y

    def on_image_loaded(self, img:Union[str, list]):
        if isinstance(img, str):
            self.thumbnails = [img]
        elif isinstance(img, list):
            self.thumbnails = img
            items = self.get_items()
            for n, thumbnail in enumerate(self.thumbnails):
                if n <= len(items) - 1:
                    item_id = items[n]
                    try:
                        if self.widget.exists(item_id):
                            self.widget.item(item_id, image=thumbnail)
                    except Exception as e:
                        print(f"id {item_id} does not exist yet.")

    def populate_items(self, img_dirs:list[str], values:list[list[str]], checked_arr:list[bool]):
        self.clear()
        
        if self.image_handler is not None:
            self.image_handler.stop()
            self.image_handler = None

        self.img_dirs = img_dirs
        self.thumbnails = [None] * len(img_dirs)

        for value, checked in zip(values, checked_arr):
            self.add_item(values=tuple(value), is_checked=checked)

        self.set_focus()
        self.image_handler = ImageHandler(img_dirs, 100, 60, self.on_image_loaded, False)

    def add_item(self, image:ImageTk.PhotoImage=None, values:list = [], is_checked:bool = False):
        tags = "checked" if is_checked else "unchecked"
        check_mark = "✅" if is_checked else "⬜"
        
        if image is not None:
            self.thumbnails.append(image)
            self.widget.insert("", tk.END, text=check_mark, image=image, values=tuple(values), tags=tags)
        else: 
            self.widget.insert("", tk.END, text=check_mark, values=tuple(values), tags=tags)

    def set_focus(self, row:int=0):
        children = self.widget.get_children()
        if len(children) > 0:
            selected_row = children[row]
            self.widget.focus(selected_row)
            self.widget.selection_set(selected_row)
        self.widget.yview_moveto(row)