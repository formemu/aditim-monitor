from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QMimeData
from PySide6.QtGui import QDrag, QPainter, QColor

class DraggableWidget(QWidget):
    """
    Виджет-обертка, позволяющий перетаскивать вложенный виджет.
    Обрабатывает события мыши для реализации drag-and-drop с визуальными эффектами.
    """

    def __init__(self, widget: QWidget, parent: QWidget = None):
        super().__init__(parent)
        self.widget = widget
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(widget)
        self.setAcceptDrops(True)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(widget.sizePolicy())
        widget.setSizePolicy(widget.sizePolicy())
        self.animation = None
        self.setCursor(Qt.ArrowCursor)  # Курсор всегда обычная стрелка

    def sizeHint(self):
        return self.widget.sizeHint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.position().toPoint()
            # Не меняем курсор
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if hasattr(self, '_drag_start_pos'):
                distance = (event.position().toPoint() - self._drag_start_pos).manhattanLength()
                if distance > 10:
                    drag = QDrag(self)
                    mime_data = QMimeData()
                    task_id = getattr(self.widget, 'task_id', None)
                    if task_id is not None:
                        mime_data.setText(str(task_id))
                        drag.setMimeData(mime_data)

                        pixmap = self.widget.grab()
                        transparent_pixmap = pixmap.copy()
                        painter = QPainter(transparent_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
                        painter.fillRect(transparent_pixmap.rect(), QColor(0, 0, 0, 128))
                        painter.end()

                        drag.setPixmap(transparent_pixmap)
                        drag.setHotSpot(event.position().toPoint())

                        opacity_effect = QGraphicsOpacityEffect()
                        opacity_effect.setOpacity(0.5)
                        self.widget.setGraphicsEffect(opacity_effect)

                        main_window = self.window()
                        if hasattr(main_window, 'timer'):
                            main_window.timer.stop()

                        result = drag.exec(Qt.MoveAction)

                        self.widget.setGraphicsEffect(None)
                        self.start_drop_animation()
                        if hasattr(main_window, 'timer'):
                            main_window.timer.start(10000)
                        del self._drag_start_pos

                        return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Не меняем курсор
        self.widget.setGraphicsEffect(None)
        if hasattr(self, '_drag_start_pos'):
            del self._drag_start_pos
        super().mouseReleaseEvent(event)

    def start_drop_animation(self):
        if self.animation and self.animation.state() == QAbstractAnimation.Running:
            self.animation.stop()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.5)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.on_animation_finished)
        self.animation.start()

    def on_animation_finished(self):
        main_window = self.window()
        if hasattr(main_window, 'refresh_tasks'):
            main_window.refresh_tasks()
