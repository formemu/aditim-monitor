# main.py
import flet as ft
from datetime import date
from api_client import *

def main(page: ft.Page):
    page.title = "Оператор"
    page.vertical_spacing = 10

    # Состояние
    selected_work_type = None
    selected_machine = None

    # Элементы интерфейса
    work_type_dropdown = ft.Dropdown(label="Категория", options=[])
    machine_dropdown = ft.Dropdown(label="Станок", options=[])
    stage_list = ft.Column()

    def on_work_type_change(e):
        nonlocal selected_work_type
        try:
            selected_work_type = int(e.control.value)
        except (ValueError, TypeError):
            selected_work_type = None

        # Очищаем список станков, если категория не выбрана
        if selected_work_type is None:
            machine_dropdown.options = []  # 🟩 ПУСТО
            machine_dropdown.value = None
            machine_dropdown.hint_text = "Сначала выберите категорию"
        else:
            # Загружаем станки только для выбранной категории
            machines = get_machines_by_work_type(selected_work_type)
            machine_dropdown.options = [
                ft.dropdown.Option(key=str(m["id"]), text=m["name"])
                for m in machines
            ]
            machine_dropdown.value = None
            machine_dropdown.hint_text = "Выберите станок"

        # Очищаем список этапов
        stage_list.controls.clear()
        page.update()

    def on_machine_change(e):
        nonlocal selected_machine
        selected_machine = int(e.control.value)
        load_stages()
        page.update()

    def load_stages():
        stage_list.controls = [ft.Text("Загрузка...")]
        page.update()
        stages = get_stages_for_machine(selected_machine)
        stage_list.controls.clear()
        for stage in stages:
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
            stage_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Text(f"{stage['task_name']} — {stage['component_name']}", weight=ft.FontWeight.BOLD),
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
        load_stages()

    def mark_finish(stage_id):
        update_stage_dates(stage_id, finish=str(date.today()))
        load_stages()

    # Загрузка типов работ
    work_type_dropdown.options = [
        ft.dropdown.Option(key=str(wt["id"]), text=wt["name"])
        for wt in get_work_types()
    ]

    machine_dropdown.options = [
        ft.dropdown.Option(key=str(m["id"]), text=m["name"])
        for m in get_machines_by_work_type(selected_work_type)
    ]

    work_type_dropdown.on_change = on_work_type_change
    # machine_dropdown.disabled = (selected_work_type is None)
    machine_dropdown.on_change = on_machine_change


    page.add(
        ft.Text("Приложение оператора", size=24),
        work_type_dropdown,
        machine_dropdown,
        ft.Divider(),
        stage_list
    )

ft.app(target=main, view=ft.WEB_BROWSER, port=8550)