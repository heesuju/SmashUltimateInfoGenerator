import tkinter as tk
from tkinter import PhotoImage
from scanner import Scanner
from mod import Mod

class Menu:
    def __init__(self) -> None:
        self.mods = []
        self.icon_off = None
        self.icon_on = None

    def create_row(self, index:int, mod:Mod):
        frame = tk.Frame(self.frame, cursor="hand2", relief=tk.RAISED, borderwidth=1)
        frame.grid(row=index, column=0, padx=10, pady=5, sticky=tk.NSEW)
        text = tk.Label(frame, text=mod.display_name)
        text.pack(side=tk.LEFT)
        checkbox_label = tk.Label(frame, image=self.icon_off, cursor="hand2")
        checkbox_label.bind("<Button-1>", lambda event: self.toggle_checkbox(event))   
        checkbox_label.pack(side=tk.RIGHT)
        mod.checkbox = checkbox_label

    def load_mods(self):
        scanner = Scanner("C:/Users/mycom/Desktop/Game_utils/smash_mods/moved", self.on_mod_loaded)
        scanner.start()

    def on_mod_loaded(self, mods):
        self.mods=mods
        for i in range(len(self.mods)):
            self.create_row(i, self.mods[i])

    def on_configure(self, event):
        # Update the canvas scroll region to fit the content
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def toggle_checkbox(self, event):
        for mod in self.mods:
            if mod.checkbox == event.widget:
                if mod.selected:
                    mod.selected = False
                else:
                    mod.selected = True
                self.update_checkbox(event, mod.selected)
                break

    def update_checkbox(self, event, checked):
        if checked:
            event.widget.config(image=self.icon_on)
        else:
            event.widget.config(image=self.icon_off)

    def show_menu(self):
        self.icon_off = PhotoImage(file='./icons/off.png')
        self.icon_on = PhotoImage(file='./icons/on.png')

        self.canvas = tk.Canvas(root)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(root, command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Create a frame to hold the list elements
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        # Add buttons and text elements to the list
        self.load_mods()
        # Bind the canvas to the event of resizing
        self.frame.bind("<Configure>", self.on_configure)
    
root = tk.Tk()
root.title("Scrollable List of Buttons and Text")

menu = Menu()
menu.show_menu()

root.mainloop()