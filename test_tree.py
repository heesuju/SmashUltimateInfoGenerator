import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QHeaderView
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage, QBrush, QPen, QColor
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QRect, QSize
import qdarktheme

def create_icon_with_text(pixmap: QPixmap, text):
    """ Draws text inside an image and returns it as a QIcon. """
    painter = QPainter(pixmap)
    painter.setFont(QFont("Arial", 20, QFont.Weight.ExtraBold))
    painter.setPen(Qt.GlobalColor.white)  # Text color

    # Center the text within the icon
    rect = pixmap.rect().adjusted(0, -64, 0, -64)  # Move text up by 10px
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    painter.end()
    return QIcon(pixmap)

def combine_images(base_pixmap: QPixmap, alpha_pixmap: QPixmap) -> QPixmap:
    # Convert both QPixmaps to QImages
    base_image = base_pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    alpha_image = alpha_pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)

    # Scale the alpha image to fit the width of the base image while maintaining its aspect ratio
    alpha_image = alpha_image.scaled(
        base_image.width() - 2,
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
        self.icon_size = 20  # Size of each icon

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        for row in range(self.topLevelItemCount()):
            item = self.topLevelItem(row)
            rect = self.visualItemRect(item)
            
            # Specify the column where you want multiple icons
            icons = item.data(0, Qt.ItemDataRole.UserRole)
            if icons:
                x_offset = self.columnViewportPosition(0) + 5  # Adjust position in column
                y_center = rect.center().y() - self.icon_size // 2
                for icon in icons:
                    icon_rect = QRect(x_offset + 104, y_center + 26, self.icon_size, self.icon_size)
                    icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)
                    x_offset += self.icon_size + 5  # Add spacing between icons


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
        self.tree_widget.setIconSize(QSize(72, 72)) 
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setColumnWidth(0, 200)
        
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree_widget.setHeaderLabels(["Mod Info", "Toggle"])
        
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
            (["assets/icons/cartridge_off", "assets/img/preview.webp", "assets/img/github.png"], ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01", "This mod is something... blah blah\ndshfkjdskfhjsa\ndfshskdjf\ndfkjhsk"),
            (["assets/icons/cartridge_on","assets/img/preview.webp", "assets/img/github.png"], ["assets/icons/characters/aegis.png", "assets/icons/characters/element.png", "assets/icons/characters/jack.png"],"Master Shield", "DarkHero", "C02", "C03 Stealth\ndshfkjdskfhjsa\ndfshskdjf\ndfkjhsk"),
            (["assets/icons/cartridge_off","assets/img/preview.webp", "assets/img/browse.png"], ["assets/icons/characters/wolf.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"],"Phantom Armor", "GhostKnight", "C03", "C03 Stealth\ndshfkjdskfhjsa\ndfshskdjf\ndfkjhsk"),
        ]

        for icon_paths, char_icon_paths, name, author, slots, category in sample_items:
            item = QTreeWidgetItem([name + "\n" + author + "\n" + slots + "\n", category])

            # Add Checkbox
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Unchecked)  # Unchecked by default

            # Add Thumbnail Icon
            # Load base and alpha images
            base_pixmap = QPixmap(icon_paths[0])
            alpha_pixmap = QPixmap(icon_paths[1])

            # Combine images
            combined_pixmap = combine_images(base_pixmap, alpha_pixmap)
            icon = create_icon_with_text(combined_pixmap, "FIGHTER")  # Overlay text "TXT" on image


            # icon = QIcon(QPixmap(icon_paths[0]))
            item.setIcon(0, icon)

            # Add Multiple Icons to 4th Column
            icons = [QIcon(QPixmap(path)) for path in char_icon_paths]
            item.setData(0, Qt.ItemDataRole.UserRole, icons)
            # item.setData(0, Qt.ItemDataRole.UserRole, icons)

            self.tree_widget.addTopLevelItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    # qdarktheme.setup_theme("light")
    window = ModManagerUI()
    window.show()
    sys.exit(app.exec())