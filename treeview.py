import tkinter as tk
from ttkwidgets import CheckboxTreeview 
from tkinter import ttk
from scanner import Scanner
import math
import common
from PIL import Image, ImageTk
import tkinter.font as font

class Menu:    
    def __init__(self) -> None:
        self.mods = []
        self.filtered_mods = []
        self.cur_page = 1
        self.total_pages = 1
        self.page_size = 10
        self.show()
        self.scan()
    
    def reset(self):
        self.treeview.selection_clear()
        self.treeview.delete(*self.treeview.get_children())

    def populate(self, mods):
        self.total_pages = math.ceil(len(mods)/self.page_size)
        print(f"found {len(mods)} items")
        
        self.show_paging()
        start = (self.cur_page-1) * self.page_size
        end = common.clamp(self.cur_page * self.page_size, start, len(mods))
        for n in range(start,end):
            self.treeview.insert("", tk.END, values=(mods[n].mod_name, mods[n].category, mods[n].version, mods[n].authors, mods[n].characters, mods[n].slots, mods[n].info_toml, mods[n].path))

    def search(self, event):
        self.reset()
        self.cur_page = 1
        mod_name = self.entry_mod_name.get()
        author = self.entry_author.get()
        category = ""
        character = self.entry_character.get()
        self.filtered_mods = []
        for mod in self.mods:
            if mod_name not in mod.mod_name: continue
            if author not in mod.authors: continue
            if character not in mod.characters: continue
            
            self.filtered_mods.append(mod)
            
        self.populate(self.filtered_mods)

    def on_scanned(self, mods):
        self.mods = mods
        self.filtered_mods = mods
        self.populate(self.mods)
    
    def on_item_selected(self, event):
        selected_item = self.treeview.focus()
        item = self.treeview.item(selected_item)

    def on_double_clicked(self, event):
        selected_item = self.treeview.focus()
        item = self.treeview.item(selected_item)
        print(item)

    def on_space_pressed(self, event):
        selected_item = self.treeview.focus()
        item = self.treeview.item(selected_item)
        if item["tags"][0] == "checked":
            self.treeview.change_state(item=selected_item, state="unchecked")
        else:
            self.treeview.change_state(item=selected_item, state="checked")

    def scan(self):
        scan_thread = Scanner("C:/Users/mycom/Desktop/Game_utils/smash_mods/moved", self.on_scanned)
        scan_thread.start()

    def add_filter_item(self, row, col, name):
        label = ttk.Label(self.category_frame, text=name)
        label.grid(row=row, column=col, sticky=tk.W, padx=5)
        entry = tk.Entry(self.category_frame)
        entry.grid(row=row, column=col+1)
        entry.bind("<Return>", self.search)
        return entry
    
    def change_page(self, number):
        self.cur_page = number
        self.reset()
        self.populate(self.filtered_mods)

    def next_page(self):
        self.cur_page = common.clamp(self.cur_page+1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def prev_page(self):
        self.cur_page = common.clamp(self.cur_page-1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def show_paging(self):
        icon_left = ImageTk.PhotoImage(file='./icons/left.png')
        icon_right = ImageTk.PhotoImage(file='./icons/right.png')
        for child in self.frame_paging.winfo_children():
            child.destroy()

        self.btn_left = tk.Button(self.frame_paging, image=icon_left, relief=tk.FLAT, cursor='hand2', command=self.prev_page)
        self.btn_left.image = icon_left
        self.btn_left.grid(row=0, column=0)
        
        prev = 0
        for index, n in enumerate(common.get_pages(self.cur_page, self.total_pages)):
            if index > 0 and prev+1 != n:
                label = tk.Label(self.frame_paging, text="...", width=2)
                label.grid(row=0, column=n-1)    
            
            btn = tk.Button(self.frame_paging, text=n, relief=tk.FLAT, cursor='hand2', command=lambda number=n: self.change_page(number), width=2)
            if self.cur_page == n:
                btn["font"]= font.Font(weight="bold")
                btn["fg"]= "#6563FF"
            btn.grid(row=0, column=n)
            prev = n

        self.btn_right = tk.Button(self.frame_paging, image = icon_right, relief=tk.FLAT, cursor='hand2', command=self.next_page)
        self.btn_right.image = icon_right
        self.btn_right.grid(row=0, column=self.total_pages + 1)

    def show(self):
        self.category_frame = ttk.LabelFrame(root, text="Filter")
        self.category_frame.pack(padx=10, pady=10, fill="x")
        
        self.entry_mod_name = self.add_filter_item(0, 0, "Mod Name")
        self.entry_author = self.add_filter_item(1, 0, "Author")
        self.entry_character = self.add_filter_item(2, 0, "Character")
        
        self.categories = ["Mod Name", "Category", "Version", "Authors", "Characters", "Slots", "Info.toml", "Dir"]

        self.treeview = CheckboxTreeview(root, columns=self.categories, show=("headings", "tree"))
        
        style = ttk.Style(root)
        style.map("Checkbox.Treeview", background=[("disabled", "#E6E6E6"), ("selected", "#E6E6E6")])
        style.configure("Checkbox.Treeview", rowheight=26)
        display_columns = []
        for col, category in enumerate(self.categories):
            if col < len(self.categories)-1:
                self.treeview.column(category, width=100)
                display_columns.append(category)
            self.treeview.heading(category, text=category)
        self.treeview["displaycolumns"]=display_columns
        self.treeview.pack(padx=10, pady=10, fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.treeview, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.bind('<<TreeviewSelect>>', self.on_item_selected)
        self.treeview.bind("<Double-1>", self.on_double_clicked)
        self.treeview.bind("<space>", self.on_space_pressed)
        self.scrollbar.pack(side="right", fill="y")
        self.frame_paging = tk.Frame(root)
        self.frame_paging.pack()


root = tk.Tk()
root.minsize(640, 340)
root.title("Toml Manager")
menu = Menu()

root.mainloop()