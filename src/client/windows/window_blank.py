"""Окно управления заготовками для ADITIM Monitor Client"""
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView, QMenu, QDialog, QMessageBox
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtUiTools import QUiLoader
from ..constant import UI_PATHS_ABS, ICON_PATHS_ABS, get_style_path
from ..style_util import load_styles
from ..api_manager import api_manager
from ..widgets.dialog_create_blank import DialogCreateBlank


class WindowBlank(QWidget):
    """Виджет управления заготовками"""
    
    def __init__(self):
        super().__init__()
        self.selected_order = None  # Выбранный заказ
        self.dict_expanded_order = {}  # Словарь развернутых заказов {order_num: True/False}
        self.load_ui()
        self.setup_ui()
        api_manager.data_updated.connect(self.refresh_data)
    
    # =============================================================================
    # ИНИЦИАЛИЗАЦИЯ И ЗАГРУЗКА ИНТЕРФЕЙСА
    # =============================================================================
    def load_ui(self):
        """Загрузка UI из файла"""
        ui_file = QFile(UI_PATHS_ABS["BLANK_CONTENT"])
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
    
    def setup_ui(self):
        """Настройка UI компонентов после загрузки"""
        self.ui.setStyleSheet(load_styles(get_style_path("MAIN")))
        self.load_logo()
        
        # Настройка таблицы заказов (вкладка "Заказы")
        table = self.ui.tableWidget_blank
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setFocusPolicy(Qt.NoFocus)
        table.customContextMenuRequested.connect(self.show_context_menu)
        table.itemClicked.connect(self.on_blank_clicked)
        
        # Настройка таблицы остатков (вкладка "Остатки")
        table_stock = self.ui.tableWidget_stock
        table_stock.setContextMenuPolicy(Qt.CustomContextMenu)
        table_stock.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_stock.setSelectionMode(QAbstractItemView.SingleSelection)
        table_stock.setFocusPolicy(Qt.NoFocus)
        
        # Подключение смены вкладок
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
        
        # Подключение кнопок
        self.ui.pushButton_blank_add.clicked.connect(self.on_blank_add_clicked)
        self.ui.pushButton_blank_edit.clicked.connect(self.on_blank_edit_clicked)
        self.ui.pushButton_blank_delete.clicked.connect(self.on_blank_delete_clicked)
        
        self.refresh_data()
    
    def load_logo(self):
        """Загрузка логотипа ADITIM"""
        logo_path = ICON_PATHS_ABS.get("ADITIM_LOGO_MAIN")
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_logo.setPixmap(scaled)
        self.ui.label_logo.setText("")
    
    # =============================================================================
    # УПРАВЛЕНИЕ ДАННЫМИ: ЗАГРУЗКА И ОБНОВЛЕНИЕ
    # =============================================================================
    def refresh_data(self):
        """Обновление данных в окне заготовок"""
        self.selected_order = None
        current_tab = self.ui.tabWidget.currentIndex()
        if current_tab == 0:  # Вкладка "Заказы"
            self.update_table_blank()
        elif current_tab == 1:  # Вкладка "Остатки"
            self.update_table_stock()
    
    def update_table_blank(self):
        """Обновление таблицы заказов (агрегированные данные с раскрывающимися группами)"""
        table = self.ui.tableWidget_blank
        list_blank = api_manager.table.get('blank', [])
        
        # Группировка заготовок по номеру заказа и агрегация данных
        dict_order_data = {}
        for blank in list_blank:
            order_num = blank.get('order', 0)
            if order_num not in dict_order_data:
                dict_order_data[order_num] = {
                    'order': order_num,
                    'material_set': set(),
                    'size_set': set(),
                    'date_order': blank.get('date_order'),
                    'date_arrival': blank.get('date_arrival'),
                    'count_total': 0,
                    'count_arrived': 0,
                    'list_blank_id': [],
                    'dict_group': {}  # Группы по материалу+размеру
                }
            
            order_data = dict_order_data[order_num]
            
            # Материал
            material = blank.get('material')
            material_name = material['name'] if material else 'Не указан'
            order_data['material_set'].add(material_name)
            
            # Размер
            width = blank.get('blank_width')
            height = blank.get('blank_height')
            length = blank.get('blank_length')
            size = f"{width or '—'}×{height or '—'}×{length or '—'}"
            order_data['size_set'].add(size)
            
            # Группировка по материалу+размеру
            group_key = f"{material_name} | {size}"
            if group_key not in order_data['dict_group']:
                order_data['dict_group'][group_key] = {
                    'material': material_name,
                    'size': size,
                    'count_total': 0,
                    'count_arrived': 0,
                    'list_blank_id': []
                }
            
            group = order_data['dict_group'][group_key]
            group['count_total'] += 1
            group['list_blank_id'].append(blank['id'])
            
            if blank.get('date_arrival'):
                group['count_arrived'] += 1
            
            # Количество для заказа
            order_data['count_total'] += 1
            if blank.get('date_arrival'):
                order_data['count_arrived'] += 1
            
            # Дата прибытия (берем последнюю непустую)
            if blank.get('date_arrival') and not order_data['date_arrival']:
                order_data['date_arrival'] = blank.get('date_arrival')
            
            # Список ID заготовок
            order_data['list_blank_id'].append(blank['id'])
        
        # Сортировка заказов по убыванию номера
        list_sorted_order = sorted(dict_order_data.keys(), reverse=True)
        
        # Подсчет строк с учетом развернутых заказов
        total_row = 0
        for order_num in list_sorted_order:
            total_row += 1  # Строка заказа
            if self.dict_expanded_order.get(order_num, False):
                total_row += len(dict_order_data[order_num]['dict_group'])  # Строки групп
        
        table.setRowCount(total_row)
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Заказ №", "Материал", "Размер", "Заказано", "Прибыло", "Количество"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        
        current_row = 0
        for order_num in list_sorted_order:
            order_data = dict_order_data[order_num]
            is_expanded = self.dict_expanded_order.get(order_num, False)
            
            # Строка заказа (заголовок)
            arrow = "▼" if is_expanded else "▶"
            order_text = f"{arrow} Заказ № {order_num if order_num else '—'}"
            item_order = QTableWidgetItem(order_text)
            item_order.setData(Qt.UserRole, {'type': 'order_header', 'order_data': order_data})
            
            # Стиль для заголовка
            from PySide6.QtGui import QFont, QColor
            font = QFont()
            font.setBold(True)
            item_order.setFont(font)
            item_order.setBackground(QColor("#E3F2FD"))
            
            # Материал (сводка)
            material_text = ', '.join(sorted(order_data['material_set'])) if order_data['material_set'] else '—'
            item_material = QTableWidgetItem(material_text)
            item_material.setData(Qt.UserRole, {'type': 'order_header', 'order_data': order_data})
            item_material.setFont(font)
            item_material.setBackground(QColor("#E3F2FD"))
            
            # Размер (сводка)
            size_text = ', '.join(sorted(order_data['size_set'])) if order_data['size_set'] else '—'
            item_size = QTableWidgetItem(size_text)
            item_size.setData(Qt.UserRole, {'type': 'order_header', 'order_data': order_data})
            item_size.setFont(font)
            item_size.setBackground(QColor("#E3F2FD"))
            
            # Дата заказа
            item_date_order = QTableWidgetItem(order_data['date_order'] or '—')
            item_date_order.setData(Qt.UserRole, {'type': 'order_header', 'order_data': order_data})
            item_date_order.setFont(font)
            item_date_order.setBackground(QColor("#E3F2FD"))
            
            # Дата прибытия
            item_date_arrival = QTableWidgetItem(order_data['date_arrival'] or '—')
            item_date_arrival.setData(Qt.UserRole, {'type': 'order_header', 'order_data': order_data})
            item_date_arrival.setFont(font)
            item_date_arrival.setBackground(QColor("#E3F2FD"))
            
            # Количество (только общее)
            quantity_text = str(order_data['count_total'])
            item_quantity = QTableWidgetItem(quantity_text)
            item_quantity.setData(Qt.UserRole, {'type': 'order_header', 'order_data': order_data})
            item_quantity.setFont(font)
            item_quantity.setBackground(QColor("#E3F2FD"))
            
            table.setItem(current_row, 0, item_order)
            table.setItem(current_row, 1, item_material)
            table.setItem(current_row, 2, item_size)
            table.setItem(current_row, 3, item_date_order)
            table.setItem(current_row, 4, item_date_arrival)
            table.setItem(current_row, 5, item_quantity)
            current_row += 1
            
            # Детализированные группы (если заказ развернут)
            if is_expanded:
                for group_key in sorted(order_data['dict_group'].keys()):
                    group = order_data['dict_group'][group_key]
                    
                    # Пустая колонка для отступа
                    item_empty = QTableWidgetItem("")
                    item_empty.setData(Qt.UserRole, {'type': 'group', 'group_data': group, 'order_data': order_data})
                    
                    # Материал группы
                    item_group_material = QTableWidgetItem(f"  {group['material']}")
                    item_group_material.setData(Qt.UserRole, {'type': 'group', 'group_data': group, 'order_data': order_data})
                    
                    # Размер группы
                    item_group_size = QTableWidgetItem(group['size'])
                    item_group_size.setData(Qt.UserRole, {'type': 'group', 'group_data': group, 'order_data': order_data})
                    
                    # Пустые ячейки для дат
                    item_empty2 = QTableWidgetItem("")
                    item_empty2.setData(Qt.UserRole, {'type': 'group', 'group_data': group, 'order_data': order_data})
                    
                    item_empty3 = QTableWidgetItem("")
                    item_empty3.setData(Qt.UserRole, {'type': 'group', 'group_data': group, 'order_data': order_data})
                    
                    # Количество группы (только общее)
                    group_quantity = str(group['count_total'])
                    item_group_quantity = QTableWidgetItem(group_quantity)
                    item_group_quantity.setData(Qt.UserRole, {'type': 'group', 'group_data': group, 'order_data': order_data})
                    
                    table.setItem(current_row, 0, item_empty)
                    table.setItem(current_row, 1, item_group_material)
                    table.setItem(current_row, 2, item_group_size)
                    table.setItem(current_row, 3, item_empty2)
                    table.setItem(current_row, 4, item_empty3)
                    table.setItem(current_row, 5, item_group_quantity)
                    current_row += 1
    
    def update_table_stock(self):
        """Обновление таблицы остатков заготовок"""
        table = self.ui.tableWidget_stock
        list_blank = api_manager.table.get('blank', [])
        
        # Группировка заготовок по материалу и размеру
        dict_stock = {}
        for blank in list_blank:
            # Пропускаем заготовки, которые еще не прибыли
            if not blank.get('date_arrival'):
                continue
            
            # Материал
            material = blank.get('material')
            material_name = material['name'] if material else 'Не указан'
            
            # Размер
            width = blank.get('blank_width')
            height = blank.get('blank_height')
            length = blank.get('blank_length')
            size = f"{width or '—'}×{height or '—'}×{length or '—'}"
            
            # Ключ группировки
            key = f"{material_name}|{size}"
            
            if key not in dict_stock:
                dict_stock[key] = {
                    'material': material_name,
                    'size': size,
                    'total': 0,      # Всего в наличии (прибыли)
                    'free': 0        # Свободные (не обработаны)
                }
            
            stock = dict_stock[key]
            stock['total'] += 1
            
            # Проверяем, свободна ли заготовка (нет date_product)
            if not blank.get('date_product'):
                stock['free'] += 1
        
        # Сортировка по материалу, затем по размеру
        list_sorted_keys = sorted(dict_stock.keys())
        
        table.setRowCount(len(list_sorted_keys))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Материал", "Размер", "В наличии", "Свободные"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        
        for row, key in enumerate(list_sorted_keys):
            stock = dict_stock[key]
            
            # Материал
            item_material = QTableWidgetItem(stock['material'])
            
            # Размер
            item_size = QTableWidgetItem(stock['size'])
            
            # В наличии (прибыли)
            item_total = QTableWidgetItem(str(stock['total']))
            
            # Свободные (не обработаны)
            item_free = QTableWidgetItem(str(stock['free']))
            
            table.setItem(row, 0, item_material)
            table.setItem(row, 1, item_size)
            table.setItem(row, 2, item_total)
            table.setItem(row, 3, item_free)
    

    
    # =============================================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # =============================================================================
    def on_tab_changed(self, index):
        """Обработчик смены вкладки"""
        if index == 0:  # Вкладка "Заказы"
            self.update_table_blank()
        elif index == 1:  # Вкладка "Остатки"
            self.update_table_stock()
    
    def on_blank_clicked(self, item):
        """Обработка клика по элементу таблицы (раскрытие или выбор)"""
        user_data = item.data(Qt.UserRole)
        if not user_data:
            return
        
        # Если клик по заголовку заказа - переключаем раскрытие
        if user_data.get('type') == 'order_header':
            order_data = user_data.get('order_data')
            order_num = order_data['order']
            
            # Переключаем состояние
            self.dict_expanded_order[order_num] = not self.dict_expanded_order.get(order_num, False)
            
            # Перерисовываем таблицу
            self.update_table_blank()
            return
        
        # Если клик по группе - выбираем заказ
        if user_data.get('type') == 'group':
            order_data = user_data.get('order_data')
            self.selected_order = order_data
            return
 
   
    def on_blank_add_clicked(self):
        """Добавление новой заготовки"""
        dialog = DialogCreateBlank(self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Успех", "Заготовка успешно создана")
            self.refresh_data()
    
    def on_blank_edit_clicked(self):
        """Редактирование заказа"""
        if not self.selected_order:
            QMessageBox.warning(self, "Внимание", "Выберите заказ для редактирования")
            return
        # TODO: Создать диалог редактирования заказа
        QMessageBox.information(self, "Информация", "Функция редактирования заказа в разработке")
    
    def on_blank_delete_clicked(self):
        """Удаление заказа (всех заготовок)"""
        if not self.selected_order:
            QMessageBox.warning(self, "Внимание", "Выберите заказ для удаления")
            return
        
        order_num = self.selected_order['order']
        count = self.selected_order['count_total']
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить заказ № {order_num} ({count} шт.)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Удаление всех заготовок заказа
            for blank_id in self.selected_order['list_blank_id']:
                api_manager.api_blank.delete_blank(blank_id)
            
            QMessageBox.information(self, "Успех", f"Заказ № {order_num} удален")
            self.refresh_data()
    
    def show_context_menu(self, pos):
        """Показать контекстное меню для заказа"""
        if not self.selected_order:
            return
        
        table = self.ui.tableWidget_blank
        menu = QMenu(table)
        
        # Действие "Плита прибыла" - устанавливает дату прибытия для всех заготовок заказа
        action_arrived = QAction("Плита прибыла", menu)
        action_arrived.triggered.connect(self.on_blank_arrived)
        
        # Действия меню
        action_edit = QAction("Редактировать", menu)
        action_edit.triggered.connect(self.on_blank_edit_clicked)
        
        action_delete = QAction("Удалить заказ", menu)
        action_delete.triggered.connect(self.on_blank_delete_clicked)
        
        menu.addAction(action_arrived)
        menu.addSeparator()
        menu.addAction(action_edit)
        menu.addAction(action_delete)
        
        menu.exec(table.viewport().mapToGlobal(pos))
    
    def on_blank_arrived(self):
        """Отметить, что плиты прибыли (установить дату прибытия для всех заготовок заказа)"""
        if not self.selected_order:
            return
        
        from PySide6.QtCore import QDate
        
        order_num = self.selected_order['order']
        count = self.selected_order['count_total']
        
        # Проверяем, не установлена ли уже дата прибытия
        if self.selected_order.get('date_arrival'):
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Дата прибытия заказа № {order_num} уже установлена: {self.selected_order['date_arrival']}\nИзменить на текущую дату?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Устанавливаем текущую дату как дату прибытия для всех заготовок заказа
        blank_data = {
            "date_arrival": QDate.currentDate().toString("yyyy-MM-dd")
        }
        
        for blank_id in self.selected_order['list_blank_id']:
            api_manager.api_blank.update_blank(blank_id, blank_data)
        
        QMessageBox.information(self, "Успех", f"Дата прибытия установлена для заказа № {order_num} ({count} шт.)")
        self.refresh_data()
