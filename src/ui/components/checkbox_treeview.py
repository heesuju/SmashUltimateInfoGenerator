import tkinter as tk
from tkinter import ttk

CHECKED = "✅"
UNCHECKED = "⬜"

class Treeview:
    def __init__(self, root, show_header:bool=True) -> None:
        self.root = root
        self.show_header = show_header
        self.widget = None
        self.is_left_click = False
    
    def construct(self, cols:list = []):
        show = ("headings", "tree") if self.show_header else ("tree")
        self.widget = ttk.Treeview(self.root, style="Custom.Treeview", columns=cols, show=show)
        self.widget.tag_configure('active', background='lightblue')
        self.widget.bind('<Button-1>', self.on_item_clicked)
        self.widget.bind("<<TreeviewSelect>>", self.on_row_select)
        self.widget.bind("<space>", self.toggle)
        self.widget.bind("<Return>", self.toggle)
        self.widget.bind('<Up>', self.on_key_pressed)
        self.widget.bind('<Down>', self.on_key_pressed)

        display_columns = cols
        self.widget.column("#0", minwidth=58, width=58, stretch=tk.NO)
        
        for idx, column in enumerate(cols, 1):
            self.widget.column(f"#{idx}", minwidth=50, width=50, stretch=tk.YES)
            self.widget.heading(f"#{idx}", text=column)
        
        self.widget["displaycolumns"]=display_columns
        self.scrollbar = ttk.Scrollbar(self.widget, orient="vertical", command=self.widget.yview)
        self.widget.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        return self.widget
    
    def add_item(self, values:list = [], is_checked:bool = False)->None:
        if self.widget is not None:
            tags = "checked" if is_checked else "unchecked"
            check_mark = CHECKED if is_checked else UNCHECKED
            self.widget.insert("", tk.END, text=check_mark, values=tuple(values), tags=[tags])

    def remove_item(self, id:str)->None:
        if self.get_item(id) is not None:
            self.widget.delete(id)

    def get_items(self)->list[str]:
        if self.widget is not None:
            return self.widget.get_children()
        return []

    def select_all(self, is_selected:bool=True)->None:
        [self.set_row_checked(item, is_selected) for item in self.get_items()]
        
    def clear(self):
        if self.widget is not None:
            self.widget.selection_clear()
            [self.remove_item(item) for item in self.get_items()]

    def get_checked_items(self):
        checked = []
        if self.widget is not None:
            for id in self.get_items():
                item = self.get_item(id)
                if "checked" in item.get("tags", []):
                    checked.append(id)
        return checked
    
    def set_row_checked(self, id:str, is_checked:bool=True)->None:
        if self.get_item(id) is not None:
            if is_checked:
                self.widget.item(id, tags=["checked"], text=CHECKED)
            else:
                self.widget.item(id, tags=["unchecked"], text=UNCHECKED)

    def get_row_text(self, id:str, column:int=0)->str:
        values = self.get_values(id)
        if values is not None and len(values) > column:
            return values[column]
        
    def set_row(self, id:str, values:list)->None:
        if self.get_item(id) is not None:
            self.widget.item(id, values=tuple(values))

    def get_checked_state(self, id:str)->bool:
        item = self.get_item(id)
        if item is not None:
            tags = item.get("tags", [])
            return "checked" in tags
        return False
    
    def toggle(self, event:tk.Event = None)->None:
        item_id = self.get_selected_id()
        if not item_id:
            return
        
        self.is_left_click = False
        is_checked = self.get_checked_state(item_id)
        self.set_row_checked(item_id, False if is_checked else True)
    
    def on_row_select(self, event)->None:
        if self.is_left_click:
            self.toggle()

    def on_key_pressed(self, event)->None:
        self.is_left_click = False

    def on_item_clicked(self, event)->None:
        self.is_left_click = True

    def get_selected_id(self)->str:
        if self.widget is not None:
            return self.widget.focus()
        return ""
    
    def get_item(self, id:str)->dict:
        if self.widget is not None:
            return self.widget.item(id)
        return None
    
    def get_values(self, id:str)->list:
        item = self.get_item(id)
        if item is not None:
            return item.get("values", None)
        return None
