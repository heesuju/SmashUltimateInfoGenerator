from typing import List
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QFrame
)
from PyQt6.QtCore import QTimer
from src.ui.components.layout import VBox
from src.ui.grid_list import GridList
from src.models.mod import ModItem
from src.ui.components.paging import Paging
from src.managers.online_manager import OnlineManager

from src.ui.online_grid_item import OnlineGridListItem
from src.ui.search_bar import SearchBar
from src.ui.components.filter_chips import FilterChips

from src.ui.components.loading_overlay import LoadingOverlay

class OnlineModList(QWidget):
    def __init__(self, online_manager: OnlineManager, filter_manager=None):
        super().__init__()
        self.online_manager = online_manager
        self.filter_manager = filter_manager
        
        self.online_manager.state_changed.connect(self.update_view)
        self.online_manager.search_complete.connect(self.populate)
        
        layout = VBox()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.search = SearchBar(online_manager=online_manager)
        layout.addWidget(self.search)
        
        self.filter_chips = FilterChips(filter_manager) if filter_manager else None
        if self.filter_chips:
            layout.addWidget(self.filter_chips)
        
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_layout = VBox(margin=0, spacing=0)
        self.frame.setLayout(self.frame_layout)
        layout.addWidget(self.frame)
        
        self.grid_list = GridList(self.online_manager, item_class=OnlineGridListItem) 
        self.frame_layout.addWidget(self.grid_list)
        
        self.paging = Paging(callback=self.on_page_changed, lock_size=True)
        layout.addWidget(self.paging)
        self.paging.page_size = 15
        
        # Initialize Overlay
        self.loading_overlay = LoadingOverlay(self.frame) # Check parent
        
    def resizeEvent(self, event):
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.resize(self.frame.size())
        super().resizeEvent(event)
        
    def on_page_changed(self, page: int, size: int):
        self.online_manager.search(
            self.online_manager.current_query, 
            self.online_manager.current_author, 
            page,
            self.online_manager.current_sort
        )
        
    def update_view(self):
        if self.online_manager.is_loading:
            self.loading_overlay.resize(self.frame.size())
            self.loading_overlay.show_loading()
        else:
            self.loading_overlay.hide_loading()
            
    def populate(self, mods: List[ModItem]):
        self.grid_list.clear()
        
        if hasattr(self, '_populate_timer') and self._populate_timer.isActive():
            self._populate_timer.stop()
        
        self._mods_to_populate = list(mods)
        self._populate_index = 0
        
        self.paging.cur_page = self.online_manager.current_page
        total_count = self.online_manager.total_results
        self.paging.update(total_count)
        
        self._populate_timer = QTimer()
        self._populate_timer.timeout.connect(self._populate_next_item)
        self._populate_timer.start(0)
        
    def _populate_next_item(self):
        if self._populate_index < len(self._mods_to_populate):
            mod = self._mods_to_populate[self._populate_index]
            self.grid_list.add_item(mod)
            self._populate_index += 1
        else:
            self._populate_timer.stop()
            self._mods_to_populate = []
            self._populate_index = 0
