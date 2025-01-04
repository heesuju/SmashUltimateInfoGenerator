"""
menu.py: The main view that contains list view showing all of the existing mods and various filters
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

from src.core.mod_loader import ModLoader
from src.core.data import load_config, get_workspace
from src.core.formatting import (
    format_folder_name, 
    format_character_names,
    format_slots
)

from src.models.mod import Mod

from src.constants.ui_params import PAD_H, PAD_V, COLUMNS
from src.constants.defs import GIT_REPO_URL

from src.ui.components.progress_bar import ProgressBar
from src.ui.components.image_treeview import ImageTreeview
from src.ui.components.paging import Paging

from src.ui.base import (
    get_text, 
    set_text, 
    clear_text, 
    open_file_dialog, 
    get_icon
)

# from .editor import Editor
# from .config import Config
from .filter import Filter
from .preview import Preview
from .preset import Preset

from src.utils.file import (
    is_valid_dir, 
    copy_directory_contents, 
    is_case_sensitive, 
    get_base_name
)
from src.utils.web import open_page
from src.utils.hash import get_hash

from src.core.hide_folder import filter_hidden
from idlelib.tooltip import Hovertip

class Menu:    
    def __init__(self, root, webdriver_manager) -> None:
        self.root = root
        self.webdriver_manager = webdriver_manager

        self.mods = []
        self.filtered_mods = []
        # self.config = Config()

        self.case_sensitive = is_case_sensitive()
        self.show()
        self.scan()
    
    def reset(self):
        self.treeview.clear()
        self.preview.clear()
            
    def open_folder(self):
        selected_item = self.treeview.get_selected()
        if selected_item:
            item = self.treeview.get_row_values(selected_item)
            values = item.get("values")
            os.startfile(values[-1])
        else:
            print("no item selected!")
    
    def toggle_mod(self):
        selected_item = self.treeview.get_selected()
        if selected_item:
            item = self.treeview.get_item(selected_item)
            path = item["values"][5].split("/")[-1].split("\\")[-1]
            hash = get_hash(path)
            workspace = self.get_valid_workspace()
            workspace_data = self.preset.workspace_list.get(workspace)
            if workspace_data:
                enabled_mods = workspace_data["mod_list"]
            
                if hash in enabled_mods: # Disable
                    self.treeview.set_row_checked(selected_item, False)
                    self.preview.set_toggle_label(False)
                    self.preset.workspace_list[workspace]["mod_list"].remove(hash)
                else: # Enable
                    self.treeview.set_row_checked(selected_item, True)
                    self.preview.set_toggle_label(True)
                    self.preset.workspace_list[workspace]["mod_list"].append(hash)

                self.preset.update_workspace_count()
            else:
                print("no workspace found")
        else:
            print("no item selected!")

    def refresh(self):
        self.filter_view.reset()
        self.paging.clear()
        clear_text(self.label_count)
        clear_text(self.label_total)
        self.reset()
        self.scan()

    def populate(self, mods:list[Mod]):
        start, end = self.paging.update(len(mods)) 
        filtered_len = len(mods)
        total = len(self.mods)
        current_count = end - start
        set_text(self.label_count, f"Showing {current_count} of {filtered_len}" if filtered_len > current_count else f"Showing {filtered_len}")
        set_text(self.label_total, f"Total: {total}")

        workspace = self.get_valid_workspace()

        images = []
        values = []
        checked = []

        for n in range(start,end):
            characters = format_character_names(mods[n].character_names)
            slots = format_slots(mods[n].character_slots)
            enabled_mods = self.preset.workspace_list[workspace]["mod_list"] if self.preset.workspace_list.get(workspace) else []
            checked.append(mods[n].hash in enabled_mods)
            images.append(mods[n].thumbnail)
            values.append([mods[n].category, characters, slots, mods[n].mod_name, mods[n].authors, mods[n].path])
        
        self.treeview.populate_items(images, values, checked)

    def on_change_page(self):
        self.reset()
        self.populate(self.filtered_mods)

    def on_prev_page(self, event):
        self.paging.prev_page()

    def on_next_page(self, event):
        self.paging.next_page()

    def search(self):
        self.paging.cur_page = 1
        self.apply_filters()

    def apply_filters(self):
        workspace = self.get_valid_workspace()
        workspace_data = self.preset.workspace_list.get(workspace)
        enabled_mods = workspace_data.get("mod_list")if workspace_data else []
        self.reset()
        include_hidden = self.filter_view.get_filter_params().get("include_hidden", False)
        if not include_hidden:
            self.filtered_mods = filter_hidden(self.mods)
            self.filtered_mods = self.filter_view.filter_mods(self.filtered_mods, enabled_mods)
        else:
            self.filtered_mods = self.filter_view.filter_mods(self.mods, enabled_mods)
        self.populate(self.filtered_mods)

    def on_finish_edit(self, old_dir:str, new_dir:str):
        is_dir_same = True if old_dir == new_dir else False
        dir_to_update = old_dir if is_dir_same else new_dir
        ModLoader(dir_to_update, self.on_finish_update)

    def on_finish_update(self, mods):
        valid_mods = [mod for mod in self.mods if os.path.isdir(mod["path"])]

        for n in mods:
            found_match = False
            for idx, m in enumerate(valid_mods):
                new_path = get_base_name(n.get("path", ""))
                mod_path = get_base_name(m.get("path", ""))

                if not self.case_sensitive:
                    new_path = new_path.lower()
                    mod_path = mod_path.lower()

                if new_path == mod_path:
                    valid_mods[idx] = n
                    found_match = True
                    print("updated dir:", n["path"])
                    break

            if found_match == False:
                valid_mods.append(n)
                print("added dir:", n["path"])
        self.mods = valid_mods
        self.search()

    def on_scan_progress(self, future):
        self.progressbar.on_update()

    def on_scanned(self, mods):
        self.mods = mods
        self.filtered_mods = mods
        if len(mods) > 0:
            self.search()

    def on_escape(self, event):
        self.preview.clear()
        if self.preview.is_shown:
            self.preview.toggle()
        elif self.preset.is_shown:
            self.preset.toggle()

    def on_item_selected(self, event):
        selected_item = self.treeview.get_selected()
        if not selected_item:
            return
        
        if self.treeview.pos_x >= 20 and self.treeview.pos_x <= 145:
            self.toggle_mod()
            self.treeview.pos_x = 0

        item = self.treeview.get_row_values(selected_item)
        path = item['values'][-1]
        selected_mod = None
        for mod in self.mods:
            if mod.path == path:
                selected_mod = mod
                break
        
        self.preview.update(item["tags"][0] == "enabled", selected_mod)
            
    def on_double_clicked(self, event):
        self.open_editor()

    def open_editor(self):
        pass
        # selected_item = self.treeview.get_selected()
        # if selected_item:
        #     item = self.treeview.item(selected_item)
        #     Editor(self.root, self.webdriver_manager, item['values'][-1], self.on_finish_edit)
        # else:
        #     print("nothing selected in treeview!")

    def open_config(self):
        pass
        # self.config.load()
        # self.config.open_config(self.root)

    def on_enable_mod(self, event):
        self.toggle_mod()
    
    def on_scan_start(self, max_count):
        self.progressbar.progress_max = max_count
        
    def scan(self):
        self.progress_cnt = 0
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            set_text(self.entry_dir, config_data["default_directory"])
            ModLoader(
                config_data["default_directory"], 
                on_start=self.on_scan_start, 
                on_progress=self.on_scan_progress, 
                on_finish=self.on_scanned
            )
    
    def on_browse(self):
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            working_dir = open_file_dialog(config_data["default_directory"])
        else:
            working_dir = open_file_dialog()
        
        self.change_directory(working_dir)
    
    def on_directory_changed(self, event):
        new_directory = get_text(self.entry_dir)
        self.change_directory(new_directory)

    def change_directory(self, new_dir:str):
        if new_dir and is_valid_dir(new_dir):
            # self.config.set_default_dir(new_dir)
            set_text(self.entry_dir, new_dir)
            self.preset.load_workspace()
            self.refresh()
        else:
            print("invalid directory!")

    def on_window_resize(self, event):
        selected_item = self.treeview.get_selected()        
        if selected_item and self.preview.is_shown:
            item = self.treeview.get_row_values(selected_item)
            path = item["values"][-1]
            self.preview.set_image(os.path.join(path, "preview.webp"))

    def save_preset(self):
        self.preset.save_presets()
        self.preset.save_workspaces()

    def toggle_preset(self):
        if not self.preset.is_shown:
            if self.preview.is_shown:
                self.toggle_preview()
            self.btn_show_preset.config(bg="white", image=self.icon_preset)
        else:
            self.btn_show_preset.config(bg="SystemButtonFace", image=self.icon_preset_off)

        self.preset.toggle()

    def toggle_preview(self):
        if not self.preview.is_shown:
            if self.preset.is_shown:
                self.toggle_preset()
            self.btn_show_preview.config(bg="white", image=self.icon_preview)
        else:
            self.btn_show_preview.config(bg="SystemButtonFace", image=self.icon_preview_off)

        self.preview.toggle()

    def open_git(self):
        open_page(GIT_REPO_URL)

    def get_valid_workspace(self):
        name = get_workspace()
        workspace = self.preset.workspace_list.get(name, None)
        if workspace is None:
            return "Default"
        else:
            return name
        
    def on_drag_drop(self, dir):
        dir = dir.strip('{}')
        config = load_config()
        default_dir = config.get("default_directory")
        if is_valid_dir(default_dir) and is_valid_dir(dir):
            ModLoader(dir, self.on_drop_scanned)

    def on_drop_scanned(self, mods:list[Mod]):
        if len(mods) <= 0: 
            return
        
        scanned_mod = mods[0]
        dir = scanned_mod.path
        config = load_config()
        default_dir = config.get("default_directory")

        folder_name = format_folder_name(
            scanned_mod.get("characters"),
            scanned_mod.get("slots"),
            scanned_mod.mod_name,
            scanned_mod.category
        )
        
        new_dir = os.path.join(default_dir, folder_name)
        num = 0
        new_name = folder_name
        while os.path.exists(new_dir): 
            num+=1
            new_name = f"{folder_name}{num}"
            new_dir = os.path.join(default_dir, new_name)
        try:
            copy_directory_contents(dir, default_dir, new_name)
            print("successfully added dir:", dir)
            messagebox.showinfo("Info", "Successfully copied contents into mod directory!")
            self.on_finish_edit("", new_dir)
        except PermissionError:
            print(f"PermissionError: You do not have the required permissions to copy to '{new_dir}'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def show(self):
        self.f_dir = tk.Frame(self.root)
        self.f_dir.pack(padx=PAD_H, pady=PAD_V, fill="x")
        
        self.l_dir = tk.Label(self.f_dir, text="Mod Directory")
        self.l_dir.pack(side=tk.LEFT)

        self.entry_dir = tk.Entry(self.f_dir, width=10)
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=PAD_H)
        self.entry_dir.bind('<Return>', self.on_directory_changed)

        self.icon_browse = get_icon('browse')
        self.btn_dir = tk.Button(self.f_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.on_browse)
        self.btn_dir.pack(side=tk.LEFT, padx = (0, PAD_H))
        
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X, padx=(0,0))

        self.frame_content = tk.Frame(self.root)
        self.frame_content.pack(fill="both", expand=True)

        self.frame_list = tk.Frame(self.frame_content)
        self.frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.filter_view = Filter(self.frame_list, self.search, self.refresh)
        
        separator = ttk.Separator(self.frame_content, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=(0,0))

        self.workspace_frame = ttk.Frame(self.frame_content)
        
        self.preset = Preset(
            root=self.workspace_frame, 
            callback=self.search
        )

        self.info_frame = ttk.Frame(self.frame_content)
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.rowconfigure(index=1, weight=1)
        self.info_frame.rowconfigure(index=3, weight=1)
        self.info_frame.pack_forget()

        self.nav_frame = tk.Frame(self.frame_content)
        self.nav_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        separator = ttk.Separator(self.frame_list, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, PAD_V))

        self.frame_count = tk.Frame(self.frame_list)
        self.frame_count.pack(fill=tk.BOTH, padx=PAD_H)

        self.label_count = tk.Label(self.frame_count, text="Showing 0", anchor=tk.W)
        self.label_count.pack(side=tk.LEFT)

        self.label_total = tk.Label(self.frame_count, text="Total: 0", anchor=tk.W)
        self.label_total.pack(side=tk.RIGHT)

        self.treeview = ImageTreeview(
            root=self.root, 
            parent=self.frame_list, 
            columns=COLUMNS,
            on_drag_drop=self.on_drag_drop,
            on_selected=self.on_item_selected,
            on_escape=self.on_escape,
            on_double_clicked=self.on_double_clicked,
            on_space=self.on_enable_mod,
            on_return=self.on_enable_mod,
            on_left=self.on_prev_page,
            on_right=self.on_next_page
        )
        
        self.paging = Paging(
            root = self.frame_list, 
            callback = self.on_change_page
        )

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0,PAD_V))

        self.f_footer = tk.Frame(self.root)
        self.f_footer.pack(padx = PAD_H, pady = (0, PAD_V), fill="x")

        self.progressbar = ProgressBar(self.root, self.f_footer)

        self.icon_save = get_icon('save')
        self.btn_save = tk.Button(self.f_footer, image=self.icon_save, text=" Save", compound=tk.LEFT, cursor='hand2', command=self.save_preset, width=100)
        self.btn_save.pack(side=tk.RIGHT)

        self.icon_preview = get_icon('details')
        self.icon_preview_off = get_icon('details_inactive')
        self.icon_preset = get_icon('workspace')
        self.icon_preset_off = get_icon('workspace_inactive')
        self.icon_git = get_icon('github_off')

        self.btn_show_preset = tk.Button(
            self.nav_frame,  
            image=self.icon_preset_off, 
            cursor='hand2', 
            command=self.toggle_preset, 
            borderwidth=0,
            relief=tk.FLAT,
            width=50,
            height=50
        )
        self.btn_show_preset.pack()
        Hovertip(self.btn_show_preset,'Show Workspace')

        self.btn_show_preview = tk.Button(
            self.nav_frame,  
            image=self.icon_preview_off,  
            cursor='hand2', 
            command=self.toggle_preview, 
            borderwidth=0,
            relief=tk.FLAT,
            width=50,
            height=50
        )
        self.btn_show_preview.pack()
        Hovertip(self.btn_show_preview,'Show Preview')

        self.btn_github = tk.Button(
            self.nav_frame,  
            image=self.icon_git,  
            cursor='hand2', 
            borderwidth=0,
            relief=tk.FLAT,
            width=50,
            height=50,
            command=self.open_git
        )
        self.btn_github.pack(side=tk.BOTTOM)
        Hovertip(self.btn_github,'Go to github page')

        self.preview = Preview(self.info_frame, self.open_editor, self.open_folder, self.toggle_mod, self.apply_filters)
        self.root.bind("<Configure>", self.on_window_resize)