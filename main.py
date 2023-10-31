import tkinter as tk
from tkinter import filedialog
from generator import Generator
from config import Config
from tkinter import ttk
from PIL import Image, ImageTk
import shutil
import os
import common
import defs
from static_scraper import Extractor
from dynamic_scraper import Selenium
from downloader import Downloader
from loader import Loader

def on_img_download():
    label_output.config(text="Downloaded image")
    find_image()

def download_img():
    downloader_thread = Downloader(generator.img_url, generator.working_dir, on_img_download)
    downloader_thread.start()
    
def on_bs4_result(mod_title, authors):
    if mod_title:
        generator.mod_title_web = mod_title
        entry_mod_name.delete(0, tk.END)
        entry_mod_name.insert(0, common.trim_mod_name(generator.mod_title_web, generator.ignore_names))
    elif generator.mod_name:
        entry_mod_name.delete(0, tk.END)
        entry_mod_name.insert(0, generator.mod_name)
    
    if authors:
        entry_authors.delete(0, tk.END)
        entry_authors.insert(0, authors)

    set_display_name(entry_char_names.get(), entry_slots.get(), entry_mod_name.get(), combobox_cat.get())
    set_folder_name(entry_char_names.get().replace(" ", ""), entry_slots.get().replace(" ", ""), entry_mod_name.get().replace(" ", ""), combobox_cat.get())

def on_selenium_result(version, img_url):
    label_output.config(text="Fetched elements")
    entry_ver.delete(0, tk.END)
    entry_ver.insert(0, common.format_version(version))
    generator.img_url = img_url
    if generator.img_url and generator.working_dir:
        btn_download_img.config(state="normal")
    else:
        btn_download_img.config(state="disabled")

def on_url_change(event):
    if generator.url == entry_url.get() or not common.is_valid_url(entry_url.get()):
        return
    
    label_output.config(text="Fetching elements...")
    btn_download_img.config(state="disabled")
    generator.url = entry_url.get()
    bs4_thread = Extractor(entry_url.get(), on_bs4_result)
    selenium_thread = Selenium(entry_url.get(), on_selenium_result)
    
    bs4_thread.start()
    selenium_thread.start()

def on_combobox_select(event):
    entry_folder_name.delete(0, tk.END)
    entry_folder_name.insert(0, combobox_cat.get() + "_" + entry_char_names.get().replace(" ", "") + "[" + entry_slots.get().replace(" ", "")  + "]_" + entry_mod_name.get().replace(" ", "") ) 

def on_entry_change(event):
    set_display_name(entry_char_names.get(), entry_slots.get(), entry_mod_name.get(), combobox_cat.get())
    set_folder_name(entry_char_names.get().replace(" ", ""), entry_slots.get().replace(" ", ""), entry_mod_name.get().replace(" ", ""), combobox_cat.get())

def set_display_name(character_names, slots, mod_name, category):
    entry_display_name.delete(0, tk.END)
    display_name = config.display_name_format
    display_name = display_name.replace("{characters}", character_names)
    display_name = display_name.replace("{slots}", slots)
    display_name = display_name.replace("{mod}", mod_name)
    display_name = display_name.replace("{category}", category)
    entry_display_name.insert(0, display_name) 

def set_folder_name(character_names, slots, mod_name, category):
    entry_folder_name.delete(0, tk.END)
    folder_name = config.folder_name_format
    folder_name = folder_name.replace("{characters}", character_names)
    folder_name = folder_name.replace("{slots}", slots)
    folder_name = folder_name.replace("{mod}", mod_name)
    folder_name = folder_name.replace("{category}", category)
    entry_folder_name.insert(0, folder_name)

def toggle_checkbox(index):
    checkbox_states[index] = not checkbox_states[index]
    update_listbox()

def update_listbox():
    listbox.delete(0, tk.END)

    # Add items with checkboxes
    for i, item in enumerate(defs.ELEMENTS + config.additional_elements):
        if i >= len(checkbox_states):
            checkbox_states.append(False)
        checkbox = "[O]" if checkbox_states[i] else "[X]"
        listbox.insert(tk.END, f"{checkbox} {item}")

    set_description()

def get_working_directory():
    if config.default_dir and common.is_valid_dir(config.default_dir):
        return filedialog.askdirectory(initialdir=config.default_dir)
    else:
        return filedialog.askdirectory()

