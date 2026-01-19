import os
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, 
                             QGraphicsSimpleTextItem, QGraphicsPixmapItem )
from PyQt6.QtGui import QPixmap, QFont, QBrush, QColor, QImage
from PyQt6.QtCore import Qt, QPointF, QUrl
from PyQt6.QtCore import QVariantAnimation
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

ICON_OFF = "assets/icons/cartridge_off"
ICON_ON = "assets/icons/cartridge_on"
SIZE = 70
TEXT_YLOC = 10.5
FONT = "Arial"
FONT_SIZE = 6
PRESS_AMOUNT = 5


def convert_to_grayscale(pixmap:QPixmap):
    image = pixmap.toImage()
    grayscale_image = image.convertToFormat(QImage.Format.Format_Grayscale8)
    return QPixmap.fromImage(grayscale_image)

class Overlay(QGraphicsView):
    # Static cache for cartridge icons to avoid repeated loading/scaling
    _cartridge_cache = {}

    def __init__(self, image_path:str, parent=None, initial_enabled=False, on_toggle_callback=None):
        super().__init__(parent)
        self.image_path = image_path
        self.enabled = initial_enabled
        self.on_toggle_callback = on_toggle_callback

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene = QGraphicsScene()
        self.setScene(self.graphics_scene)
        # self.setStyleSheet("QGraphicsView { border: none; padding: 0px; }")
        # self.setStyleSheet("background: transparent;")

        # Use the correct cartridge icon based on initial state
        icon_type = ICON_ON if initial_enabled else ICON_OFF
        if icon_type not in Overlay._cartridge_cache:
             pix = QPixmap(icon_type).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
             Overlay._cartridge_cache[icon_type] = pix
        
        cartridge = Overlay._cartridge_cache[icon_type]

        preview = QPixmap(image_path)
        preview = preview.scaled(cartridge.width() - 4, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.preview_item= QGraphicsPixmapItem(preview)
        self.graphics_scene.addItem(self.preview_item)
        
        
        self.cartridge_item= QGraphicsPixmapItem(cartridge)
        self.graphics_scene.addItem(self.cartridge_item)
        self.setSceneRect(self.cartridge_item.sceneBoundingRect())
        
        # center
        self.parent_width = cartridge.width()
        self.parent_height = cartridge.height()
        self.item_width = preview.width()
        self.item_height = preview.height()
        self.preview_item.setPos((self.parent_width - self.item_width)/2, (self.parent_height - self.item_height)/2)
        
        # Determine category text from parent
        cat_text = "FIGHTER"
        if parent and hasattr(parent, "mod") and hasattr(parent.mod, "category"):
            c = parent.mod.category
            # Handle Enum or String
            if hasattr(c, "value"):
                cat_text = str(c.value).upper()
            else:
                cat_text = str(c).upper()

        self.text = QGraphicsSimpleTextItem(cat_text)
        font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        font.setBold(True)
        self.text.setFont(font)
        self.text.setBrush(QBrush(QColor("white")))  # Set the font color to red
        self.graphics_scene.addItem(self.text)
        self.text.setPos((self.graphics_scene.width() - self.text.boundingRect().width()) / 2, TEXT_YLOC)

        # self.anim = QVariantAnimation()
        # self.anim.setStartValue(0.0)
        # self.anim.setEndValue(1.0)
        # self.anim.setDuration(2000)
        # self.anim.valueChanged.connect(self.move)
        # self.anim.start()
    
    def mousePressEvent(self, event):
        self.cartridge_item.setPos(0, PRESS_AMOUNT)
        self.preview_item.setPos((self.parent_width - self.item_width)/2, (self.parent_height - self.item_height)/2 + PRESS_AMOUNT)
        self.text.setPos((self.graphics_scene.width() - self.text.boundingRect().width()) / 2, TEXT_YLOC + PRESS_AMOUNT)
        # super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.cartridge_item.setPos(0, 0)
        self.preview_item.setPos((self.parent_width - self.item_width)/2, (self.parent_height - self.item_height)/2)
        self.text.setPos((self.graphics_scene.width() - self.text.boundingRect().width()) / 2, TEXT_YLOC)
        # Call the callback instead of directly toggling
        if self.on_toggle_callback:
            self.on_toggle_callback()
        else:
            self.toggle()  # Fallback to old behavior if no callback
        # super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None: 
        pass

    def toggle(self):
        cartridge = None

        if self.enabled:
            # Use cached ICON_OFF
            if ICON_OFF not in Overlay._cartridge_cache:
                Overlay._cartridge_cache[ICON_OFF] = QPixmap(ICON_OFF).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            cartridge = Overlay._cartridge_cache[ICON_OFF]
            
            preview = QPixmap(self.image_path).scaled(cartridge.width() - 4, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            # preview = convert_to_grayscale(preview)  # Optimization: removed expensive grayscale conversion
            self.play_audio("assets/sounds/deselect.wav")
            self.enabled = False
        else:
            # Use cached ICON_ON
            if ICON_ON not in Overlay._cartridge_cache:
                Overlay._cartridge_cache[ICON_ON] = QPixmap(ICON_ON).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            cartridge = Overlay._cartridge_cache[ICON_ON]
            
            preview = QPixmap(self.image_path).scaled(cartridge.width() - 4, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.play_audio("assets/sounds/select.wav")
            self.enabled = True
        
        self.cartridge_item.setPixmap(cartridge)
        self.preview_item.setPixmap(preview)
    
    def set_enabled(self, enabled:bool):
        """Set enabled state without calling callback (used when syncing from external changes)"""
        if self.enabled == enabled:
            return  # Already in the correct state
        
        # Update visual state without playing sound or triggering callback
        cartridge = None
        if enabled:
            if ICON_ON not in Overlay._cartridge_cache:
                Overlay._cartridge_cache[ICON_ON] = QPixmap(ICON_ON).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            cartridge = Overlay._cartridge_cache[ICON_ON]
            self.enabled = True
        else:
            if ICON_OFF not in Overlay._cartridge_cache:
                Overlay._cartridge_cache[ICON_OFF] = QPixmap(ICON_OFF).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            cartridge = Overlay._cartridge_cache[ICON_OFF]
            self.enabled = False
        
        preview = QPixmap(self.image_path).scaled(cartridge.width() - 4, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.cartridge_item.setPixmap(cartridge)
        self.preview_item.setPixmap(preview)

    # def move(self, value:float):
    #     print(value)


    def play_audio(self, path:str):
        audio_file = QUrl.fromLocalFile(path)
        self.player.setSource(audio_file)
        self.player.play()

    def update_image(self, image_path: str):
        """Update the preview image dynamically"""
        self.image_path = image_path
        
        # Determine current cartridge based on state
        cartridge = None
        if self.enabled:
             if ICON_ON not in Overlay._cartridge_cache:
                 Overlay._cartridge_cache[ICON_ON] = QPixmap(ICON_ON).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
             cartridge = Overlay._cartridge_cache[ICON_ON]
        else:
             if ICON_OFF not in Overlay._cartridge_cache:
                 Overlay._cartridge_cache[ICON_OFF] = QPixmap(ICON_OFF).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
             cartridge = Overlay._cartridge_cache[ICON_OFF]
        
        # Determine center pos
        self.parent_width = cartridge.width()
        self.parent_height = cartridge.height() # Should be roughly SIZE
        
        if image_path and os.path.exists(image_path):
            preview = QPixmap(image_path)
            preview = preview.scaled(cartridge.width() - 4, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.item_width = preview.width()
            self.item_height = preview.height()
            self.preview_item.setPixmap(preview)
            
            # Re-center
            self.preview_item.setPos((self.parent_width - self.item_width)/2, (self.parent_height - self.item_height)/2)
