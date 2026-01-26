import os
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, 
                             QGraphicsSimpleTextItem, QGraphicsPixmapItem,
                             QGraphicsDropShadowEffect, QGraphicsRectItem, QGraphicsItem)
from PyQt6.QtGui import QPixmap, QFont, QBrush, QColor, QImage, QPainterPath, QPen

from PyQt6.QtCore import Qt, QPointF, QUrl
from PyQt6.QtCore import QVariantAnimation
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Category icon paths
CATEGORY_ICON_PATH = "assets/icons/categories/{}.png"
CATEGORY_ICON_BACK_PATH = "assets/icons/categories/{}_b.png"

SIZE = 70
THUMBNAIL_TOP_OFFSET = 20
THUMBNAIL_SIDE_OFFSET = 6
THUMBNAIL_BOTTOM_OFFSET = 20
TEXT_YLOC = 12.5
FONT = "Arial"
FONT_SIZE = 6
PRESS_AMOUNT = 5

# Glow color for enabled state
ENABLED_GLOW_COLOR = QColor(0, 200, 100, 200)  # Green glow
ENABLED_GLOW_RADIUS = 20


def convert_to_grayscale(pixmap:QPixmap):
    image = pixmap.toImage()
    grayscale_image = image.convertToFormat(QImage.Format.Format_Grayscale8)
    return QPixmap.fromImage(grayscale_image)


