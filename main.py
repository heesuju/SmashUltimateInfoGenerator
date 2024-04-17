import tkinter as tk
from ui.treeview import Menu

root = tk.Tk()
root.minsize(640, 340)
root.geometry("920x540")
root.title("Toml Manager")
menu = Menu(root)

root.mainloop()