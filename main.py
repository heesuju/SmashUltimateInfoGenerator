import tkinter as tk
from tkinter import filedialog
from generator import Generator
from tkinter import ttk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import shutil
import os

def on_combobox_select(event):
    selected_option = combobox.get()
    
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
    display_text.delete(0, tk.END)
    display_text.insert(0, dict_info["display_name"])  # Insert the new text
    description_text.delete(1.0, tk.END)
    description_text.insert(tk.END, dict_info["description"])  # Insert the new text
    combobox.set(dict_info["category"])

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

# Create the main application window
root = tk.Tk()
root.title("Toml Generator")

# Set the size of the window
root.geometry("840x440")

# Create a button to trigger the directory selection and info.toml update
select_directory_button = tk.Button(root, text="Select Directory", command=change_working_directory)
select_directory_button.grid(row=0, column=0, sticky=tk.W, padx = 10, pady=10)

directory_label = tk.Label(root, text="None", width=40, anchor="e", justify="right")
directory_label.grid(row=0, column=1, padx = 10, sticky=tk.W)

display_label = tk.Label(root, text="Display Name:")
display_label.grid(row=1, column=0, sticky=tk.W, padx = 10, pady=10)

# Create a Text widget for the multiline description
display_text = tk.Entry(root, width=40)
display_text.grid(row=1, column=1, padx = 10, sticky=tk.W)

# Create a label for the authors input
authors_label = tk.Label(root, text="Authors:")
authors_label.grid(row=2, column=0, sticky=tk.W, padx = 10, pady=10)

# Create an Entry widget for the single-line authors input
authors_entry = tk.Entry(root, width=40)
authors_entry.grid(row=2, column=1, padx = 10, sticky=tk.W)

# Create a label for the description input
description_label = tk.Label(root, text="Description:")
description_label.grid(row=3, column=0, padx = 10, sticky=tk.W, pady=10)

# Create a Text widget for the multiline description
description_text = tk.Text(root, height=10, width=40)
description_text.grid(row=3, column=1, padx = 10, sticky=tk.W)

# Create a label for the version input
version_label = tk.Label(root, text="Version:")
version_label.grid(row=4, column=0, sticky=tk.W, padx = 10, pady=10)

version_text = tk.Entry(root, width=40)
version_text .grid(row=4, column=1, padx = 10, sticky=tk.W)
version_text.insert(0, "1.0.0")

# Create a label for the version input
category_label = tk.Label(root, text="Category:")
category_label.grid(row=5, column=0, sticky=tk.W, padx = 10, pady=10)

# Create a ComboBox with string options
options = ["Fighter", "Stage", "Effects", "UI", "Param", "Audio", "Misc"]
combobox = ttk.Combobox(root, values=options)
combobox.grid(row=5, column=1, sticky=tk.W, padx = 10, pady=10)
combobox.bind("<<ComboboxSelected>>", on_combobox_select)
combobox.set("Misc")

generate_button = tk.Button(root, text="Generate", command=update_info_toml)
generate_button.grid(row=6, column=0, sticky=tk.W, padx = 10, pady=10)

result_text = tk.Label(root, width=40, anchor="w")
result_text .grid(row=7, column=0, sticky=tk.W, columnspan=2, padx = 10)

# Create a Label widget to display the image
label = tk.Label(root)
label.grid(row=0, column=2, rowspan=8, pady=10, columnspan=2)

img_button = tk.Button(root, text="Select Image", command=update_image)
img_button.grid(row=0, column=2, sticky=tk.W, padx = 10, pady=10)

img_dir_label = tk.Label(root, text="None", width=40, anchor="e", justify="right")
img_dir_label.grid(row=0, column=3, padx = 10, sticky=tk.W)

global generator
generator = Generator()

# Start the GUI event loop
root.mainloop()