class Overlay(QGraphicsView):
    # Static cache for category icons to avoid repeated loading/scaling
    _icon_cache = {}
    _hover_icon_cache = {}

    def __init__(self, image_path:str, parent=None, initial_enabled=False, on_toggle_callback=None, category:str="Fighter", has_thumbnail:bool=True, overlay_mode="toggle", hover_icon=None):
        super().__init__(parent)
        self.image_path = image_path
        self.enabled = initial_enabled
        self.on_toggle_callback = on_toggle_callback
        self.category = category.lower()  # Normalize to lowercase for file paths
        self.has_thumbnail = has_thumbnail
        self.overlay_mode = overlay_mode
        self.hover_icon = hover_icon
        self.hover_item_graphics = None

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene = QGraphicsScene()
        self.setScene(self.graphics_scene)

        # Load category icon based on whether thumbnail exists
        category_icon = self._get_category_icon()

        # Create glow backing item
        self.glow_item = QGraphicsPixmapItem(category_icon)
        self.graphics_scene.addItem(self.glow_item)

        # Create a clipping item for the thumbnail
        self.thumbnail_clip_item = QGraphicsRectItem()
        self.thumbnail_clip_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
        self.thumbnail_clip_item.setPen(QPen(Qt.PenStyle.NoPen)) 
        

        # We want to clip left, right, bottom, and start from an offset at top.
        rect_width = category_icon.width() - (2 * THUMBNAIL_SIDE_OFFSET)
        rect_height = SIZE - THUMBNAIL_TOP_OFFSET - THUMBNAIL_BOTTOM_OFFSET
        self.thumbnail_clip_item.setRect(0, 0, rect_width, rect_height) 
        
        # Position clip item: Centered horizontally, offset vertically
        self.thumbnail_clip_item.setPos(THUMBNAIL_SIDE_OFFSET, THUMBNAIL_TOP_OFFSET) 
        
        self.graphics_scene.addItem(self.thumbnail_clip_item)

        preview = QPixmap(image_path)
        
        # This ensures we fit width layout UNLESS height is too small
        virtual_height = SIZE - THUMBNAIL_TOP_OFFSET - THUMBNAIL_BOTTOM_OFFSET
        target_size = QSize(int(rect_width), int(virtual_height))
        preview = preview.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        self.preview_item = QGraphicsPixmapItem(preview)
        self.preview_item.setParentItem(self.thumbnail_clip_item)
        
        # Darkening overlay (initially transparent)
        if self.hover_icon:
            self.darken_item = QGraphicsRectItem(self.thumbnail_clip_item.rect())
            self.darken_item.setParentItem(self.thumbnail_clip_item)
            self.darken_item.setBrush(QBrush(QColor("black")))
            self.darken_item.setPen(QPen(Qt.PenStyle.NoPen))
            self.darken_item.setOpacity(0.0)
        
        # Center preview in clip item
        self.category_icon_item = QGraphicsPixmapItem(category_icon)
        self.graphics_scene.addItem(self.category_icon_item)
        self.setSceneRect(self.category_icon_item.sceneBoundingRect())
        
        self.parent_width = category_icon.width()
        self.parent_height = category_icon.height()
        self.item_width = preview.width()
        self.item_height = preview.height()
        
        # Position relative to VIRTUAL rect
        # X is centered, Y is 0 (Top Aligned)
        self.preview_item.setPos((rect_width - self.item_width)/2, 0)
        
        # Determine category text from parent
        cat_text = category.upper()

        self.text = QGraphicsSimpleTextItem(cat_text)
        font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        font.setBold(True)
        self.text.setFont(font)
        self.text.setBrush(QBrush(QColor("white")))  # Set the font color
        self.graphics_scene.addItem(self.text)
        self.text.setPos((self.parent_width - self.text.boundingRect().width()) / 2, TEXT_YLOC)

        # Setup Hover Icon if provided
        if self.hover_icon:
            pix = None
            icon_size = 24
            
            if isinstance(self.hover_icon, str):
                if self.hover_icon in Overlay._hover_icon_cache:
                    pix = Overlay._hover_icon_cache[self.hover_icon]
                else:
                    pix = QPixmap(self.hover_icon)
                    pix = pix.scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    Overlay._hover_icon_cache[self.hover_icon] = pix
            else:
                pix = self.hover_icon
                pix = pix.scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.hover_item_graphics = QGraphicsPixmapItem(pix)
            self.hover_item_graphics.setZValue(100) # Ensure it's on top
            self.hover_item_graphics.setVisible(False)
            
            icon_x = (self.parent_width - pix.width()) / 2
            icon_y = (self.parent_height - pix.height()) / 2
            
            self.hover_item_graphics.setPos(icon_x, icon_y)
            self.graphics_scene.addItem(self.hover_item_graphics)

        # Apply initial enabled state shadow
        self._update_enabled_shadow()

    def _get_category_icon(self) -> QPixmap:
        """Get the appropriate category icon based on has_thumbnail flag"""
        if self.has_thumbnail:
            icon_path = CATEGORY_ICON_PATH.format(self.category)
        else:
            icon_path = CATEGORY_ICON_BACK_PATH.format(self.category)
        
        # Check cache first
        if icon_path not in Overlay._icon_cache:
            pix = QPixmap(icon_path)
            if pix.isNull():
                # Fallback to fighter icon if specific category not found
                fallback_path = CATEGORY_ICON_PATH.format("fighter") if self.has_thumbnail else CATEGORY_ICON_BACK_PATH.format("fighter")
                pix = QPixmap(fallback_path)
            pix = pix.scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            Overlay._icon_cache[icon_path] = pix
        
        return Overlay._icon_cache[icon_path]

    def _update_enabled_shadow(self):
        """Update the shadow/glow effect based on enabled state"""
        if self.enabled:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(ENABLED_GLOW_RADIUS)
            shadow.setOffset(0, 0)
            shadow.setColor(ENABLED_GLOW_COLOR)

            # APPLY TO THE GLOW ITEM
            self.glow_item.setGraphicsEffect(shadow)
        else:
            self.glow_item.setGraphicsEffect(None)
    
    def mousePressEvent(self, event):
        self.glow_item.setPos(0, PRESS_AMOUNT)
        self.category_icon_item.setPos(0, PRESS_AMOUNT)
        self.thumbnail_clip_item.setPos(THUMBNAIL_SIDE_OFFSET, THUMBNAIL_TOP_OFFSET + PRESS_AMOUNT)
        self.text.setPos((self.parent_width - self.text.boundingRect().width()) / 2, TEXT_YLOC + PRESS_AMOUNT)
        if self.hover_item_graphics:
            x = self.hover_item_graphics.x()
            y = self.hover_item_graphics.y()
            self.hover_item_graphics.setPos(x, y + PRESS_AMOUNT)

    def mouseReleaseEvent(self, event):
        self.glow_item.setPos(0, 0)
        self.category_icon_item.setPos(0, 0)
        self.thumbnail_clip_item.setPos(THUMBNAIL_SIDE_OFFSET, THUMBNAIL_TOP_OFFSET)
        self.text.setPos((self.parent_width - self.text.boundingRect().width()) / 2, TEXT_YLOC)
        if self.hover_item_graphics:
            x = self.hover_item_graphics.x()
            y = self.hover_item_graphics.y()
            self.hover_item_graphics.setPos(x, y - PRESS_AMOUNT)

        if self.on_toggle_callback:
            if self.overlay_mode == "action":
                self.play_audio("assets/sounds/select.wav")
                self.on_toggle_callback()
                return

            if self.enabled:
                self.play_audio("assets/sounds/deselect.wav")
            else:
                self.play_audio("assets/sounds/select.wav")
            self.on_toggle_callback()
        else:
            self.toggle()  # Fallback to old behavior if no callback

    def enterEvent(self, event):
        if self.hover_item_graphics:
            self.hover_item_graphics.setVisible(True)
            self.darken_item.setOpacity(0.5)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.hover_item_graphics:
            self.hover_item_graphics.setVisible(False)
            self.darken_item.setOpacity(0.0)
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event) -> None: 
        pass

    def toggle(self):
        if self.enabled:
            self.play_audio("assets/sounds/deselect.wav")
            self.enabled = False
        else:
            self.play_audio("assets/sounds/select.wav")
            self.enabled = True
        
        # Update shadow effect for enabled state
        self._update_enabled_shadow()
        
        # Reload preview image
        category_icon = self._get_category_icon()
        
        # Calculate virtual target size
        rect_width = self.thumbnail_clip_item.rect().width()
        virtual_height = SIZE - THUMBNAIL_TOP_OFFSET - THUMBNAIL_BOTTOM_OFFSET
        target_size = QSize(int(rect_width), int(virtual_height))
        
        preview = QPixmap(self.image_path).scaled(target_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.preview_item.setPixmap(preview)
        
        # Center in virtual rect
        self.item_width = preview.width()
        self.item_height = preview.height()
        self.preview_item.setPos((rect_width - self.item_width)/2, 0)
    
    def set_enabled(self, enabled:bool):
        """Set enabled state without calling callback (used when syncing from external changes)"""
        if self.enabled == enabled:
            return  # Already in the correct state
        
        self.enabled = enabled
        self._update_enabled_shadow()
        
        # Reload preview image
        category_icon = self._get_category_icon()
        
        # Calculate virtual target size
        rect_width = self.thumbnail_clip_item.rect().width()
        virtual_height = SIZE - THUMBNAIL_TOP_OFFSET - THUMBNAIL_BOTTOM_OFFSET
        target_size = QSize(int(rect_width), int(virtual_height))
        
        preview = QPixmap(self.image_path).scaled(target_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.preview_item.setPixmap(preview)
        
        # Center in virtual rect
        self.item_width = preview.width()
        self.item_height = preview.height()
        self.preview_item.setPos((rect_width - self.item_width)/2, 0)

    def play_audio(self, path:str):
        audio_file = QUrl.fromLocalFile(path)
        self.player.setSource(audio_file)
        self.player.play()

    def update_image(self, image_path: str):
        """Update the preview image dynamically"""
        self.image_path = image_path
        
        # Update has_thumbnail based on new image
        self.has_thumbnail = image_path and os.path.exists(image_path) and os.path.isfile(image_path)
        
        category_icon = self._get_category_icon()
        
        # Determine center pos
        self.parent_width = category_icon.width()
        self.parent_height = category_icon.height()
        
        if image_path and os.path.exists(image_path):

            rect_width = category_icon.width() - (2 * THUMBNAIL_SIDE_OFFSET)
            rect_height = SIZE - THUMBNAIL_TOP_OFFSET - THUMBNAIL_BOTTOM_OFFSET
            self.thumbnail_clip_item.setRect(0, 0, rect_width, rect_height)
            self.thumbnail_clip_item.setPos(THUMBNAIL_SIDE_OFFSET, THUMBNAIL_TOP_OFFSET)
            
            if hasattr(self, 'darken_item'):
                 self.darken_item.setRect(0, 0, rect_width, rect_height)

            preview = QPixmap(image_path)
            # Virtual target size
            virtual_height = SIZE - THUMBNAIL_TOP_OFFSET - THUMBNAIL_BOTTOM_OFFSET
            target_size = QSize(int(rect_width), int(virtual_height))
            
            preview = preview.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.item_width = preview.width()
            self.item_height = preview.height()
            self.preview_item.setPixmap(preview)
            
            # Re-center in virtual rect
            self.preview_item.setPos((rect_width - self.item_width)/2, 0)
        
        self.category_icon_item.setPixmap(category_icon)
        self.glow_item.setPixmap(category_icon)
        self.setSceneRect(self.category_icon_item.sceneBoundingRect())
        
        # Update text position
        self.text.setPos((self.parent_width - self.text.boundingRect().width()) / 2, TEXT_YLOC)
