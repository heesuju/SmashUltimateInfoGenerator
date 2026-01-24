from PyQt6.QtWidgets import (
    QWidget, 
    QLineEdit,
    QComboBox,
)
from src.ui.components.side_panel import SidePanel
from src.ui.components.single_combobox import SingleComboBox
from src.constants.enums import Category

class OnlineFilterPanel(SidePanel):
    def __init__(self, online_manager):
        super().__init__("Online Filters")
        self.online_manager = online_manager
        
        # Author filter
        self.author = QLineEdit()
        self.author.setPlaceholderText("Author Name")
        self.body.addWidget(self.author)
        
        # Category filter (single selection)
        # Category filter not supported by API for some reason
        # self.category = SingleComboBox()
        # self.category.addItem("All Categories")
        # self.category.addItems(Category.list())
        # self.body.addWidget(self.category)
        
        # Sort dropdown
        self.sort = SingleComboBox()
        self.sort.addItems([
            "Relevance",
            "Popularity", 
            "Newest",
            "Updated"
        ])
        self.body.addWidget(self.sort)
        
        self.body.addStretch(1)
        
        # Footer buttons
        self.add_footer_button("Reset", self.reset)
        self.add_footer_button("Apply", self.apply, primary=True)
    
    def reset(self):
        """Reset all filters to defaults"""
        self.author.clear()
        self.category.setCurrentIndex(0)
        self.sort.setCurrentIndex(0)
    
    def apply(self):
        """Apply filters and trigger search"""
        author = self.author.text()
        
        # Get selected category (single selection, 0 = All Categories)
        category_index = self.category.currentIndex()
        category_filter = None if category_index == 0 else [Category.list()[category_index - 1]]
        
        # Get sort option (correct API values)
        sort_map = {
            0: "best_match",     # Relevance
            1: "popularity",     # Popularity
            2: "date",           # Newest
            3: "udate"           # Updated
        }
        sort_option = sort_map.get(self.sort.currentIndex(), "best_match")
        
        # Trigger search with filters (including sort)
        # Get current search query from online_manager if exists, otherwise use author
        query = self.online_manager.current_query if self.online_manager.current_query else author
        self.online_manager.search(query=query, author=author, page=1, sort=sort_option)
    
    def reset_filter(self):
        """Alias for reset to match FilterPanel interface"""
        self.reset()