def update_preview():
    entry_url.delete(0, tk.END)
    generator.url = entry_url.get()
    config.load_config()
    config.set_default_dir(os.path.dirname(entry_work_dir.get()))

    dict_info = generator.preview_info_toml(entry_work_dir.get(), "", entry_ver.get(), "")
    label_output.config(text="Changed working directory")
    
    update_description()
    combobox_cat.set(dict_info["category"])

    entry_char_names.delete(0, tk.END)
    names = common.group_char_name(generator.char_names, generator.group_names)           
    entry_char_names.insert(0, names)

    slots_cleaned = common.slots_to_string(dict_info["slots"])
    entry_slots.delete(0, tk.END)
    entry_slots.insert(0, slots_cleaned)

    mod_name = ""
    if not entry_url.get():
        dir_name = common.get_dir_name(generator.working_dir)
        title = common.get_mod_title(dir_name, generator.char_names, config.folder_name_format)
        capitalized = common.add_spaces_to_camel_case(title)
        mod_name = capitalized
        generator.mod_name = mod_name

        if loader.load_toml(entry_work_dir.get()):
            entry_authors.delete(0, tk.END)
            entry_authors.insert(0, loader.authors)
            entry_ver.delete(0, tk.END)
            entry_ver.insert(0, loader.version)
            combobox_cat.set(loader.category)
    else:
        mod_name = generator.mod_title_web
    
    entry_mod_name.delete(0, tk.END)
    entry_mod_name.insert(0, mod_name)

    set_display_name(names, slots_cleaned, mod_name, dict_info["category"])
    set_folder_name(names.replace(" ", "") , slots_cleaned.replace(" ", ""), mod_name.replace(" ", ""), dict_info["category"])

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

def apply_changes():
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

def move_file(source_file, dst_dir):
    if not source_file or not os.path.exists(source_file):
        print("image dir is empty or invalid")
        return
    
    new_path = os.path.join(dst_dir, defs.IMAGE_NAME)
    entry_img_dir.delete(0, tk.END)
    entry_img_dir.insert(tk.END, new_path)
    # Use shutil.move() to move and rename the file
    shutil.move(source_file, new_path)

def find_image():
    for type in defs.IMAGE_TYPES:
        img_list = common.get_direct_child_by_extension(generator.working_dir, type)
        if len(img_list) > 0:
            set_image(generator.working_dir +  "/" + img_list[0])
            return

    entry_img_dir.delete(0, tk.END)
    label_img.config(image=None)
    label_img.image = None

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

def set_description():
    description = "Includes:\n"
    txt_desc.delete(1.0, tk.END)
    combined_list = defs.ELEMENTS + config.additional_elements
    for n in range(len(checkbox_states)):
        if n >= len(combined_list):
            checkbox_states[n] = False
        elif checkbox_states[n]:
            description += "- " + combined_list[n] + "\n"

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
    checkbox_states[6] = generator.is_narrator_voice
    checkbox_states[7] = generator.is_victory_theme
    checkbox_states[8] = generator.is_victory_animation
    checkbox_states[9] = generator.is_custom_name
    checkbox_states[10] = generator.is_single_name
    checkbox_states[11] = generator.is_ui
    checkbox_states[12] = generator.is_kirby
    checkbox_states[13] = generator.is_stage

    update_listbox()

def on_window_resize(event):
    set_image(entry_img_dir.get())

def open_config():
    config.open_config(root) 

# Create the main application window
root = tk.Tk()
root.title("Smash Ultimate Toml Generator")
for i in range(3):
    root.columnconfigure(i, weight=1)
    root.columnconfigure(i, minsize=200)
root.rowconfigure(10, weight=1)
root.minsize(640, 340)

# Set the size of the window
root.geometry("920x500")
root.configure(padx=10, pady=10) 

# column 0
label_work_dir = tk.Label(root, text="Directory")
label_work_dir.grid(row=0, column=0, sticky=tk.W, pady = (0, defs.PAD_V))

img_icon = ImageTk.PhotoImage(file='./icons/config.png')
btn_config = tk.Button(root, image=img_icon, width=15,height=15,relief=tk.FLAT ,cursor='hand2',command=open_config )
btn_config.grid(row=0, column=2, sticky=tk.E, pady = (0, defs.PAD_V))

frame_work_dir = tk.Frame(root)
frame_work_dir.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=tk.EW, pady = (0, defs.PAD_V))

btn_change_work_dir = tk.Button(frame_work_dir, text="Browse", command=change_working_directory)
btn_change_work_dir.pack(side="left", padx = (0, defs.PAD_H))

entry_work_dir = tk.Entry(frame_work_dir, width=10)
entry_work_dir.pack(fill=tk.X, expand=True)
entry_work_dir.bind("<KeyRelease>", on_update_directory)

label_url = tk.Label(root, text="Url")
label_url.grid(row=3, column=0, sticky=tk.W)

entry_url = tk.Entry(root, width=10)
entry_url.grid(row=4, column=0, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
entry_url.bind("<KeyRelease>", on_url_change)

label_authors = tk.Label(root, text="Authors")
label_authors.grid(row=5, column=0, sticky=tk.W)

entry_authors = tk.Entry(root, width=10)
entry_authors.grid(row=6, column=0, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))

