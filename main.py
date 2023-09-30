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

def toggle_checkbox(index):
    checkbox_states[index] = not checkbox_states[index]
    update_listbox()

def update_listbox():
    listbox.delete(0, tk.END)
    
    # Add items with checkboxes
    for i, item in enumerate(defs.ELEMENTS):
        checkbox = "[O]" if checkbox_states[i] else "[X]"
        listbox.insert(tk.END, f"{checkbox} {item}")

    set_description()

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

def update_preview():
    config.set_default_dir(os.path.dirname(entry_work_dir.get()))

    dict_info = generator.preview_info_toml(entry_work_dir.get(), "", entry_ver.get(), "")
    label_output.config(text="Changed working directory")
    
    update_description()
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

def change_working_directory():
    working_dir = get_working_directory()
    if not working_dir:
        return
    
    entry_work_dir.delete(0, tk.END)
    entry_work_dir.insert(tk.END, working_dir)
    update_preview()

def on_update_directory(event):
    if entry_work_dir.get() and os.path.exists(entry_work_dir.get()):
        update_preview()

def update_info_toml():
    generator.generate_info_toml(entry_display_name.get(), entry_authors.get(), txt_desc.get("1.0", tk.END), entry_ver.get(), combobox_cat.get())
    move_file(entry_img_dir.get(), entry_work_dir.get())
    rename_directory()
    label_output.config(text="Applied changes")
    
def update_image():
    image_path =  filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.webp")])
    if not image_path or not os.path.exists(image_path):
        return
    set_image(image_path)

def on_update_image(event):
    image_dir = entry_img_dir.get()
    if generator.image_dir == image_dir:
        return
    generator.image_dir = image_dir
    image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
    if image_dir and os.path.exists(image_dir):
        for extension in image_extensions:
            if image_dir.endswith(extension):
                set_image(image_dir)
                break
    
def resize_image(image_path, target_width, target_height):
    img = Image.open(image_path)
    
    # Calculate the aspect ratio
    aspect_ratio = img.width / img.height
    
    # Resize the image to fit the target dimensions while preserving aspect ratio
    if target_width / aspect_ratio <= target_height:
        new_width = target_width
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = target_height
        new_width = int(new_height * aspect_ratio)
    
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

def set_image(directory):
    image_path =  directory    
    if not image_path or not os.path.exists(image_path):
        return
    
    entry_img_dir.delete(0, tk.END)
    entry_img_dir.insert(tk.END, image_path)

    label_width = label_img.winfo_width()
    label_height = label_img.winfo_height()
    resized_image = resize_image(image_path, label_width, label_height)
    image = ImageTk.PhotoImage(resized_image)
    label_img.config(image=image, width=10, height=10)
    label_img.image = image  # Keep a reference to prevent garbage collection

def move_file(source_file, destination_directory):
    if source_file == "None":
        return
    new_file_name = "preview.webp"  # Replace with the desired new file name
    destination_path = os.path.join(destination_directory, new_file_name)
    entry_img_dir.delete(0, tk.END)
    entry_img_dir.insert(tk.END, destination_path)
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
            entry_img_dir.delete(0, tk.END)
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
            entry_work_dir.delete(0, tk.END)
            entry_work_dir.insert(tk.END, new_directory_path)
            generator.working_dir = new_directory_path
            find_image()
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

def set_description():
    description = "Includes:\n"
    txt_desc.delete(1.0, tk.END)

    for n in range(len(checkbox_states)):
        if checkbox_states[n]:
            description += defs.ELEMENTS[n] + "\n"

    if True in checkbox_states:
        txt_desc.insert(tk.END, description)

def update_description():
    listbox.selection_clear(0, tk.END)
    checkbox_states[0] = generator.is_skin
    checkbox_states[1] = generator.is_motion
    checkbox_states[2] = generator.is_effect
    checkbox_states[3] = generator.is_single_effect
    checkbox_states[4] = generator.is_voice
    checkbox_states[5] = generator.is_sfx
    checkbox_states[6] = generator.is_narrator
    checkbox_states[7] = generator.is_custom_name
    checkbox_states[8] = generator.is_ui
    checkbox_states[9] = generator.is_kirby
    update_listbox()

def on_window_resize(event):
    set_image(entry_img_dir.get())

# Create the main application window
root = tk.Tk()
root.title("Smash Ultimate Toml Generator")
for i in range(3):  # Assuming you have three columns
    root.columnconfigure(i, weight=1)
    root.columnconfigure(i, minsize=200)  # Adjust the width as needed
root.rowconfigure(10, weight=1)  # Adjust the width as needed
root.minsize(640, 300)  # Set a minimum width of 300 pixels and a minimum height of 200 pixels

# Set the size of the window
root.geometry("920x500")
root.configure(padx=10, pady=10) 
h_pad = 10
v_pad = 5

# column 0
label_work_dir = tk.Label(root, text="Directory")
label_work_dir.grid(row=0, column=0, sticky=tk.W, pady = (0, v_pad))

frame_work_dir = tk.Frame(root)
frame_work_dir.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=tk.EW, pady = (0, v_pad))

btn_change_work_dir = tk.Button(frame_work_dir, text="Browse", command=change_working_directory)
btn_change_work_dir.pack(side="left", padx = (0, h_pad))

