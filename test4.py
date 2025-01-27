from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QCheckBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage
from PyQt6.QtCore import Qt, QRect, QSize
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QPen, QColor
from PyQt6.QtCore import Qt, QRect

def combine_images(base_pixmap: QPixmap, alpha_pixmap: QPixmap) -> QPixmap:
    # Convert both QPixmaps to QImages
    base_image = base_pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    alpha_image = alpha_pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)

    # Scale the alpha image to fit the width of the base image while maintaining its aspect ratio
    alpha_image = alpha_image.scaled(
        base_image.width(),
        base_image.height(),
        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        transformMode=Qt.TransformationMode.SmoothTransformation,
    )

    # Calculate offsets to center the scaled alpha image
    offset_x = (base_image.width() - alpha_image.width()) // 2
    offset_y = (base_image.height() - alpha_image.height()) // 2

    # Create a new image to store the final result
    result_image = QImage(base_image.size(), QImage.Format.Format_ARGB32)
    result_image.fill(Qt.GlobalColor.transparent)  # Fill with transparency

    # Combine images
    for y in range(base_image.height()):
        for x in range(base_image.width()):
            # Get the base image's color and alpha
            base_color = base_image.pixelColor(x, y)
            base_alpha = base_color.alpha()

            # Determine if the pixel is within the alpha image bounds
            if offset_x <= x < offset_x + alpha_image.width() and offset_y <= y < offset_y + alpha_image.height():
                # Calculate coordinates in the alpha image
                alpha_x = x - offset_x
                alpha_y = y - offset_y

                # Get the color from the alpha image
                alpha_color = alpha_image.pixelColor(alpha_x, alpha_y)

                if base_alpha == 255:  # Base image is fully opaque
                    # Keep the base image as is
                    new_color = base_color
                else:
                    # Calculate the inverted alpha of the base image
                    inverted_alpha = 255 - base_alpha

                    # Combine alpha image's color with the inverted alpha
                    new_alpha = int(alpha_color.alpha() * (inverted_alpha / 255))
                    new_color = QColor(
                        alpha_color.red(),
                        alpha_color.green(),
                        alpha_color.blue(),
                        new_alpha,
                    )
            else:
                # Outside the alpha image bounds, retain the base image pixel
                new_color = base_color

            # Set the new color to the result image
            result_image.setPixelColor(x, y, new_color)

    # Convert back to QPixmap
    return QPixmap.fromImage(result_image)

class CustomTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.icon_size = 24  # Size of each icon

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        for row in range(self.topLevelItemCount()):
            item = self.topLevelItem(row)
            rect = self.visualItemRect(item)
            
            # Specify the column where you want multiple icons
            icons = item.data(4, Qt.ItemDataRole.UserRole)
            if icons:
                x_offset = self.columnViewportPosition(4) + 5  # Adjust position in column
                y_center = rect.center().y() - self.icon_size // 2
                for icon in icons:
                    icon_rect = QRect(x_offset, y_center, self.icon_size, self.icon_size)
                    icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)
                    x_offset += self.icon_size + 5  # Add spacing between icons

            icons = item.data(0, Qt.ItemDataRole.UserRole)
            if icons:
                icon_size = 64
                x_offset = self.columnViewportPosition(0) + 39  # Adjust position in column
                y_center = rect.center().y() - icon_size // 2
                base = icons[0]
                icon = icons[0]
                icon_rect = QRect(x_offset, y_center, icon_size, icon_size)
                icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)


class ModManagerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mod Manager")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Top Controls
        top_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("SELECT ALL")
        self.add_button = QPushButton("ADD")
        self.remove_button = QPushButton("REMOVE")
        top_layout.addWidget(self.select_all_checkbox)
        top_layout.addStretch()
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.remove_button)
        layout.addLayout(top_layout)

        # Custom Tree Widget with Multiple Columns
        self.tree_widget = CustomTreeWidget()
        self.tree_widget.setIconSize(QSize(64, 64)) 
        self.tree_widget.setColumnCount(5)
        self.tree_widget.setColumnWidth(0, 200)
        
        self.tree_widget.setHeaderLabels(["Mod Name", "Author", "Status", "Category", ""])
        
        layout.addWidget(self.tree_widget)

        # Bottom Controls
        bottom_layout = QHBoxLayout()
        self.hide_button = QPushButton("HIDE")
        self.enable_button = QPushButton("ENABLE")
        self.disable_button = QPushButton("DISABLE")
        self.get_url_button = QPushButton("GET URL")
        self.generate_info_button = QPushButton("GENERATE INFO.TOML")
        bottom_layout.addWidget(self.hide_button)
        bottom_layout.addWidget(self.enable_button)
        bottom_layout.addWidget(self.disable_button)
        bottom_layout.addWidget(self.get_url_button)
        bottom_layout.addWidget(self.generate_info_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.populate_tree()

    def populate_tree(self):
        # Sample Data with (Thumbnail Paths, Name, Author, Status, Category)
        sample_items = [
            (["assets/img/cartridge", "assets/img/preview.webp", "assets/img/github.png"], ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "Enabled", "C01 Effects"),
            (["assets/img/cartridge","assets/img/preview.webp", "assets/img/github.png"], ["assets/icons/characters/aegis.png", "assets/icons/characters/element.png", "assets/icons/characters/jack.png"],"Master Shield", "DarkHero", "Disabled", "C02 Defense"),
            (["assets/img/cartridge","assets/img/preview.webp", "assets/img/browse.png"], ["assets/icons/characters/wolf.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"],"Phantom Armor", "GhostKnight", "Enabled", "C03 Stealth"),
        ]

        for icon_paths, char_icon_paths, name, author, status, category in sample_items:
            item = QTreeWidgetItem([name, author, status, category, ""])

            # Add Checkbox
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Unchecked)  # Unchecked by default

            # Add Thumbnail Icon
            # Load base and alpha images
            base_pixmap = QPixmap(icon_paths[0])
            alpha_pixmap = QPixmap(icon_paths[1])

            # Combine images
            combined_pixmap = combine_images(base_pixmap, alpha_pixmap)


            # icon = QIcon(QPixmap(icon_paths[0]))
            item.setIcon(0, QIcon(combined_pixmap))

            # Add Multiple Icons to 4th Column
            icons = [QIcon(QPixmap(path)) for path in char_icon_paths]
            item.setData(4, Qt.ItemDataRole.UserRole, icons)
            # item.setData(0, Qt.ItemDataRole.UserRole, icons)

            self.tree_widget.addTopLevelItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModManagerUI()
    window.show()
    sys.exit(app.exec())