# main.py
import flet as ft
from datetime import date
from api_client import (
    get_work_types,
    get_machines_by_work_type,
    get_quenching_stages,
    get_all_stages_by_work_type,
    update_stage_dates
)


class OperatorApp:
    """Приложение оператора для управления этапами производства"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Оператор"
        self.page.vertical_spacing = 10
        
        # Состояние
        self.selected_work_type = None
        self.list_stage = []  # Все этапы для выбранной категории
        
        # UI элементы
        self.dropdown_work_type = ft.Dropdown(label="Категория работ", options=[])
        self.column_stage = ft.Column()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Инициализация UI"""
        # Загрузка типов работ
        self.dropdown_work_type.options = [
            ft.dropdown.Option(key=str(wt["id"]), text=wt["name"])
            for wt in get_work_types()
        ]
        
        # Подключение обработчиков
        self.dropdown_work_type.on_change = self._on_work_type_change

        # Включаем прокрутку для мобильных устройств
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Добавление элементов на страницу
        self.page.add(
            ft.Text("Приложение оператора", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.dropdown_work_type,
            ft.Divider(),
            self.column_stage
        )
    
    def _on_work_type_change(self, e):
        """Обработчик изменения категории работ"""
        try:
            self.selected_work_type = int(e.control.value)
        except (ValueError, TypeError):
            self.selected_work_type = None
        
        if self.selected_work_type is None:
            self.list_stage = []
            self.column_stage.controls.clear()
        else:
            # Загружаем все этапы для выбранной категории
            self._load_stage()
        
        self.page.update()
    
    def _load_stage(self):
        """Загружает все этапы для выбранной категории"""
        self.column_stage.controls = [ft.Text("Загрузка...")]
        self.page.update()
        
        # Получаем название выбранной категории
        list_work_type = get_work_types()
        name_work_type = None
        for wt in list_work_type:
            if wt["id"] == self.selected_work_type:
                name_work_type = wt["name"].lower()
                break
        
        # Если выбрана категория "закалка" - загружаем этапы закалки
        if name_work_type and "закалка" in name_work_type:
            self.list_stage = get_quenching_stages(self.selected_work_type)
        else:
            # Для остальных категорий загружаем все этапы без привязки к станку
            self.list_stage = get_all_stages_by_work_type(self.selected_work_type)
        
        # Отображаем этапы
        self._display_stage(self.list_stage)
    
    def _display_stage(self, list_stage):
        """Отображает список этапов"""
        self.column_stage.controls.clear()
        
        if not list_stage:
            self.column_stage.controls.append(
                ft.Text("Нет доступных этапов для выбранной категории", italic=True)
            )
            self.page.update()
            return
        
        for stage in list_stage:
            if stage.get("is_quenching"):
                # Специальная обработка для закалки
                button_start = ft.ElevatedButton(
                    "Уехала на закалку",
                    disabled=stage["start"] is not None,
                    on_click=lambda e, sid=stage["id"]: self._mark_start(sid),
                )
                button_finish = ft.ElevatedButton(
                    "Приехала с закалки",
                    disabled=stage["finish"] is not None,
                    on_click=lambda e, sid=stage["id"]: self._mark_finish(sid),
                )
                
                # Описание этапа (если есть)
                description = stage.get('description', '')
                description_text = ft.Text(f"📝 {description}", italic=True, color=ft.Colors.GREY_700) if description else ft.Container()
                
                self.column_stage.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Text(f"{stage['task_name']} — {stage['component_name']}", 
                                    weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"Операция: {stage['work_subtype']['name']}", color=ft.Colors.ORANGE),
                                description_text,
                                ft.Text(f"Уехала: {stage['start'] or '—'}"),
                                ft.Text(f"Приехала: {stage['finish'] or '—'}"),
                                ft.Row([button_start, button_finish])
                            ])
                        )
                    )
                )
            else:
                # Обычная обработка — оператор выбирает станок
                is_started = stage.get("start") is not None
                is_finished = stage.get("finish") is not None
                
                # Список доступных станков для этой категории
                list_machine = get_machines_by_work_type(self.selected_work_type)
                
                dropdown_machine = ft.Dropdown(
                    label="Выберите станок",
                    options=[
                        ft.dropdown.Option(key=str(m["id"]), text=m["name"])
                        for m in list_machine
                    ],
                    value=str(stage["machine"]["id"]) if stage.get("machine") else None,
                    disabled=is_started,
                    width=200
                )
                
                # ИСПРАВЛЕНИЕ: передаём stage_id И dropdown напрямую через default аргументы
                def create_start_handler(sid, dd):
                    return lambda e: self._mark_start_with_machine(sid, dd)
                
                button_start = ft.ElevatedButton(
                    "Принял в работу",
                    disabled=is_started,
                    on_click=create_start_handler(stage["id"], dropdown_machine),
                )
                
                button_finish = ft.ElevatedButton(
                    "Завершил работу",
                    disabled=not is_started or is_finished,
                    on_click=lambda e, sid=stage["id"]: self._mark_finish(sid),
                )
                
                # Информация о текущем станке
                text_machine = f"Станок: {stage['machine']['name']}" if stage.get("machine") else "Станок не выбран"
                
                # Описание этапа (если есть)
                description = stage.get('description', '')
                description_text = ft.Text(f"📝 {description}", italic=True, color=ft.Colors.GREY_700) if description else ft.Container()
                
                # Информация о заготовке (для type_id = 3)
                blank_info_controls = []
                if stage.get("task_type_id") == 3 and stage.get("blank_info"):
                    blank_info = stage["blank_info"]
                    blank_info_controls = [
                        ft.Divider(height=1),
                        ft.Text("📦 Габариты заготовки:", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE),
                        ft.Text(f"Материал: {blank_info.get('material', 'N/A')}", color=ft.Colors.BLUE_GREY),
                        ft.Text(f"Из чего: {blank_info.get('blank_size', 'N/A')} мм", color=ft.Colors.BLUE_GREY),
                        ft.Text(f"Что сделать: {blank_info.get('product_size', 'N/A')} мм", color=ft.Colors.GREEN_700),
                    ]
                
                self.column_stage.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Text(f"{stage['task_name']} — {stage['component_name']}", 
                                    weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"Операция: {stage['work_subtype']['name']}"),
                                description_text,
                                *blank_info_controls,
                                ft.Text(text_machine, color=ft.Colors.BLUE_700),
                                ft.Text(f"Начал: {stage['start'] or '—'}"),
                                ft.Text(f"Завершил: {stage['finish'] or '—'}"),
                                dropdown_machine if not is_started else ft.Container(),
                                ft.Row([button_start, button_finish], spacing=10)
                            ], spacing=5)
                        )
                    )
                )
        self.page.update()
    def _mark_start_with_machine(self, stage_id, dropdown_machine):
        """Отмечает начало выполнения этапа с привязкой к станку"""
        if not dropdown_machine.value:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Выберите станок перед началом работы!"))
            )
            return
        
        machine_id = int(dropdown_machine.value)
        update_stage_dates(stage_id, start=date.today(), machine_id=machine_id)  # ← date объект
        self._load_stage()

    def _mark_start(self, stage_id):
        """Отмечает начало выполнения этапа (для закалки)"""
        update_stage_dates(stage_id, start=date.today())  # ← date объект
        self._load_stage()

    def _mark_finish(self, stage_id):
        """Отмечает завершение этапа"""
        update_stage_dates(stage_id, finish=date.today())  # ← date объект
        self._load_stage()


def main(page: ft.Page):
    """Точка входа в приложение"""
    OperatorApp(page)


ft.app(target=main, view=ft.WEB_BROWSER, port=8550)