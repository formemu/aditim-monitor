from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from draggable_widget import DraggableWidget
from server_api import ServerAPI

class TasksContainer(QWidget):
    """
    Контейнер для отображения задач с поддержкой drag-and-drop.
    Управляет расположением и перемещением виджетов задач.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def showEvent(self, event):
        super().showEvent(event)

    def add_task_widget(self, task_widget):
        draggable = DraggableWidget(task_widget)
        self.layout.addWidget(draggable)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            pos = event.position().toPoint()
            insert_index = 0
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                widget = item.widget()
                widget_center = widget.geometry().center()
                if pos.y() < widget_center.y():
                    insert_index = i
                    break
                insert_index = i + 1
            self.animate_shift(insert_index)

    def animate_shift(self, insert_index):
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.setContentsMargins(0, 0, 0, 0)
        if insert_index < self.layout.count():
            item = self.layout.itemAt(insert_index)
            widget = item.widget()
            margin = widget.sizeHint().height() + self.layout.spacing()
            widget.setContentsMargins(0, margin, 0, 0)

    def reset_shift_animations(self):
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            anim = getattr(widget, '_shift_animation', None)
            if anim is not None:
                anim.stop()
            widget.setContentsMargins(0, 0, 0, 0)

    def dropEvent(self, event):
        if event.mimeData().hasText():
            task_id = event.mimeData().text()
            pos = event.position().toPoint()
            insert_index = 0
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                widget = item.widget()
                widget_center = widget.geometry().center()
                if pos.y() < widget_center.y():
                    insert_index = i
                    break
                insert_index = i + 1
            self.move_task_widget(task_id, insert_index)
            self.reset_shift_animations()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.reset_shift_animations()

    def move_task_widget(self, task_id_str, new_index):
        task_id = int(task_id_str)
        current_index = -1
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget.widget.task_id == task_id:
                current_index = i
                break
        if current_index == -1 or current_index == new_index:
            return
        # Корректировка индекса при перемещении вниз
        if new_index > current_index:
            new_index -= 1
        item = self.layout.takeAt(current_index)
        widget = item.widget()
        self.layout.insertWidget(new_index, widget)
        self.update_positions_on_server()

    def update_positions_on_server(self):
        positions = []
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            task_id = widget.widget.task_id
            positions.append({"id": task_id, "position": i})
        resp = ServerAPI.update_positions(positions)
        if resp.status_code == 200:
            print("Позиции успешно обновлены на сервере")
        else:
            print(f"Ошибка обновления позиций: {resp.status_code} {resp.text}")
