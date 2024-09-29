import tkinter as tk
import defs
from tkinter import ttk
from utils.files import get_dir_name

class Comparison:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.new_window = None

    def open(self, root, loaded_data, generated_data):
        if self.new_window is not None:
            self.new_window.destroy()
            
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Comparison")
        for i in range(2):
            self.new_window.columnconfigure(i, weight=1)
            self.new_window.columnconfigure(i, minsize=200)
        self.new_window.rowconfigure(3, weight=1)
        self.new_window.minsize(640, 340)

        # Set the size of the window
        self.new_window.geometry("620x300")
        self.new_window.configure(padx=10, pady=10) 

        #-------------------------------old-------------------------------
        l_prev = tk.Label(self.new_window, text="Old Data", font='Helvetica 10 bold')
        l_prev.grid(row=2, column=0, sticky=tk.W)

        f_prev = tk.Frame(self.new_window)
        f_prev.grid(row=3, column=0, sticky=tk.NSEW, padx=(0,defs.PAD_H))
        f_prev.columnconfigure(0, weight=1)
        f_prev.rowconfigure(6, weight=1)

        l_folder_name_prev = tk.Label(f_prev, text="Folder Name")
        l_folder_name_prev.grid(row=0, column=0, sticky=tk.W)

        e_folder_name_prev = tk.Entry(f_prev, width=10)
        e_folder_name_prev.grid(row=1, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))
        e_folder_name_prev.insert(0,get_dir_name(generated_data['working_dir']))

        l_display_name_prev = tk.Label(f_prev, text="Display Name")
        l_display_name_prev.grid(row=2, column=0, sticky=tk.W)

        e_display_name_prev = tk.Entry(f_prev, width=10)
        e_display_name_prev.grid(row=3, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))
        e_display_name_prev.insert(0, loaded_data.display_name)

        l_authors_prev = tk.Label(f_prev, text="Authors")
        l_authors_prev.grid(row=4, column=0, sticky=tk.W)

        e_authors_prev = tk.Entry(f_prev, width=10)
        e_authors_prev.grid(row=5, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))
        e_authors_prev.insert(0, loaded_data.authors)

        f_group_prev = tk.Frame(f_prev)
        f_group_prev.grid(row=6, column=0, sticky=tk.NSEW, pady = (0, defs.PAD_V))
        f_group_prev.columnconfigure(0, weight=3)
        f_group_prev.columnconfigure(1, weight=7)
        f_group_prev.rowconfigure(3, weight=1)

        l_ver_prev = tk.Label(f_group_prev, text="Version")
        l_ver_prev.grid(row=0, column=0, sticky=tk.W)

        e_ver_new = tk.Entry(f_group_prev, width=10)
        e_ver_new.grid(row=1, column=0, sticky=tk.EW, padx=(0,defs.PAD_H), pady = (0, defs.PAD_V))
        e_ver_new.insert(0, loaded_data.version)

        l_cat_prev = tk.Label(f_group_prev, text="Category")
        l_cat_prev.grid(row=0, column=1, sticky=tk.W)

        e_cat_prev_v = tk.Entry(f_group_prev, width=10)
        e_cat_prev_v.grid(row=1, column=1, sticky=tk.EW)
        e_cat_prev_v.insert(0, loaded_data.category)

        l_desc_prev = tk.Label(f_group_prev, text="Description")
        l_desc_prev.grid(row=2, column=0, sticky=tk.W)

        t_desc_prev_v = tk.Text(f_group_prev, height=10, width=10)
        t_desc_prev_v.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)
        t_desc_prev_v.insert(tk.END, loaded_data.description)

        #-------------------------------new-------------------------------

        f_new_label = tk.Frame(self.new_window)
        f_new_label.grid(row=2, column=1, sticky=tk.EW)

        l_new = tk.Label(f_new_label, text="New Data", font='Helvetica 10 bold')
        l_new.pack(side="left")

        f_new = tk.Frame(self.new_window)
        f_new.grid(row=3, column=1, sticky=tk.NSEW, padx = (0, 0)) 
        f_new.columnconfigure(0, weight=1)
        f_new.rowconfigure(6, weight=1)

        l_folder_name_new = tk.Label(f_new, text="Folder Name")
        l_folder_name_new.grid(row=0, column=0, sticky=tk.W)
        
        e_folder_name_new = tk.Entry(f_new, width=10)
        e_folder_name_new.grid(row=1, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))
        e_folder_name_new.insert(0,generated_data['folder_name'])

        l_display_name_new = tk.Label(f_new, text="Display Name")
        l_display_name_new.grid(row=2, column=0, sticky=tk.W)

        e_display_name_new = tk.Entry(f_new, width=10)
        e_display_name_new.grid(row=3, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))
        e_display_name_new.insert(0, generated_data['display_name'])

        l_authors_new = tk.Label(f_new, text="Authors")
        l_authors_new.grid(row=4, column=0, sticky=tk.W)

        e_authors_new = tk.Entry(f_new, width=10)
        e_authors_new.grid(row=5, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))
        e_authors_new.insert(0, generated_data['authors'])

        f_group_new = tk.Frame(f_new)
        f_group_new.grid(row=6, column=0, sticky=tk.NSEW, pady = (0, defs.PAD_V))
        f_group_new.columnconfigure(0, weight=3)
        f_group_new.columnconfigure(1, weight=7)
        f_group_new.rowconfigure(3, weight=1)

        l_ver_new = tk.Label(f_group_new, text="Version")
        l_ver_new.grid(row=0, column=0, sticky=tk.W)

        e_ver_new = tk.Entry(f_group_new, width=10)
        e_ver_new.grid(row=1, column=0, sticky=tk.EW, padx=(0,defs.PAD_H), pady = (0, defs.PAD_V))
        e_ver_new.insert(0, generated_data['version'])

        l_cat_new = tk.Label(f_group_new, text="Category")
        l_cat_new.grid(row=0, column=1, sticky=tk.W)

        c_cat_new = ttk.Combobox(f_group_new, values=defs.CATEGORIES, width=10)
        c_cat_new.grid(row=1, column=1, sticky=tk.EW)
        c_cat_new.set(generated_data['category'])

        l_desc_new = tk.Label(f_group_new, text="Description")
        l_desc_new.grid(row=2, column=0, sticky=tk.W)

        t_desc_new_v = tk.Text(f_group_new, height=10, width=10)
        t_desc_new_v.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, padx = (0, defs.PAD_H))
        t_desc_new_v.insert(tk.END, generated_data['description'])