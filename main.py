import tkinter as tk
from tkinter import filedialog
from generator import Generator
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import shutil
import os
import common
import defs

def on_combobox_select(event):
    selected_option = combobox.get()
def on_entry_change(event):
    display_text.delete(0, tk.END)
    display_text.insert(0, char_name_text.get() + " " + slot_text.get() + " " + mod_name_text.get()) 

# Create a function to get the directory using a file dialog
def get_working_directory():
    return filedialog.askdirectory()

def change_working_directory():
    working_dir = get_working_directory()
    if not working_dir:
        return
    directory_label.config(text=f"{working_dir}")
    dict_info = generator.preview_info_toml(directory_label.cget("text"), "", version_text.get(), "")
    
    result_text.config(text="Changed working directory")

    description_text.delete(1.0, tk.END)
    description_text.insert(tk.END, dict_info["description"])  # Insert the new text
    combobox.set(dict_info["category"])
    char_name_text.delete(0, tk.END)
    names = ""

    if len(dict_info["character_names"]) > 1:
        name_parts = common.split_into_arr(dict_info["character_names"][0], " ")
        head = name_parts[0]
        names = dict_info["character_names"][0].replace(" ", "")
        max = len(dict_info["character_names"])
        num = 1
        for n in range(1, max):
            if head in dict_info["character_names"][n]:
                next = dict_info["character_names"][n].replace(" ", "")
                names += " & " + next
                names = names.replace(head, "")
                num += 1
        if num > 1:
            names = head + " " + names 
    elif len(dict_info["character_names"]) == 1:
        names = dict_info["character_names"][0]
    char_name_text.insert(0, names)

    mod_name_text.delete(0, tk.END)
    mod_name_text.insert(0, dict_info["mod_name"])

    slots_cleaned = slots_to_string(dict_info["slots"])
    slot_text.delete(0, tk.END)
    slot_text.insert(0, slots_cleaned)
    display_text.delete(0, tk.END)
    display_text.insert(0, names + " " + slots_cleaned + " " + dict_info["mod_name"]) 

# Create a function to update the info.toml file
def update_info_toml():
    generator.generate_info_toml(display_text.get(), authors_entry.get(), description_text.get("1.0", tk.END), version_text.get(), combobox.get())
    move_file(img_dir_label.cget("text"), directory_label.cget("text"))
    result_text.config(text="Generated info.toml in mod folder")
    
def update_image():
    image_path =  filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.webp")])
    if not image_path:
        return
    img_dir_label.config(text=f"{image_path}")
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
    label.config(image=img)
    label.image = img  # Keep a reference to prevent garbage collection

def move_file(source_file, destination_directory):
    if source_file == "None":
        return
    new_file_name = "preview.webp"  # Replace with the desired new file name
    # Create the full destination path by joining the directory and file name
    destination_path = os.path.join(destination_directory, new_file_name)

    # Use shutil.move() to move and rename the file
    shutil.move(source_file, destination_path)

def rename_folder(directory):
    # Define the old folder name and the new folder name
    old_directory_path = directory
    dir_name = common.get_dir_name(directory)
    new_directory_path = directory[0:-len(dir_name)]
    new_directory_path.join("test")
    # Check if the old directory exists
    if common.is_valid_dir(old_directory_path):
        try:
            # Rename the directory
            os.rename(old_directory_path, new_directory_path)
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

# Create a button to trigger the directory selection and info.toml update
select_directory_button = tk.Button(root, text="Select Directory", command=change_working_directory)
select_directory_button.grid(row=0, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

directory_label = tk.Label(root, text="None", width=40, anchor="e", justify="right")
directory_label.grid(row=0, column=1, padx = h_pad, sticky=tk.W)

char_name_label = tk.Label(root, text="Characters:")
char_name_label.grid(row=1, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

char_name_text = tk.Entry(root, width=40)
char_name_text.grid(row=1, column=1, padx = h_pad, sticky=tk.W)
char_name_text.bind("<KeyRelease>", on_entry_change)

slot_label = tk.Label(root, text="Slots:")
slot_label.grid(row=2, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

slot_text = tk.Entry(root, width=40)
slot_text.grid(row=2, column=1, padx = h_pad, sticky=tk.W)
slot_text.bind("<KeyRelease>", on_entry_change)

mod_name_label = tk.Label(root, text="Mod Title:")
mod_name_label.grid(row=3, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

mod_name_text = tk.Entry(root, width=40)
mod_name_text.grid(row=3, column=1, padx = h_pad, sticky=tk.W)
mod_name_text.bind("<KeyRelease>", on_entry_change)

display_label = tk.Label(root, text="Display Name:")
display_label.grid(row=4, column=0, sticky=tk.W, padx = 10, pady=v_pad)

# Create a Text widget for the multiline description
display_text = tk.Entry(root, width=40)
display_text.grid(row=4, column=1, padx = h_pad, sticky=tk.W)

# Create a label for the authors input
authors_label = tk.Label(root, text="Authors:")
authors_label.grid(row=5, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

# Create an Entry widget for the single-line authors input
authors_entry = tk.Entry(root, width=40)
authors_entry.grid(row=5, column=1, padx = h_pad, sticky=tk.W)

# Create a label for the description input
description_label = tk.Label(root, text="Description:")
description_label.grid(row=6, column=0, padx = h_pad, sticky=tk.W, pady=v_pad)

# Create a Text widget for the multiline description
description_text = tk.Text(root, height=10, width=40)
description_text.grid(row=6, column=1, padx = h_pad, pady=v_pad, sticky=tk.W)

# Create a label for the version input
version_label = tk.Label(root, text="Version:")
version_label.grid(row=7, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

version_text = tk.Entry(root, width=40)
version_text .grid(row=7, column=1, padx = h_pad, sticky=tk.W)
version_text.insert(0, "1.0.0")

# Create a label for the version input
category_label = tk.Label(root, text="Category:")
category_label.grid(row=8, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

# Create a ComboBox with string options
combobox = ttk.Combobox(root, values=defs.CATEGORIES)
combobox.grid(row=8, column=1, sticky=tk.W, padx = h_pad, pady=v_pad)
combobox.bind("<<ComboboxSelected>>", on_combobox_select)
combobox.set(defs.CATEGORIES[-1])

generate_button = tk.Button(root, text="Generate", command=update_info_toml)
generate_button.grid(row=9, column=0, sticky=tk.W, padx = h_pad, pady=v_pad)

result_text = tk.Label(root, width=40, anchor="w")
result_text .grid(row=10, column=0, sticky=tk.W, columnspan=2, padx = h_pad)

# Create a Label widget to display the image
label = tk.Label(root)
label.grid(row=0, column=2, rowspan=11, pady=v_pad, columnspan=2)

img_button = tk.Button(root, text="Select Image", command=update_image)
img_button.grid(row=0, column=2, sticky=tk.W, padx = h_pad, pady=v_pad)

img_dir_label = tk.Label(root, text="None", width=40, anchor="e", justify="right")
img_dir_label.grid(row=0, column=3, padx = h_pad, sticky=tk.W)

global generator
generator = Generator()

# Start the GUI event loop
root.mainloop()