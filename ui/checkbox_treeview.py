import tkinter as tk
from tkinter import ttk

class Treeview:
    def __init__(self, root, show_header:bool=True) -> None:
        self.root = root
        self.show_header = show_header
        self.widget = None
        self.x = 0
    
    def construct(self, cols:list = []):
        show = ("headings", "tree") if self.show_header else ("tree")
        self.widget = ttk.Treeview(self.root, style="Custom.Treeview", columns=cols, show=show)
        self.widget.tag_configure('active', background='lightblue')
        self.widget.bind('<Button-1>', self.on_item_clicked)
        self.widget.bind("<<TreeviewSelect>>", self.on_row_select)
        self.widget.bind("<space>", self.on_row_select_key)
        self.widget.bind("<Return>", self.on_row_select_key)
        self.widget.bind('<Up>', self.on_key_press)
        self.widget.bind('<Down>', self.on_key_press)

        display_columns = cols
        self.widget.column("#0", minwidth=58, width=58, stretch=tk.NO)
        
        for idx, column in enumerate(cols, 1):
            self.widget.column(f"#{idx}", minwidth=140, width=160, stretch=tk.YES)
            self.widget.heading(f"#{idx}", text=column)
        
        self.widget["displaycolumns"]=display_columns
        self.scrollbar = ttk.Scrollbar(self.widget, orient="vertical", command=self.widget.yview)
        self.widget.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        return self.widget
    
    def add_item(self, values:list = [], is_checked:bool = False):
        tags = "checked" if is_checked else "unchecked"
        check_mark = "✅" if is_checked else "⬜"
        self.widget.insert("", tk.END, text=check_mark, values=tuple(values), tags=[tags])

    def remove_item(self, item):
        self.widget.delete(item)

    def get_items(self):
        return self.widget.get_children()

    def select_all(self, is_selected:bool=True):
        for item in self.get_items():
            self.set_row_checked(item, is_selected)

    def clear(self):
        self.widget.selection_clear()
        
        for item in self.get_items():
            self.remove_item(item)

    def get_checked_items(self):
        checked = []
        for item in self.widget.get_children():
            data = self.widget.item(item)
            if "checked" in data.get("tags"):
                checked.append(item)
        return checked
    
    def set_row_checked(self, item, is_checked:bool=True):
        if is_checked:
            self.widget.item(item, tags=["checked"], text="✅")
        else:
            self.widget.item(item, tags=["unchecked"], text="⬜")

    def get_row_text(self, item):
        values = self.widget.item(item)["values"]
        if len(values) > 0:
            return values[0]
        
    def set_row(self, item, values):
        self.widget.item(item, values=tuple(values))

    def get_checked_state(self, item):
        data = self.widget.item(item)
        return "checked" in data.get("tags")
    
    def on_row_select(self, event):
        selected_item = self.widget.focus()
        if not selected_item or self.x == 0:
            return
        self.x = 0
        is_checked = self.get_checked_state(selected_item)
        self.set_row_checked(selected_item, False if is_checked else True)

    def on_row_select_key(self, event):
        selected_item = self.widget.focus()
        if not selected_item:
            return
        self.x = 0
        is_checked = self.get_checked_state(selected_item)
        self.set_row_checked(selected_item, False if is_checked else True)

    def on_key_press(self, event):
        self.x = 0

    def on_item_clicked(self, event):
        self.x = 1