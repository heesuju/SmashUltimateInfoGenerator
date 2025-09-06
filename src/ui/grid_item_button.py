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
    def __init__(self, image_path:str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.enabled = False

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.graphics_scene = QGraphicsScene()
        self.setScene(self.graphics_scene)
        # self.setStyleSheet("QGraphicsView { border: none; padding: 0px; }")
        # self.setStyleSheet("background: transparent;")

        cartridge = QPixmap(ICON_OFF)
        cartridge = cartridge.scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

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

        self.text = QGraphicsSimpleTextItem('FIGHTER')
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
        self.toggle()
        # super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None: 
        pass

    def toggle(self):
        cartridge = None

        if self.enabled:
            cartridge = QPixmap(ICON_OFF).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            preview = QPixmap(self.image_path).scaled(cartridge.width() - 4, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            preview = convert_to_grayscale(preview)
            self.play_audio("assets/sounds/deselect.wav")
            self.enabled = False
        else:
            cartridge = QPixmap(ICON_ON).scaled(SIZE, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            preview = QPixmap(self.image_path).scaled(cartridge.width() - 4, SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.play_audio("assets/sounds/select.wav")
            self.enabled = True
        
        self.cartridge_item.setPixmap(cartridge)
        self.preview_item.setPixmap(preview)

    # def move(self, value:float):
    #     print(value)


    def play_audio(self, path:str):
        audio_file = QUrl.fromLocalFile(path)
        self.player.setSource(audio_file)
        self.player.play()