entry_work_dir = tk.Entry(frame_work_dir, width=10)
entry_work_dir.pack(fill=tk.X, expand=True)
entry_work_dir.bind("<KeyRelease>", on_update_directory)

label_authors = tk.Label(root, text="Authors")
label_authors.grid(row=3, column=0, sticky=tk.W)

entry_authors = tk.Entry(root, width=10)
entry_authors.grid(row=4, column=0, sticky=tk.EW, padx = (0, h_pad), pady = (0, v_pad))

frame = tk.Frame(root)
frame.grid(row=5, column=0, rowspan=2, sticky=tk.EW, padx = (0, h_pad), pady = (0, v_pad))
frame.columnconfigure(1, weight=1)

label_ver = tk.Label(frame, text="Version")
label_ver.grid(row=0, column=0, sticky=tk.W)

entry_ver = tk.Entry(frame, width=10)
entry_ver .grid(row=1, column=0, sticky=tk.W, padx=(0,h_pad))
entry_ver.insert(0, "1.0.0")

label_cat = tk.Label(frame, text="Category")
label_cat.grid(row=0, column=1, sticky=tk.W)

combobox_cat = ttk.Combobox(frame, values=defs.CATEGORIES, width=10)
combobox_cat.grid(row=1, column=1, sticky=tk.EW)
combobox_cat.bind("<<ComboboxSelected>>", on_combobox_select)
combobox_cat.set(defs.CATEGORIES[-1])

label_img_dir = tk.Label(root, text="Image", anchor='w')
label_img_dir.grid(row=9, column=0, sticky=tk.W, padx = (0, h_pad))

frame_img = tk.Frame(root, width = 10)
frame_img.grid(row=10, column=0, sticky=tk.NSEW, padx = (0, h_pad), pady = (0, v_pad))

frame_img_dir = tk.Frame(frame_img, width = 10)
frame_img_dir.pack(side=tk.TOP, fill=tk.X, expand=False)

btn_select_img = tk.Button(frame_img_dir, text="Browse", command=update_image)
btn_select_img.pack(side="left", padx = (0, h_pad))

entry_img_dir = tk.Entry(frame_img_dir, width=10, justify='right')
entry_img_dir.pack(fill=tk.X, expand=True)
entry_img_dir.bind("<KeyRelease>", on_update_image)

label_img = tk.Label(frame_img, justify='left', anchor='nw')
label_img.pack(fill=tk.BOTH, expand=True)

# column 1
label_char_names = tk.Label(root, text="Characters")
label_char_names.grid(row=3, column=1, sticky=tk.W)

entry_char_names = tk.Entry(root, width=10)
entry_char_names.grid(row=4, column=1, sticky=tk.EW, padx = (0, h_pad), pady = (0, v_pad))
entry_char_names.bind("<KeyRelease>", on_entry_change)

label_slots = tk.Label(root, text="Slots")
label_slots.grid(row=5, column=1, sticky=tk.W)

entry_slots = tk.Entry(root, width=10)
entry_slots.grid(row=6, column=1, sticky=tk.EW, padx = (0, h_pad), pady = (0, v_pad))
entry_slots.bind("<KeyRelease>", on_entry_change)

label_mod_name = tk.Label(root, text="Mod Title")
label_mod_name.grid(row=7, column=1, sticky=tk.W)

entry_mod_name = tk.Entry(root, width=10)
entry_mod_name.grid(row=8, column=1, sticky=tk.EW, padx = (0, h_pad), pady = (0, v_pad))
entry_mod_name.bind("<KeyRelease>", on_entry_change)

label_list = tk.Label(root, text="Includes")
label_list.grid(row=9, column=1, sticky=tk.W)

listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=10)
listbox.grid(row=10, column=1, sticky=tk.NSEW, padx = (0, h_pad), pady = (0, v_pad))

for item in defs.ELEMENTS:
    listbox.insert(tk.END, item)

# column 2
label_folder_name = tk.Label(root, text="Folder Name")
label_folder_name .grid(row=3, column=2, sticky=tk.W)

entry_folder_name = tk.Entry(root)
entry_folder_name.grid(row=4, column=2, sticky=tk.EW, pady = (0, v_pad))

label_display_name = tk.Label(root, text="Display Name")
label_display_name.grid(row=5, column=2, sticky=tk.W)

entry_display_name = tk.Entry(root, width=10)
entry_display_name.grid(row=6, column=2, sticky=tk.EW, pady = (0, v_pad))

label_desc = tk.Label(root, text="Description")
label_desc.grid(row=9, column=2, sticky=tk.W)

txt_desc = tk.Text(root, height=10, width=10)
txt_desc.grid(row=10, column=2, sticky=tk.NSEW, pady = (0, v_pad))

btn_apply = tk.Button(root, text="Apply", command=update_info_toml)
btn_apply.grid(row=11, column=2, sticky=tk.E)

label_output = tk.Label(root)
label_output .grid(row=11, column=0, sticky=tk.W, columnspan=2)

global checkbox_states
checkbox_states = [False] * len(defs.ELEMENTS)
update_listbox()
listbox.bind("<Button-1>", lambda event: toggle_checkbox(listbox.nearest(event.y)))

global generator
generator = Generator()
config = Config()

root.bind("<Configure>", on_window_resize)

# Start the GUI event loop
root.mainloop()