frame = tk.Frame(root)
frame.grid(row=7, column=0, rowspan=2, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
frame.columnconfigure(1, weight=1)

label_ver = tk.Label(frame, text="Version")
label_ver.grid(row=0, column=0, sticky=tk.W)

entry_ver = tk.Entry(frame, width=10)
entry_ver .grid(row=1, column=0, sticky=tk.W, padx=(0,defs.PAD_H))
entry_ver.insert(0, "1.0.0")

label_cat = tk.Label(frame, text="Category")
label_cat.grid(row=0, column=1, sticky=tk.W)

combobox_cat = ttk.Combobox(frame, values=defs.CATEGORIES, width=10)
combobox_cat.grid(row=1, column=1, sticky=tk.EW)
combobox_cat.bind("<<ComboboxSelected>>", on_combobox_select)
combobox_cat.set(defs.CATEGORIES[-1])

label_img_dir = tk.Label(root, text="Image", anchor='w')
label_img_dir.grid(row=9, column=0, sticky=tk.W, padx = (0, defs.PAD_H))

frame_img = tk.Frame(root, width=10)
frame_img.grid(row=10, column=0, sticky=tk.NSEW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))

frame_img_dir = tk.Frame(frame_img, width = 10)
frame_img_dir.pack(side=tk.TOP, fill=tk.X, expand=False)

btn_select_img = tk.Button(frame_img_dir, text="Browse", command=update_image, anchor='n')
btn_select_img.pack(side=tk.LEFT, padx = (0, defs.PAD_H))

entry_img_dir = tk.Entry(frame_img_dir, width=10)
entry_img_dir.pack(fill=tk.X, expand=True)
entry_img_dir.bind("<KeyRelease>", on_update_image)

btn_download_img = tk.Button(frame_img, text="Download", command=download_img, state="disabled")
btn_download_img.pack(side=tk.BOTTOM, anchor=tk.NW, padx = (0, defs.PAD_H))

label_img = tk.Label(frame_img, justify='center', anchor='center', bg='black')
label_img.pack(fill=tk.BOTH, expand=True, pady = (0, defs.PAD_V))

# column 1
label_char_names = tk.Label(root, text="Characters")
label_char_names.grid(row=3, column=1, sticky=tk.W)

entry_char_names = tk.Entry(root, width=10)
entry_char_names.grid(row=4, column=1, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
entry_char_names.bind("<KeyRelease>", on_entry_change)

label_slots = tk.Label(root, text="Slots")
label_slots.grid(row=5, column=1, sticky=tk.W)

entry_slots = tk.Entry(root, width=10)
entry_slots.grid(row=6, column=1, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
entry_slots.bind("<KeyRelease>", on_entry_change)

label_mod_name = tk.Label(root, text="Mod Title")
label_mod_name.grid(row=7, column=1, sticky=tk.W)

entry_mod_name = tk.Entry(root, width=10)
entry_mod_name.grid(row=8, column=1, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
entry_mod_name.bind("<KeyRelease>", on_entry_change)

label_list = tk.Label(root, text="Includes")
label_list.grid(row=9, column=1, sticky=tk.W)

listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=10)
listbox.grid(row=10, column=1, sticky=tk.NSEW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))

# column 2
label_folder_name = tk.Label(root, text="Folder Name")
label_folder_name .grid(row=3, column=2, sticky=tk.W)

entry_folder_name = tk.Entry(root)
entry_folder_name.grid(row=4, column=2, sticky=tk.EW, pady = (0, defs.PAD_V))

label_display_name = tk.Label(root, text="Display Name")
label_display_name.grid(row=5, column=2, sticky=tk.W)

entry_display_name = tk.Entry(root, width=10)
entry_display_name.grid(row=6, column=2, sticky=tk.EW, pady = (0, defs.PAD_V))

label_desc = tk.Label(root, text="Description")
label_desc.grid(row=9, column=2, sticky=tk.W)

txt_desc = tk.Text(root, height=10, width=10)
txt_desc.grid(row=10, column=2, sticky=tk.NSEW, pady = (0, defs.PAD_V))

btn_apply = tk.Button(root, text="Apply", command=apply_changes)
btn_apply.grid(row=11, column=2, sticky=tk.E)

label_output = tk.Label(root)
label_output .grid(row=11, column=0, sticky=tk.W, columnspan=2)

global generator
global loader
generator = Generator()
config = Config()
loader = Loader()

global checkbox_states
checkbox_states = [False] * len(defs.ELEMENTS + config.additional_elements)
update_listbox()
listbox.bind("<Button-1>", lambda event: toggle_checkbox(listbox.nearest(event.y)))

root.bind("<Configure>", on_window_resize)

# Start the GUI event loop
root.mainloop()