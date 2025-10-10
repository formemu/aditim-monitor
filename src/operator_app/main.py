# main.py
import flet as ft
from datetime import date
from api_client import *

def main(page: ft.Page):
    page.title = "Оператор"
    page.vertical_spacing = 10

    # Состояние
    selected_mode = "category"  # "category" или "task"
    selected_work_type = None
    selected_machine = None
    selected_task = None
    all_stages = []  # Все этапы для выбранной категории

    # Элементы интерфейса
    mode_radio = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="category", label="По категории и станку"),
            ft.Radio(value="task", label="По задаче")
        ])
    )
    
    work_type_dropdown = ft.Dropdown(label="Категория", options=[])
    machine_dropdown = ft.Dropdown(label="Станок (все)", options=[])
    task_dropdown = ft.Dropdown(label="Задача", options=[])
    stage_list = ft.Column()

    def on_mode_change(e):
        nonlocal selected_mode
        selected_mode = e.control.value
        
        # Показываем/скрываем соответствующие элементы
        if selected_mode == "category":
            work_type_dropdown.visible = True
            machine_dropdown.visible = True
            task_dropdown.visible = False
        else:
            work_type_dropdown.visible = False
            machine_dropdown.visible = False
            task_dropdown.visible = True
            
        # Очищаем данные
        all_stages = []
        stage_list.controls.clear()
        page.update()

    def on_work_type_change(e):
        nonlocal selected_work_type, all_stages
        try:
            selected_work_type = int(e.control.value)
        except (ValueError, TypeError):
            selected_work_type = None

        # Очищаем список станков, если категория не выбрана
        if selected_work_type is None:
            machine_dropdown.options = []
            machine_dropdown.value = None
            machine_dropdown.hint_text = "Сначала выберите категорию"
            all_stages = []
        else:
            # Загружаем станки только для выбранной категории
            machines = get_machines_by_work_type(selected_work_type)
            machine_dropdown.options = [
                ft.dropdown.Option(key="all", text="Все станки")
            ] + [
                ft.dropdown.Option(key=str(m["id"]), text=m["name"])
                for m in machines
            ]
            machine_dropdown.value = "all"
            machine_dropdown.hint_text = "Выберите станок"
            
            # Загружаем все этапы для выбранной категории
            load_all_stages()
        
        page.update()

    def on_machine_change(e):
        nonlocal selected_machine
        if e.control.value == "all":
            selected_machine = None
        else:
            selected_machine = int(e.control.value)
        filter_stages()
        page.update()

    def on_task_change(e):
        nonlocal selected_task, all_stages
        try:
            selected_task = int(e.control.value)
        except (ValueError, TypeError):
            selected_task = None
        
        if selected_task is None:
            all_stages = []
        else:
            load_task_stages()
        
        page.update()

    def load_all_stages():
        """Загружает все этапы для выбранной категории"""
        nonlocal all_stages
        stage_list.controls = [ft.Text("Загрузка...")]
        page.update()
        
        all_stages = []
        
        # Получаем название выбранной категории
        work_types = get_work_types()
        selected_work_type_name = None
        for wt in work_types:
            if wt["id"] == selected_work_type:
                selected_work_type_name = wt["name"].lower()
                break
        
        # Если выбрана категория "закалка" - загружаем только этапы закалки
        if selected_work_type_name and "закалка" in selected_work_type_name:
            quenching_stages = get_quenching_stages(selected_work_type)
            all_stages.extend(quenching_stages)
        else:
            # Для остальных категорий загружаем этапы со всех станков
            machines = get_machines_by_work_type(selected_work_type)
            for machine in machines:
                stages = get_stages_for_machine(machine["id"], selected_work_type)
                all_stages.extend(stages)
        
        # Показываем все этапы
        filter_stages()

    def load_task_stages():
        """Загружает все этапы для выбранной задачи"""
        nonlocal all_stages
        stage_list.controls = [ft.Text("Загрузка...")]
        page.update()
        
        all_stages = []
        
        # Получаем все задачи
        tasks = requests.get(f"{BASE_URL}/task").json()
        
        # Находим выбранную задачу
        selected_task_data = None
        for task in tasks:
            if task["id"] == selected_task:
                selected_task_data = task
                break
        
        if not selected_task_data:
            stage_list.controls = [ft.Text("Задача не найдена")]
            page.update()
            return
        
        # Загружаем все этапы для этой задачи
        for component in selected_task_data.get("component", []):
            for stage in component.get("stage", []) or []:
                # Добавляем контекст
                stage["task_name"] = f"#{selected_task_data['id']} — {selected_task_data.get('product_name', 'Профиль')}"
                comp_type = (
                    component["profiletool_component"]["type"]["name"]
                    if component.get("profiletool_component")
                    else (component["product_component"]["name"] if component.get("product_component") else "Без имени")
                )
                stage["component_name"] = comp_type
                
                # Определяем тип этапа
                if stage.get("work_subtype") and "закалка" in stage["work_subtype"]["name"].lower():
                    stage["is_quenching"] = True
                
                all_stages.append(stage)
        
        # Показываем все этапы
        display_stages(all_stages)

    def filter_stages():
        """Фильтрует этапы по выбранному станку"""
        if selected_machine is None:
            # Показываем все этапы
            display_stages(all_stages)
        else:
            # Фильтруем по станку (закалка всегда показывается)
            filtered_stages = []
            for stage in all_stages:
                if stage.get("is_quenching"):
                    # Закалка всегда показывается
                    filtered_stages.append(stage)
                elif stage.get("machine") and stage["machine"]["id"] == selected_machine:
                    # Обычные этапы фильтруются по станку
                    filtered_stages.append(stage)
            display_stages(filtered_stages)

    def display_stages(stages):
        """Отображает список этапов"""
        stage_list.controls.clear()
        for stage in stages:
            if stage.get("is_quenching"):
                # Специальная обработка для закалки
                start_btn = ft.ElevatedButton(
                    "Уехала на закалку",
                    disabled=stage["start"] is not None,
                    on_click=lambda e, sid=stage["id"]: mark_start(sid),
                )
                finish_btn = ft.ElevatedButton(
                    "Приехала с закалки",
                    disabled=stage["finish"] is not None,
                    on_click=lambda e, sid=stage["id"]: mark_finish(sid),
                )
                
                stage_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Text(f"{stage['task_name']} — {stage['component_name']} (ЗАКАЛКА)", 
                                       weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
                                ft.Text(f"Операция: {stage['work_subtype']['name']}"),
                                ft.Text(f"Уехала: {stage['start'] or '—'}"),
                                ft.Text(f"Приехала: {stage['finish'] or '—'}"),
                                ft.Row([start_btn, finish_btn])
                            ])
                        )
                    )
                )
            else:
                # Обычная обработка для станков
                start_btn = ft.ElevatedButton(
                    "Взял в работу",
                    disabled=stage["start"] is not None,
                    on_click=lambda e, sid=stage["id"]: mark_start(sid),
                )
                finish_btn = ft.ElevatedButton(
                    "Выполнено",
                    disabled=stage["finish"] is not None,
                    on_click=lambda e, sid=stage["id"]: mark_finish(sid),
                )
                
                # Добавляем информацию о станке
                machine_info = f" — {stage['machine']['name']}" if stage.get("machine") else ""
                
                stage_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Text(f"{stage['task_name']} — {stage['component_name']}{machine_info}", 
                                       weight=ft.FontWeight.BOLD),
                                ft.Text(f"Операция: {stage['work_subtype']['name']}"),
                                ft.Text(f"Start: {stage['start'] or '—'}"),
                                ft.Text(f"Finish: {stage['finish'] or '—'}"),
                                ft.Row([start_btn, finish_btn])
                            ])
                        )
                    )
                )
        page.update()

    def mark_start(stage_id):
        update_stage_dates(stage_id, start=str(date.today()))
        if selected_mode == "category":
            load_all_stages()
        else:
            load_task_stages()

    def mark_finish(stage_id):
        update_stage_dates(stage_id, finish=str(date.today()))
        if selected_mode == "category":
            load_all_stages()
        else:
            load_task_stages()

    # Загрузка типов работ
    work_type_dropdown.options = [
        ft.dropdown.Option(key=str(wt["id"]), text=wt["name"])
        for wt in get_work_types()
    ]

    # Загрузка задач
    tasks = requests.get(f"{BASE_URL}/task").json()
    task_dropdown.options = [
        ft.dropdown.Option(key=str(task["id"]), text=f"#{task['id']} — {task.get('product_name', 'Профиль')}")
        for task in tasks
    ]

    mode_radio.on_change = on_mode_change
    work_type_dropdown.on_change = on_work_type_change
    machine_dropdown.on_change = on_machine_change
    task_dropdown.on_change = on_task_change

    page.add(
        ft.Text("Приложение оператора", size=24),
        ft.Text("Режим работы:", size=16),
        mode_radio,
        ft.Divider(),
        work_type_dropdown,
        machine_dropdown,
        task_dropdown,
        ft.Divider(),
        stage_list
    )

ft.app(target=main, view=ft.WEB_BROWSER, port=8550)