"""
menu.py: The main view that contains list view showing all of the existing mods and various filters
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from idlelib.tooltip import Hovertip
from src.core.mod_loader import ModLoader
from src.core.mod_installer import ModInstaller
from src.core.data import load_config, get_workspace
from src.core.formatting import (
    format_folder_name,
    format_character_names,
    format_slots,
    group_char_name
)
from src.core.filter import filter_mods
from src.models.mod import Mod
from src.constants.ui_params import PAD_H, PAD_V, COLUMNS
from src.constants.defs import GIT_REPO_URL
from src.constants.colors import DEFAULT, WHITE
from src.constants.strings import (
    INFO_DRAG_DROP_COPY_COMPLETE, 
    INFO, 
    TITLE_PRESET_SAVE, 
    ASK_PRESET_SAVE, 
    ASK_DUPLICATE_ENTRY, 
    TITLE_DUPLICATE_ENTRY, 
    WARNING_NO_WORKSPACE, 
    WARNING, 
    WARNING_MOD_DIR, 
    WARNING_FILE_DIR,
    DRAG_DROP_COPY_FAILED
)
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
from src.utils.file import (
    is_valid_dir,
    is_valid_path,
    copy_directory_contents,
    is_case_sensitive,
    get_base_name,
    is_same_dir,
    sanitize_path
)
from src.utils.web import open_page
from src.utils.hash import get_hash
from src.utils.string_helper import remove_spacing
from src.core.hide_folder import filter_hidden
from .editor import Editor
from .config import Config
from .search_filter import SearchFilter
from .preview import Preview
from .preset import Preset

class Menu:    
    def __init__(self, root, webdriver_manager) -> None:
        self.root = root
        self.webdriver_manager = webdriver_manager

        self.mods = []
        self.filtered_mods = []
        self.config = Config()

        self.case_sensitive = is_case_sensitive()
        self.show()
        self.scan()

    def reset(self):
        self.treeview.clear()
        self.preview.clear()

    def open_folder(self):
        selected_item = self.treeview.get_selected_id()
        if selected_item:
            values = self.treeview.get_values(selected_item)
            if values is not None:
                os.startfile(values[-1])
        else:
            print("no item selected!")

    def toggle_mod(self):
        selected_item = self.treeview.get_selected_id()
        if selected_item:
            item = self.treeview.get_item(selected_item)
            path = item["values"][5].split("/")[-1].split("\\")[-1]
            hash_value = get_hash(path)
            workspace = self.get_valid_workspace()
            workspace_data = self.preset.workspace_list.get(workspace)
            if workspace_data:
                enabled_mods = workspace_data["mod_list"]
            
                if hash_value in enabled_mods: # Disable
                    self.treeview.set_row_checked(selected_item, False)
                    self.preview.set_toggle_label(False)
                    self.preset.workspace_list[workspace]["mod_list"].remove(hash_value)
                else: # Enable
                    self.treeview.set_row_checked(selected_item, True)
                    self.preview.set_toggle_label(True)
                    self.preset.workspace_list[workspace]["mod_list"].append(hash_value)

                self.preset.update_workspace_count()
            else:
                if self.preset.is_shown == False:
                    self.toggle_preset()
                messagebox.showwarning(WARNING, WARNING_NO_WORKSPACE)
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
        """
        Adds items to the list of mods
        """
        start, end = self.paging.update(len(mods)) 
        filtered_len = len(mods)
        total = len(self.mods)
        current_count = end - start
        if filtered_len > current_count:
            set_text(self.label_count, f"Showing {current_count} of {filtered_len}")
        else:
            set_text(self.label_count, f"Showing {filtered_len}")

        set_text(self.label_total, f"Total: {total}")

        workspace = self.get_valid_workspace()

        images, values, checked = [], [], []

        for n in range(start,end):
            keys, names, groups, series, slots = mods[n].get_character_data()
            characters = format_character_names(names)
            slots = format_slots(slots)
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
        if not self.filter_view.params.include_hidden:
            self.filtered_mods = filter_hidden(self.mods)
            self.filtered_mods = filter_mods(self.filtered_mods, self.filter_view.params, enabled_mods)
        else:
            self.filtered_mods = filter_mods(self.mods, self.filter_view.params, enabled_mods)
        self.populate(self.filtered_mods)

    def on_finish_edit(self, old_dir:str, new_dir:str):
        is_dir_same = is_same_dir(old_dir, new_dir)
        dir_to_update = old_dir if is_dir_same else new_dir
        ModLoader([dir_to_update], self.on_finish_update)

    def on_finish_update(self, mods:list[Mod]):
        valid_mods = [mod for mod in self.mods if os.path.isdir(mod.path)]

        for n in mods:
            found_match = False
            for idx, m in enumerate(valid_mods):
                new_path = get_base_name(n.path)
                mod_path = get_base_name(m.path)

                if not self.case_sensitive:
                    new_path = new_path.lower()
                    mod_path = mod_path.lower()

                if new_path == mod_path:
                    valid_mods[idx] = n
                    found_match = True
                    print("updated dir:", n.path)
                    break

            if found_match == False:
                valid_mods.append(n)
                print("added dir:", n.path)
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
            self.toggle_preview()
        elif self.preset.is_shown:
            self.toggle_preset()

    def on_item_selected(self, event:tk.Event = None):
        selected_item = self.treeview.get_selected_id()
        if not selected_item:
            return
        
        if self.treeview.pos_x >= 20 and self.treeview.pos_x <= 145:
            self.toggle_mod()
            self.treeview.pos_x = 0

        self.update_preview(selected_item)
            
    def update_preview(self, selected_item:str):
        if not selected_item:
            return

        item = self.treeview.get_item(selected_item)
        values = item.get("values", None)
        selected_mod = None

        if values is not None:
            path = values[-1]    
            for mod in self.filtered_mods:
                if mod.path == path:
                    selected_mod = mod
                    break
            
        self.preview.update(item["tags"][0] == "enabled", selected_mod)
    
    def on_double_clicked(self, event):
        self.open_editor()

    def open_editor(self):
        selected_item = self.treeview.get_selected_id()
        if selected_item:
            values = self.treeview.get_values(selected_item)
            Editor(
                self.root,
                self.webdriver_manager,
                values[-1],
                self.on_finish_edit
            )
        else:
            print("nothing selected in treeview!")

    def open_config(self):
        self.config.load()
        self.config.open_config(self.root)

    def on_enable_mod(self, event):
        self.toggle_mod()
    
    def on_scan_start(self, max_count):
        self.progressbar.progress_max = max_count
        
    def scan(self):
        self.progress_cnt = 0
        config_data = load_config()
        if config_data is not None and config_data.default_directory:
            set_text(self.entry_dir, config_data.default_directory)
            ModLoader(
                config_data.default_directory, 
                on_start=self.on_scan_start, 
                on_progress=self.on_scan_progress, 
                on_finish=self.on_scanned
            )

    def on_browse(self):
        config_data = load_config()
        if config_data is not None and config_data.default_directory:
            working_dir = open_file_dialog(config_data.default_directory)
        else:
            working_dir = open_file_dialog()
        
        self.change_directory(working_dir)
    
    def on_directory_changed(self, event):
        new_directory = get_text(self.entry_dir)
        self.change_directory(new_directory)

    def change_directory(self, new_dir:str):
        if new_dir and is_valid_dir(new_dir):
            self.config.set_default_dir(new_dir)
            set_text(self.entry_dir, new_dir)
            self.preset.load_workspace()
            self.refresh()
        else:
            print("invalid directory!")

    def on_save_preset(self)->None:
        if self.config is not None:
            self.config.settings.cache_dir = self.preset.cache_dir
            self.config.settings.workspace = self.preset.workspace
            name = self.config.settings.workspace
            list_enabled = self.preset.workspace_list.get(name, None)
            if list_enabled is not None:
                count = len(list_enabled["mod_list"])
                result = messagebox.askokcancel(TITLE_PRESET_SAVE, ASK_PRESET_SAVE.format(count, name))
                
                if result:
                    self.config.save_config()
                    self.save_preset()

    def save_preset(self):
        self.preset.save_presets()
        self.preset.save_workspaces()

    def toggle_preset(self):
        if not self.preset.is_shown:
            if self.preview.is_shown:
                self.toggle_preview()
            self.btn_show_preset.config(bg=WHITE, image=self.icon_preset)
        else:
            self.btn_show_preset.config(bg=DEFAULT, image=self.icon_preset_off)

        self.preset.toggle()

    def toggle_preview(self):
        if not self.preview.is_shown:
            if self.preset.is_shown:
                self.toggle_preset()
            self.btn_show_preview.config(bg=WHITE, image=self.icon_preview)
            if self.preview.mod is None:
                self.update_preview(self.treeview.get_selected_id())
        else:
            self.btn_show_preview.config(bg=DEFAULT, image=self.icon_preview_off)

        self.preview.toggle()

    def open_git(self):
        open_page(GIT_REPO_URL)

    def get_valid_workspace(self):
        name = self.preset.workspace
        workspace = self.preset.workspace_list.get(name, None)
        if workspace is None:
            return "Default"
        else:
            return name
        
    def on_drag_drop(self, dir:str)->None:
        """On drag n dropped file or folder"""
        dir = sanitize_path(dir.strip('{}'))
        settings = load_config()
        default_dir = settings.default_directory
        
        if not default_dir or is_valid_dir(default_dir) == False:
            messagebox.showerror(WARNING, WARNING_MOD_DIR)
            return

        if not dir or is_valid_path(dir) == False:
            messagebox.showerror(WARNING, WARNING_FILE_DIR)
            return

        ModInstaller(dir, default_dir, self.on_drop_scanned)

    def on_drop_scanned(self, added_dirs:list[str])->None:
        if len(added_dirs) <= 0: 
            messagebox.showinfo(WARNING, DRAG_DROP_COPY_FAILED)
            return
        
        ModLoader(added_dirs, self.on_finish_update)
        messagebox.showinfo(INFO, INFO_DRAG_DROP_COPY_COMPLETE)

    def show(self):
        """
        Shows the UI
        """
        self.f_dir = tk.Frame(self.root)
        self.f_dir.pack(padx=PAD_H, pady=PAD_V, fill="x")

        self.l_dir = tk.Label(self.f_dir, text="Mod Directory")
        self.l_dir.pack(side=tk.LEFT)

        self.entry_dir = tk.Entry(self.f_dir, width=10)
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=PAD_H)
        self.entry_dir.bind('<Return>', self.on_directory_changed)

        self.icon_browse = get_icon('browse')
        self.btn_dir = tk.Button(
            self.f_dir,
            image=self.icon_browse,
            relief=tk.FLAT,
            cursor='hand2',
            command=self.on_browse
        )
        self.btn_dir.pack(side=tk.LEFT, padx = (0, PAD_H))

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X, padx=(0,0))

        self.frame_content = tk.Frame(self.root)
        self.frame_content.pack(fill="both", expand=True)

        self.frame_list = tk.Frame(self.frame_content)
        self.frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.filter_view = SearchFilter(self.frame_list, self.search, self.refresh)

        separator = ttk.Separator(self.frame_content, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=(0,0))

        self.workspace_frame = ttk.Frame(self.frame_content)
        self.preset = Preset(self.workspace_frame, self.search)

        self.info_frame = ttk.Frame(self.frame_content)
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
        self.btn_save = tk.Button(
            self.f_footer,
            image=self.icon_save,
            text=" Save",
            compound=tk.LEFT,
            cursor='hand2',
            command=self.on_save_preset,
            width=100
        )
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

        self.preview = Preview(
            self.info_frame,
            self.open_editor,
            self.open_folder,
            self.toggle_mod,
            self.apply_filters
        )
