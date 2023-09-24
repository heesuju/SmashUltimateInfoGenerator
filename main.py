import tkinter as tk
from tkinter import filedialog
from generator import Generator

# Create a function to get the directory using a file dialog
def get_working_directory():
    return filedialog.askdirectory()

def change_working_directory():
    working_dir = get_working_directory()
    directory_label.config(text=f"{working_dir}")

# Create a function to update the info.toml file
def update_info_toml():
    generator = Generator(directory_label.cget("text"), authors_entry.get(), version_text.get(), description_text.get("1.0", tk.END))
    generator.generate_info_toml()
    
# Create the main application window
root = tk.Tk()
root.title("Toml Gen for Smash Ultimate")

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