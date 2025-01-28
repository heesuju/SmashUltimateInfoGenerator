from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QImage, QColor, QFont

def add_text_to_image(pixmap: QPixmap, text:str, padding:tuple[int, int, int, int]=(0, 0, 0, 0), size:int=20)->QPixmap:
    """ Draws text inside an image and returns it as a QIcon. """
    painter = QPainter(pixmap)
    painter.setFont(QFont("Arial", size, QFont.Weight.ExtraBold))
    painter.setPen(Qt.GlobalColor.white)  # Text color

    # Center the text within the icon
    xp1, yp1, xp2, yp2 = padding
    rect = pixmap.rect().adjusted(xp1, yp1, xp2, yp2)  # Move text up by 10px
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    painter.end()
    return pixmap

def create_image_overlay(base_pixmap: QPixmap, alpha_pixmap: QPixmap) -> QPixmap:
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
