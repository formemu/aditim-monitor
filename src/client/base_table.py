"""
Базовый класс для работы с таблицами QTableWidget.

Предоставляет унифицированные методы для заполнения, очистки и настройки таблиц.
"""

from typing import List, Dict, Any, Optional, Callable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class BaseTable:
    """
    Базовый класс для работы с QTableWidget.
    
    Централизует общую логику работы с таблицами:
    - Настройка заголовков
    - Заполнение строк
    - Установка UserRole данных
    - Очистка таблиц
    """

    @staticmethod
    def setup_table(
        table: QTableWidget,
        list_header: List[str],
        count_row: int = 0,
        is_stretch_last: bool = True
    ) -> None:
        """
        Настройка структуры таблицы.

        Args:
            table: Виджет таблицы
            list_header: Список заголовков колонок
            count_row: Количество строк (по умолчанию 0)
            is_stretch_last: Растягивать последнюю колонку (по умолчанию True)

        Example:
            BaseTable.setup_table(
                self.ui.tableWidget_profile,
                ["Артикул", "Описание"],
                count_row=10
            )
        """
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QHeaderView
        
        table.setColumnCount(len(list_header))
        table.setHorizontalHeaderLabels(list_header)
        table.setRowCount(count_row)
        
        # Увеличиваем шрифт таблицы
        font = table.font()
        font.setPointSize(12)
        table.setFont(font)
        
        # Увеличиваем шрифт заголовков
        header_font = table.horizontalHeader().font()
        header_font.setPointSize(12)
        header_font.setBold(True)
        table.horizontalHeader().setFont(header_font)
        
        # Добавляем отступы между ячейками
        table.setStyleSheet("""
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        # Настройка ширины колонок
        header = table.horizontalHeader()
        
        # Все колонки кроме последней - по содержимому
        for i in range(len(list_header) - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Последняя колонка растягивается до конца
        if is_stretch_last:
            header.setSectionResizeMode(len(list_header) - 1, QHeaderView.Stretch)
        else:
            header.setSectionResizeMode(len(list_header) - 1, QHeaderView.ResizeToContents)

    @staticmethod
    def populate_row(
        table: QTableWidget,
        index_row: int,
        list_value: List[str],
        data_id: Optional[Any] = None
    ) -> None:
        """
        Заполнение одной строки таблицы.

        Args:
            table: Виджет таблицы
            index_row: Индекс строки
            list_value: Список значений для колонок
            data_id: ID для сохранения в Qt.UserRole (опционально)

        Example:
            BaseTable.populate_row(
                self.ui.tableWidget_profile,
                0,
                ["П-001", "Профиль алюминиевый"],
                data_id=42
            )
        """
        for index_col, value in enumerate(list_value):
            item = QTableWidgetItem(str(value))
            
            if data_id is not None:
                item.setData(Qt.UserRole, data_id)
            
            table.setItem(index_row, index_col, item)

    @staticmethod
    def populate_table(
        table: QTableWidget,
        list_header: List[str],
        list_data: List[Dict[str, Any]],
        func_row_mapper: Callable[[Dict[str, Any]], List[str]],
        func_id_getter: Optional[Callable[[Dict[str, Any]], Any]] = None,
        is_stretch_last: bool = True
    ) -> None:
        """
        Полное заполнение таблицы данными.

        Args:
            table: Виджет таблицы
            list_header: Список заголовков колонок
            list_data: Список словарей с данными
            func_row_mapper: Функция преобразования dict -> list значений для строки
            func_id_getter: Функция получения ID из dict (опционально)
            is_stretch_last: Растягивать последнюю колонку (по умолчанию True)

        Example:
            BaseTable.populate_table(
                self.ui.tableWidget_profile,
                ["Артикул", "Описание"],
                api_manager.table["profile"],
                func_row_mapper=lambda p: [p['article'], p['description']],
                func_id_getter=lambda p: p['id']
            )
        """
        BaseTable.setup_table(table, list_header, len(list_data), is_stretch_last)
        
        for index_row, data_row in enumerate(list_data):
            list_value = func_row_mapper(data_row)
            data_id = func_id_getter(data_row) if func_id_getter else None
            BaseTable.populate_row(table, index_row, list_value, data_id)

    @staticmethod
    def clear_table(table: QTableWidget, count_col: Optional[int] = None) -> None:
        """
        Очистка таблицы.

        Args:
            table: Виджет таблицы
            count_col: Количество колонок (если None, сохраняется текущее)

        Example:
            BaseTable.clear_table(self.ui.tableWidget_profile)
        """
        table.setRowCount(0)
        if count_col is not None:
            table.setColumnCount(count_col)

    @staticmethod
    def get_selected_id(table: QTableWidget) -> Optional[Any]:
        """
        Получение ID выбранной строки из Qt.UserRole.

        Args:
            table: Виджет таблицы

        Returns:
            ID из UserRole или None, если ничего не выбрано

        Example:
            profile_id = BaseTable.get_selected_id(self.ui.tableWidget_profile)
        """
        item_current = table.currentItem()
        if item_current is None:
            return None
        return item_current.data(Qt.UserRole)

    @staticmethod
    def set_cell_value(
        table: QTableWidget,
        index_row: int,
        index_col: int,
        value: str,
        data_id: Optional[Any] = None
    ) -> None:
        """
        Установка значения в конкретную ячейку.

        Args:
            table: Виджет таблицы
            index_row: Индекс строки
            index_col: Индекс колонки
            value: Значение для ячейки
            data_id: ID для сохранения в Qt.UserRole (опционально)

        Example:
            BaseTable.set_cell_value(
                self.ui.tableWidget_profile,
                0, 1,
                "Новое описание",
                data_id=42
            )
        """
        item = QTableWidgetItem(str(value))
        
        if data_id is not None:
            item.setData(Qt.UserRole, data_id)
        
        table.setItem(index_row, index_col, item)
