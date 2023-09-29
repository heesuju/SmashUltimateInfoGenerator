import tkinter as tk
from tkinter import filedialog
from generator import Generator
from config import Config
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import shutil
import os
import common
import defs

def on_combobox_select(event):
    entry_folder_name.delete(0, tk.END)
    entry_folder_name.insert(0, combobox_cat.get() + "_" + entry_char_names.get().replace(" ", "") + "[" + entry_slots.get().replace(" ", "")  + "]_" + entry_mod_name.get().replace(" ", "") ) 

def on_entry_change(event):
    entry_display_name.delete(0, tk.END)
    entry_display_name.insert(0, entry_char_names.get() + " " + entry_slots.get() + " " + entry_mod_name.get()) 
    entry_folder_name.delete(0, tk.END)
    entry_folder_name.insert(0, combobox_cat.get() + "_" + entry_char_names.get().replace(" ", "") + "[" + entry_slots.get().replace(" ", "")  + "]_" + entry_mod_name.get().replace(" ", "") ) 

def get_working_directory():
    if config.default_dir and common.is_valid_dir(config.default_dir):
        return filedialog.askdirectory(initialdir=config.default_dir)
    else:
        return filedialog.askdirectory()

def group_char_name():
    names = ""
    names_by_group = {}
    for n in range(len(generator.char_names)):
        if generator.group_names[n] in names_by_group.keys():
            arr = names_by_group[generator.group_names[n]]
        else:
            arr = []
        arr.append(generator.char_names[n])
        names_by_group.update({generator.group_names[n]: arr})

    for key, value in names_by_group.items():
        if key:
            names += key + " "
        for n in range(len(value)):
            if n > 0:
                names +=  " & " + value[n]
            else:
                names += value[n]
                
    return names

def change_working_directory():
    working_dir = get_working_directory()
    if not working_dir:
        return
    config.set_default_dir(os.path.dirname(working_dir))
    label_work_dir.config(text=f"{working_dir}")
    dict_info = generator.preview_info_toml(label_work_dir.cget("text"), "", entry_ver.get(), "")
    label_output.config(text="Changed working directory")

    txt_desc.delete(1.0, tk.END)
    txt_desc.insert(tk.END, dict_info["description"])  # Insert the new text

    combobox_cat.set(dict_info["category"])

    entry_char_names.delete(0, tk.END)
    names = group_char_name()           
    entry_char_names.insert(0, names)

    entry_mod_name.delete(0, tk.END)
    entry_mod_name.insert(0, dict_info["mod_name"])

    slots_cleaned = slots_to_string(dict_info["slots"])
    entry_slots.delete(0, tk.END)
    entry_slots.insert(0, slots_cleaned)

    entry_display_name.delete(0, tk.END)
    entry_display_name.insert(0, names + " " + slots_cleaned + " " + dict_info["mod_name"]) 

    entry_folder_name.delete(0, tk.END)
    entry_folder_name.insert(0, dict_info["category"] + "_" + names.replace(" ", "") + "[" + slots_cleaned.replace(" ", "")  + "]_" + dict_info["mod_name"].replace(" ", "") ) 
    
    find_image()

# Create a function to update the info.toml file
def update_info_toml():
    generator.generate_info_toml(entry_display_name.get(), entry_authors.get(), txt_desc.get("1.0", tk.END), entry_ver.get(), combobox_cat.get())
    move_file(label_img_dir.cget("text"), label_work_dir.cget("text"))
    rename_directory()
    label_output.config(text="Applied changes")
    
def update_image():
    image_path =  filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.webp")])
    if not image_path or not os.path.exists(image_path):
        return
    set_image(image_path)
    
def set_image(directory):
    image_path =  directory    
    if not image_path or not os.path.exists(image_path):
        return
    label_img_dir.config(text=f"{image_path}")
    original_image = Image.open(image_path)

    target_width = 400  # Replace with your desired width
    target_height = 225  # Replace with your desired height

    original_width, original_height = original_image.size
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    scaling_factor = min(width_ratio, height_ratio)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)

    resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    img = ImageTk.PhotoImage(resized_image)
    label_img.config(image=img)
    label_img.image = img  # Keep a reference to prevent garbage collection

def move_file(source_file, destination_directory):
    if source_file == "None":
        return
    new_file_name = "preview.webp"  # Replace with the desired new file name
    # Create the full destination path by joining the directory and file name
    destination_path = os.path.join(destination_directory, new_file_name)
    label_img_dir.config(text=f"{destination_path}")
    # Use shutil.move() to move and rename the file
    shutil.move(source_file, destination_path)

def find_image():
    img_list = common.get_children_by_extension(generator.working_dir, ".webp")
    if len(img_list) > 0:
        set_image(generator.working_dir +  "/" + img_list[0])
    else:
        png_list = common.get_children_by_extension(generator.working_dir, ".png")
        if len(png_list) > 0:
            set_image(generator.working_dir + "/" + png_list[0])
        else:
            label_img_dir.config(text="None")
            label_img.config(image=None)
            label_img.image = None  # Keep a reference to prevent garbage collection


