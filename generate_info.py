import os
import tomli_w as tomli
import tkinter as tk
from tkinter import filedialog
import subprocess
import re

# Create a function to get the directory using a file dialog
def get_working_directory():
    return filedialog.askdirectory()

def change_working_directory():
    working_dir = get_working_directory()
    directory_label.config(text=f"{working_dir}")
    
def get_dir_name(directory):
    return os.path.basename(directory)
    
# Split the folder name into array
def split_into_arr(folder_name, split_char = '_'):
    return folder_name.split(split_char)
    
def search_dir_for_keyword(directory, keyword):
    for root, dirs, files in os.walk(directory):
        if keyword in dirs:
            return True
    return False
    
def search_files_for_pattern(file, pattern):
    if re.search(pattern, file):
        return True
    return False

# Create a function to update the info.toml file
def update_info_toml():
    display_name = ""
    category = ""
    working_dir = directory_label.cget("text")
    folder_name_parts = split_into_arr(get_dir_name(working_dir))
    print(working_dir)
    if len(folder_name_parts) > 2:
        character_name = folder_name_parts[1]
        character_name = character_name.replace("[", " ").replace("]", " ")
        display_name = display_name + character_name + folder_name_parts[-1]
        category = folder_name_parts[0]
    
    description = "Includes:\n"

    if os.path.exists(working_dir + "/fighter") and os.path.isdir(working_dir + "/fighter"):
        if search_dir_for_keyword(working_dir + "/fighter", "model"):
            description = description + "Skin\n"
            
        if search_dir_for_keyword(working_dir + "/fighter", "motion"):
            description = description + "Motion\n"
        
        if search_dir_for_keyword(working_dir + "/fighter", "kirby"):
            description = description + "Kirby\n"
        
        category = "Fighter"
        
    if os.path.exists(working_dir + "/effect") and os.path.isdir(working_dir + "/effect"):
        for root, dirs, files in os.walk(working_dir + "/effect"):
            for file in files:
                if file.endswith('.eff'):
                    if search_files_for_pattern(file, r"c\d+"):
                        description = description + "Single Effect\n"
                    else:
                        description = description + "Effects\n"
        
    # Check if the "ui" directory exists
    if os.path.exists(working_dir + "/sound") and os.path.isdir(working_dir + "/sound"):
        if search_dir_for_keyword(working_dir + "/sound", "fighter_voice"):
            description = description + "Voice\n"
        
        if search_dir_for_keyword(working_dir + "/sound", "narration"):
            description = description + "Narrator Voice\n"
        
    # Check if the "ui" directory exists
    if os.path.exists(working_dir + "/ui") and os.path.isdir(working_dir + "/ui"):
        if search_dir_for_keyword(working_dir + "/ui", "message"):
            description = description + "Custom Name\n"
        
        if search_dir_for_keyword(working_dir + "/ui", "replace"):
            description = description + "UI\n"
            
    # Get the description from the multiline Text widget
    description = description + description_text.get("1.0", tk.END)
    version = version_text.get()
    # Get the authors from the single-line Entry widget
    authors = authors_entry.get()

    # Rest of your script

    # Create and write to the info.toml file
    with open(working_dir + "\info.toml", "wb") as toml_file:
        tomli.dump({
            "display_name": display_name, 
            "authors": authors,
            "description": description,
            "version": version,
            "category": category
        }, toml_file)

# Create the main application window
root = tk.Tk()
root.title("Info Generator")

# Set the size of the window
root.geometry("400x300")

# Create a button to trigger the directory selection and info.toml update
select_directory_button = tk.Button(root, text="Select Directory", command=change_working_directory)
select_directory_button.grid(row=1, column=0, sticky=tk.W)

directory_label = tk.Label(root, text="None", width=40)
directory_label.grid(row=1, column=1, sticky=tk.W)

# Create a label for the description input
description_label = tk.Label(root, text="Description:")
description_label.grid(row=2, column=0, sticky=tk.W)

# Create a Text widget for the multiline description
description_text = tk.Text(root, height=10, width=40)
description_text.grid(row=2, column=1, sticky=tk.W)

# Create a label for the authors input
authors_label = tk.Label(root, text="Authors:")
authors_label.grid(row=3, column=0, sticky=tk.W)

# Create an Entry widget for the single-line authors input
authors_entry = tk.Entry(root, width=40)
authors_entry.grid(row=3, column=1, sticky=tk.W)

# Create a label for the version input
version_label = tk.Label(root, text="Version:")
version_label.grid(row=4, column=0, sticky=tk.W)

version_text = tk.Entry(root, width=40)
version_text .grid(row=4, column=1, sticky=tk.W)
version_text.insert(0, "1.0.0")

generate_button = tk.Button(root, text="Generate", command=update_info_toml)
generate_button.grid(row=5, column=0, sticky=tk.W)

# Start the GUI event loop
root.mainloop()