"""Мастер создания задачи"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt


from ...constant import UI_PATHS_ABS, ICON_PATHS_ABS, get_style_path
from ...api_manager import api_manager
from ...style_util import load_styles
from PySide6.QtWidgets import QWizard, QWizardPage, QComboBox, QLineEdit, QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QCheckBox, QLabel, QTextEdit, QDateEdit, QMessageBox
from PySide6.QtCore import QDate


class WizardTaskCreate(QWizard):
    """Мастер создания задачи"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Состояние
        self.profile = None
        self.profiletool = None
        self.product = None
        self.dict_selected_profiletool_component = []
        self.dict_selected_product_component = []
        self.load_ui()
        self.setup_ui()
    
    def load_ui(self):
        """Загружает UI через QUiLoader и экспортирует виджеты на self."""
        ui_file = QFile(UI_PATHS_ABS["WIZARD_TASK_CREATE"])
        if not ui_file.open(QFile.ReadOnly):
            return
        
        loader = QUiLoader()
        tmp_wizard = loader.load(ui_file)
        ui_file.close()
        
        if tmp_wizard is None:
            return
        
        # Копируем базовые свойства визарда
        self.setWindowTitle(tmp_wizard.windowTitle())
        self.setStyleSheet(tmp_wizard.styleSheet())
        
        # Переносим страницы из загруженного визарда в текущий
        for pid in tmp_wizard.pageIds():
            page = tmp_wizard.page(pid)
            if page is not None:
                self.addPage(page)
                # Экспортируем все виджеты со страницы на self для прямого доступа
                self._export_widgets_from_page(page)
        
        tmp_wizard.deleteLater()
    
    def _export_widgets_from_page(self, page: QWizardPage):
        """Экспортирует все дочерние виджеты страницы на self по objectName."""
        for widget in page.findChildren(QWidget):
            obj_name = widget.objectName()
            if obj_name and not obj_name.startswith("_"):
                setattr(self, obj_name, widget)


    def setup_ui(self):
        """Настраивает логику визарда."""
        # Сопоставляем id страницам по именам из UI
        self._page_id_by_name = {}
        for pid in self.pageIds():
            page = self.page(pid)
            if page is not None:
                self._page_id_by_name[page.objectName()] = pid

        # Виджеты уже экспортированы на self в load_ui через objectName, используем прямые имена

        # Сигналы поиска
        self.lineEdit_profile_search.textChanged.connect(self.on_search_profile)
        # Выбор по Enter: берём первый результат
        self.lineEdit_profile_search.returnPressed.connect(self.on_profile_enter)
        self.lineEdit_product_search.textChanged.connect(self.on_search_product)

        # Выбор из результатов
        self.listWidget_profile_search.itemSelectionChanged.connect(self.on_profile_selected)
        self.listWidget_profile_search.itemClicked.connect(lambda _item: self.on_profile_selected())
        self.comboBox_dimension.currentIndexChanged.connect(self.on_dimension_selected)
        self.listWidget_product_search.itemSelectionChanged.connect(self.on_product_selected)

        # Инициализация справочников
        self.fill_task_types()

        # Обновление страниц при смене
        self.currentIdChanged.connect(self.on_current_id_changed)

    def nextId(self):
        """Переопределяем маршрут переходов между страницами."""
        current_id = self.currentId()
        current_page = self.page(current_id)
        if current_page is None:
            return -1

        name = current_page.objectName()

        # Ветвление из стартовой страницы по выбору типа изделия
        if name == "wizardPage_start":
            # 0 — "Инструмент профиля", 1 — "Другое изделие"
            if self.comboBox_product_type.currentIndex() == 0:
                return self._page_id_by_name.get("wizardPage_profiletool_selection", -1)
            else:
                return self._page_id_by_name.get("wizardPage_product_selection", -1)

        # Ветвь Инструмент профиля: выбор инструмента -> выбор компонентов -> детали задачи
        if name == "wizardPage_profiletool_selection":
            return self._page_id_by_name.get("wizardPage_profiletool_component_selection", -1)
        if name == "wizardPage_profiletool_component_selection":
            return self._page_id_by_name.get("wizardPage_task_detail", -1)

        # Ветвь Другое изделие: выбор изделия -> выбор компонентов -> детали задачи
        if name == "wizardPage_product_selection":
            return self._page_id_by_name.get("wizardPage_product_component_selection", -1)
        if name == "wizardPage_product_component_selection":
            return self._page_id_by_name.get("wizardPage_task_detail", -1)

        # Финал
        return -1

    def validateCurrentPage(self) -> bool:
        """Валидация перед переходом на следующую страницу."""
        current_page = self.currentPage()
        if current_page is None:
            return False

        name = current_page.objectName()
        if name == "wizardPage_start":
            # Обязательно должен быть выбран тип изделия
            return self.comboBox_product_type.currentIndex() >= 0
        if name == "wizardPage_profiletool_selection":
            if self.profiletool is None:
                QMessageBox.warning(self, "Внимание", "Выберите профиль и типоразмер инструмента")
                return False
            return True
        if name == "wizardPage_profiletool_component_selection":
            self.dict_selected_profiletool_component = self.collect_selected_profiletool_components()
            return len(self.dict_selected_profiletool_component) > 0
        if name == "wizardPage_product_selection":
            if self.product is None:
                QMessageBox.warning(self, "Внимание", "Выберите изделие из списка")
                return False
            return True
        if name == "wizardPage_product_component_selection":
            self.dict_selected_product_component = self.collect_selected_product_components()
            return True

        return super().validateCurrentPage()

    # ---------- Служебные методы ----------
    def on_current_id_changed(self, pid: int):
        page = self.page(pid)
        if not page:
            return
        name = page.objectName()
        if name == "wizardPage_profiletool_selection":
            # Очистка и подготовка
            self.listWidget_profile_search.clear()
            self.comboBox_dimension.clear()
            self.profile = None
            self.profiletool = None
            # Кнопка Next заблокирована до выбора типоразмера
            btn = self.button(QWizard.NextButton)
            if btn:
                btn.setEnabled(False)
        elif name == "wizardPage_profiletool_component_selection":
            self.populate_profiletool_components()
        elif name == "wizardPage_product_selection":
            self.listWidget_product_search.clear()
            self.product = None
            btn = self.button(QWizard.NextButton)
            if btn:
                btn.setEnabled(False)
        elif name == "wizardPage_product_component_selection":
            self.populate_product_components()
        elif name == "wizardPage_task_detail":
            self.dateEdit_date.setDate(QDate.currentDate().addDays(7))

    def fill_task_types(self):
        self.comboBox_work_type.clear()
        types = api_manager.directory.get('task_type', [])
        for t in types:
            self.comboBox_work_type.addItem(t['name'], t['id'])

    # --- Поиск и выбор профиля / инструмента ---
    def on_search_profile(self, text: str):
        self.listWidget_profile_search.clear()
        if not text.strip():
            return
        results = api_manager.search_in('profile', 'article', text)[:10]
        for profile in results:
            item = QListWidgetItem(f"{profile['article']}")
            item.setData(Qt.UserRole, profile)
            self.listWidget_profile_search.addItem(item)

    def on_profile_selected(self):
        item = self.listWidget_profile_search.currentItem()
        if not item:
            return
        self.profile = item.data(Qt.UserRole)
        # Отобразим выбранный профиль в поле поиска
        self.lineEdit_profile_search.setText(f"{self.profile.get('article', '')}")
        # Заполнить типы работ из справочника уже сделано в fill_task_types
        # Заполнить доступные инструменты/типоразмеры
        self.comboBox_dimension.clear()
        for profiletool in self.profile.get('profiletool', []):
            name = profiletool['dimension']['name']
            self.comboBox_dimension.addItem(name, profiletool)
        # Если добавили элементы — выбираем первый по умолчанию
        if self.comboBox_dimension.count() > 0:
            self.comboBox_dimension.setCurrentIndex(0)
            # Явно устанавливаем profiletool, даже если сигнал не пришёл
            self.on_dimension_selected(0)

    def on_dimension_selected(self, index: int):
        if index < 0:
            self.profiletool = None
            return
        self.profiletool = self.comboBox_dimension.currentData()
        # Показать, что выбрано, прямо в строке поиска
        if self.profile:
            article = self.profile.get('article', '')
            dim = self.profiletool.get('dimension', {}).get('name', '') if self.profiletool else ''
            self.lineEdit_profile_search.setText(f"{article} / {dim}")
        # Сообщить визарду, что страница может стать «полной»
        page = self.page(self._page_id_by_name.get("wizardPage_profiletool_selection", -1))
        if isinstance(page, QWizardPage):
            page.completeChanged.emit()
        # Разблокировать Next
        btn = self.button(QWizard.NextButton)
        if btn:
            btn.setEnabled(True)

    def on_profile_enter(self):
        """Выбор первого результата по Enter, если список не пуст."""
        if self.listWidget_profile_search.count() > 0:
            self.listWidget_profile_search.setCurrentRow(0)
            self.on_profile_selected()

    # --- Компоненты инструмента ---
    def populate_profiletool_components(self):
        if not self.profiletool:
            return
        self.listWidget_profiletool_component.clear()
        self.clear_container(self.widget_profiletool_component_container)
        self._component_id_to_widget = {}
        components = self.profiletool.get('component', [])
        for comp in components:
            checkbox = QCheckBox(f"{comp['type']['name']}")
            checkbox.setProperty("component", comp)
            item = QListWidgetItem(self.listWidget_profiletool_component)
            self.listWidget_profiletool_component.setItemWidget(item, checkbox)
            checkbox.toggled.connect(lambda checked, c=comp, cb=checkbox: self.on_profiletool_component_toggled(checked, c, cb))

    def on_profiletool_component_toggled(self, checked: bool, component: dict, checkbox: QCheckBox):
        layout = self.ensure_hbox(self.widget_profiletool_component_container)
        if checked:
            widget = self.build_component_widget(component)
            self._component_id_to_widget[component['id']] = widget
            layout.addWidget(widget)
        else:
            widget = self._component_id_to_widget.pop(component['id'], None)
            if widget:
                layout.removeWidget(widget)
                widget.deleteLater()
        # Сортировка по type_id
        widgets = []
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w:
                widgets.append((w.property("type_id") or 0, w))
        widgets.sort(key=lambda x: x[0])
        for _, w in widgets:
            layout.removeWidget(w)
            layout.addWidget(w)

    def build_component_widget(self, component: dict) -> QWidget:
        widget = QWidget()
        v = QHBoxLayout()
        widget.setLayout(v)
        widget.setProperty("type_id", component['type']['id'])
        v.addWidget(QLabel(f"{component['type']['name']}"))
        # Этапы
        for stage in self.load_stages_for_component(component):
            sub = QHBoxLayout()
            cb = QCheckBox(f"{stage['stage_num']}. {stage['work_subtype']['name']}")
            cb.setProperty("stage", stage)
            sub.addWidget(cb)
            v.addLayout(sub)
        return widget

    def load_stages_for_component(self, component: dict):
        comp_type_id = component['type']['id']
        list_stage = []
        for stage in api_manager.plan.get('task_component_stage', []):
            if stage['profiletool_component_type']['id'] == comp_type_id:
                list_stage.append(stage)
        list_stage.sort(key=lambda s: s['stage_num'])
        return list_stage

    def collect_selected_profiletool_components(self):
        selected = []
        for i in range(self.listWidget_profiletool_component.count()):
            item = self.listWidget_profiletool_component.item(i)
            cb = self.listWidget_profiletool_component.itemWidget(item)
            if isinstance(cb, QCheckBox) and cb.isChecked():
                comp = cb.property("component").copy()
                list_selected_stage = []
                # Найти соответствующий виджет
                widget = self._component_id_to_widget.get(comp['id']) if hasattr(self, '_component_id_to_widget') else None
                if widget and widget.layout():
                    layout = widget.layout()
                    for j in range(1, layout.count()):
                        sublayout = layout.itemAt(j)
                        if not sublayout or not sublayout.layout():
                            continue
                        cb_widget = sublayout.layout().itemAt(0).widget()
                        if isinstance(cb_widget, QCheckBox) and cb_widget.isChecked():
                            stage = cb_widget.property("stage")
                            list_selected_stage.append({"stage": stage})
                comp["list_selected_stage"] = list_selected_stage
                selected.append(comp)
        return selected

    def clear_container(self, container: QWidget):
        if not container:
            return
        for child in container.findChildren(QWidget):
            child.deleteLater()

    def ensure_hbox(self, container: QWidget) -> QHBoxLayout:
        layout = container.layout()
        if not isinstance(layout, QHBoxLayout):
            layout = QHBoxLayout()
            container.setLayout(layout)
        return layout

    # --- Изделие ---
    def on_search_product(self, text: str):
        self.listWidget_product_search.clear()
        if not text.strip():
            return
        results = api_manager.search_in('product', 'name', text)[:10]
        for product in results:
            item = QListWidgetItem(f"{product['name']} - {product['description']}")
            item.setData(Qt.UserRole, product)
            self.listWidget_product_search.addItem(item)

    def on_product_selected(self):
        item = self.listWidget_product_search.currentItem()
        if not item:
            return
        self.product = item.data(Qt.UserRole)
        # Разблокировать Next
        btn = self.button(QWizard.NextButton)
        if btn:
            btn.setEnabled(True)

    def populate_product_components(self):
        if not self.product:
            return
        self.listWidget_product_component.clear()
        for comp in self.product.get('component', []):
            item = QListWidgetItem()
            cb = QCheckBox(comp['name'])
            cb.setProperty("component", comp)
            item.setSizeHint(cb.sizeHint())
            self.listWidget_product_component.addItem(item)
            self.listWidget_product_component.setItemWidget(item, cb)

    def collect_selected_product_components(self):
        selected = []
        for i in range(self.listWidget_product_component.count()):
            item = self.listWidget_product_component.item(i)
            widget = self.listWidget_product_component.itemWidget(item)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                comp = widget.property("component")
                selected.append(comp)
        return selected

    # --- Создание задач ---
    def accept(self):
        if self.profiletool:
            self.create_profiletool_task()
        elif self.product:
            self.create_product_task()
        super().accept()

    def create_profiletool_task(self):
        deadline = self.dateEdit_date.date().toString("yyyy-MM-dd")
        description = self.textEdit_desctiption.toPlainText()
        type_id = self.comboBox_work_type.currentData()
        task_data = {
            "profiletool_id": self.profiletool['id'],
            "deadline": deadline,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "description": description,
            "status_id": 1,
            "type_id": type_id,
            "location_id": 1
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']
        for component in self.dict_selected_profiletool_component:
            component_data = {"profiletool_component_id": component['id'], "description": ""}
            task_component = api_manager.api_task.create_task_component(task_id, component_data)
            task_component_id = task_component['id']
            list_selected_stage = component.get('list_selected_stage', [])
            for selected_stage in list_selected_stage:
                stage = {
                    "work_subtype_id": selected_stage['stage']['work_subtype']['id'],
                    "stage_num": selected_stage['stage']['stage_num']
                }
                try:
                    api_manager.api_task.create_task_component_stage(task_component_id, stage)
                except Exception as e:
                    print(f"Ошибка при создании этапа: {e}")

    def create_product_task(self):
        deadline = self.dateEdit_date.date().toString("yyyy-MM-dd")
        description = self.textEdit_desctiption.toPlainText()
        type_id = self.comboBox_work_type.currentData()
        task_data = {
            "product_id": self.product['id'],
            "deadline": deadline,
            "created": QDate.currentDate().toString("yyyy-MM-dd"),
            "description": description,
            "status_id": 1,
            "type_id": type_id,
            "location_id": 1
        }
        task = api_manager.api_task.create_task(task_data)
        task_id = task['id']
        for component in self.dict_selected_product_component:
            component_data = {"product_component_id": component['id'], "description": ""}
            api_manager.api_task.create_task_component(task_id, component_data)