def rename_directory():
    if not generator.working_dir or not entry_folder_name.get():
        return
    # Define the old folder name and the new folder name
    old_directory_path = generator.working_dir
    dir_name = common.get_dir_name(old_directory_path)
    new_directory_path = old_directory_path[0:-len(dir_name)]
    new_directory_path += entry_folder_name.get()
    # Check if the old directory exists
    if common.is_valid_dir(old_directory_path):
        try:
            # Rename the directory
            os.rename(old_directory_path, new_directory_path)
            label_work_dir.config(text=f"{new_directory_path}")
            generator.working_dir = new_directory_path
        except OSError as e:
            print(f"Error renaming directory: {e}")
    else:
        print(f"The directory '{old_directory_path}' does not exist.")

def slots_to_string(slots):
    ranges = []
    current_idx = 0
    out_str = ""
    start = slots[0] 
    prev = slots[0]
    if not isinstance(start,int):
        ranges.append("C" + start)
    else:
        ranges.append("C" + f"{start:02}")

        for n in range(1, len(slots)):
            if prev + 1 == slots[n]:
                ranges[current_idx] = "C" + f"{start:02}" + "-" + f"{slots[n]:02}"
            else:
                current_idx+=1
                ranges.append("C" + f"{slots[n]:02}")
                start = slots[n]
            prev = slots[n]

    for item in ranges:
        if not out_str:
            out_str += item
        else:
            out_str += ", " + item
    
    return out_str

# Create the main application window
root = tk.Tk()
root.title("Toml Generator")

# Set the size of the window
root.geometry("840x500")
h_pad = 10
v_pad = 5

btn_change_work_dir = tk.Button(root, text="Select Directory", command=change_working_directory)
btn_change_work_dir.grid(row=0, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

label_work_dir = tk.Label(root, text="None", width=40, anchor="e", justify="right")
label_work_dir.grid(row=0, column=1, padx = h_pad, sticky=tk.W)

label_char_names = tk.Label(root, text="Characters:")
label_char_names.grid(row=1, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

entry_char_names = tk.Entry(root, width=40)
entry_char_names.grid(row=1, column=1, padx = h_pad, sticky=tk.W)
entry_char_names.bind("<KeyRelease>", on_entry_change)

label_slots = tk.Label(root, text="Slots:")
label_slots.grid(row=2, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

entry_slots = tk.Entry(root, width=40)
entry_slots.grid(row=2, column=1, padx = h_pad, sticky=tk.W)
entry_slots.bind("<KeyRelease>", on_entry_change)

label_mod_name = tk.Label(root, text="Mod Title:")
label_mod_name.grid(row=3, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

entry_mod_name = tk.Entry(root, width=40)
entry_mod_name.grid(row=3, column=1, padx = h_pad, sticky=tk.W)
entry_mod_name.bind("<KeyRelease>", on_entry_change)

label_folder_name = tk.Label(root, text="Folder Name")
label_folder_name .grid(row=4, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

entry_folder_name = tk.Entry(root, width=40)
entry_folder_name.grid(row=4, column=1, padx = h_pad, sticky=tk.W)

label_display_name = tk.Label(root, text="Display Name:")
label_display_name.grid(row=5, column=0, sticky=tk.W, padx = 10, pady=v_pad)

entry_display_name = tk.Entry(root, width=40)
entry_display_name.grid(row=5, column=1, padx = h_pad, sticky=tk.W)

label_authors = tk.Label(root, text="Authors:")
label_authors.grid(row=6, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

entry_authors = tk.Entry(root, width=40)
entry_authors.grid(row=6, column=1, padx = h_pad, sticky=tk.W)

label_desc = tk.Label(root, text="Description:")
label_desc.grid(row=7, column=0, padx = h_pad, sticky=tk.W, pady=v_pad)

txt_desc = tk.Text(root, height=10, width=40)
txt_desc.grid(row=7, column=1, padx = h_pad, pady=v_pad, sticky=tk.W)

label_ver = tk.Label(root, text="Version:")
label_ver.grid(row=8, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

entry_ver = tk.Entry(root, width=40)
entry_ver .grid(row=8, column=1, padx = h_pad, sticky=tk.W)
entry_ver.insert(0, "1.0.0")

label_cat = tk.Label(root, text="Category:")
label_cat.grid(row=9, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

combobox_cat = ttk.Combobox(root, values=defs.CATEGORIES)
combobox_cat.grid(row=9, column=1, sticky=tk.W, padx = h_pad, pady=v_pad)
combobox_cat.bind("<<ComboboxSelected>>", on_combobox_select)
combobox_cat.set(defs.CATEGORIES[-1])

btn_apply = tk.Button(root, text="Apply", command=update_info_toml)
btn_apply.grid(row=10, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

label_output = tk.Label(root, width=40, anchor="w")
label_output .grid(row=11, column=0, sticky=tk.W, columnspan=2, padx = h_pad)

label_img = tk.Label(root)
label_img.grid(row=0, column=2, rowspan=11, pady=v_pad, columnspan=2)

btn_select_img = tk.Button(root, text="Select Image", command=update_image)
btn_select_img.grid(row=0, column=2, sticky=tk.W, padx = h_pad, pady=v_pad)

label_img_dir = tk.Label(root, text="None", width=40, anchor="e", justify="right")
label_img_dir.grid(row=0, column=3, padx = h_pad, sticky=tk.W)

global generator
generator = Generator()
config = Config()

# Start the GUI event loop
root.mainloop()