# api_client.py
import requests
from typing import List, Dict

BASE_URL = "http://0.0.0.0:8000/api"

def get_work_types():
    url = f"{BASE_URL}/directory/dir_work_type"
    print(f"Запрос к: {url}")
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Получено:", data)
            return data
        else:
            print(f"❌ Ошибка: {resp.status_code}, {resp.text}")
            return []
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return []
    
def get_machines_by_work_type(work_type_id: int = None) -> List[Dict]:
    # Если work_type_id не задан — получаем все станки (без параметра)
    if work_type_id is None:
        url = f"{BASE_URL}/directory/dir_machine"
    else:
        url = f"{BASE_URL}/directory/dir_machine?work_type_id={work_type_id}"
    
    print(f"Запрос к: {url}")
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Получено машин:", data)
            return data
        else:
            print(f"❌ Ошибка: {resp.status_code}, {resp.text}")
            return []
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return []

def get_stages_for_machine(machine_id: int) -> List[Dict]:
    """
    Возвращает ТОЛЬКО следующую активную стадию для каждого компонента,
    назначенного на станок.
    """
    tasks = requests.get(f"{BASE_URL}/task").json()
    next_stages = []

    for task in tasks:
        for component in task.get("component", []):
            # Собираем все стадии компонента, назначенные на этот станок
            stages_on_machine = [
                stage for stage in component.get("stage", []) or []
                if stage.get("machine") and stage["machine"]["id"] == machine_id
            ]

            if not stages_on_machine:
                continue

            # Сортируем по stage_num
            sorted_stages = sorted(stages_on_machine, key=lambda s: s.get("stage_num", 0))

            # Ищем первую стадию без finish
            next_stage = None
            for stage in sorted_stages:
                if stage.get("finish") is None:
                    next_stage = stage
                    break  # Только первая незавершённая

            if next_stage:
                # Добавляем контекст
                next_stage["task_name"] = f"#{task['id']} — {task.get('product_name', 'Профиль')}"
                comp_type = (
                    component["profile_tool_component"]["type"]["name"]
                    if component.get("profile_tool_component")
                    else (component["product_component"]["name"] if component.get("product_component") else "Без имени")
                )
                next_stage["component_name"] = comp_type
                next_stages.append(next_stage)

    return next_stages

def update_stage_dates(stage_id: int, start=None, finish=None):
    data = {}
    if start:
        data["start"] = start
    if finish:
        data["finish"] = finish
    requests.patch(f"{BASE_URL}/task/component/stage/{stage_id}", json=data)

