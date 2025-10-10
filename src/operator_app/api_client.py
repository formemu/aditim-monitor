# api_client.py
import requests
from typing import List, Dict

BASE_URL = "http://0.0.0.0:8000/api"

def get_work_types():
    url = f"{BASE_URL}/directory/dir_work_type"

    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data
    
def get_machines_by_work_type(work_type_id: int = None) -> List[Dict]:
    # Если work_type_id не задан — получаем все станки (без параметра)
    if work_type_id is None:
        url = f"{BASE_URL}/directory/dir_machine"
    else:
        url = f"{BASE_URL}/directory/dir_machine?work_type_id={work_type_id}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            return data

def get_stages_for_machine(machine_id: int, work_type_id: int = None) -> List[Dict]:
    tasks = requests.get(f"{BASE_URL}/task").json()
    next_stages = []
    for task in tasks:
        for component in task.get("component", []):
            # Собираем ВСЕ этапы этого компонента
            all_component_stages = component.get("stage", []) or []
            if not all_component_stages:
                continue
            # Сортируем по stage_num
            sorted_stages = sorted(all_component_stages, key=lambda s: s.get("stage_num", 0))
            # Находим первый незавершённый этап
            next_stage = None
            for stage in sorted_stages:
                if stage.get("finish") is None:
                    next_stage = stage
                    break
            # Если нет незавершённого — пропускаем
            if next_stage is None:
                continue
            # Проверяем, что все предыдущие этапы завершены
            previous_stages = [s for s in sorted_stages if s["stage_num"] < next_stage["stage_num"]]
            if any(s.get("finish") is None for s in previous_stages):
                # Есть незавершённые предыдущие этапы → пропускаем
                continue
            # Проверяем, подходит ли этот этап по станку и типу работ
            machine_match = (
                next_stage.get("machine") and 
                next_stage["machine"]["id"] == machine_id
            )
            work_type_match = True
            if work_type_id is not None:
                if next_stage.get("work_subtype"):
                    work_type_match = (next_stage["work_subtype"].get("work_type_id") == work_type_id)
                else:
                    work_type_match = False
            if machine_match and work_type_match:
                # Добавляем контекст
                next_stage["task_id"] = task["id"]
                next_stage["task_name"] = f"#{task['id']} — {task.get('product_name', 'Профиль')}"
                next_stage["component_id"] = component.get("id")
                next_stage["component_name"] = (
                    component["profiletool_component"]["type"]["name"]
                    if component.get("profiletool_component")
                    else (component["product_component"]["name"] if component.get("product_component") else "Без имени")
                )
                next_stages.append(next_stage)
    return next_stages

def get_quenching_stages(work_type_id: int) -> List[Dict]:
    """
    Возвращает следующую стадию закалки для каждого компонента каждой задачи.
    """
    tasks = requests.get(f"{BASE_URL}/task").json()
    quenching_stages = []

    for task in tasks:
        for component in task.get("component", []):
            # Собираем все этапы закалки этого конкретного компонента
            quenching_stages_for_component = [
                stage for stage in component.get("stage", []) or []
                if (stage.get("work_subtype") and 
                    "закалка" in stage["work_subtype"]["name"].lower() and
                    stage.get("machine") is None and
                    stage["work_subtype"].get("work_type_id") == work_type_id)
            ]
            
            if not quenching_stages_for_component:
                continue

            # Сортируем этапы закалки этого компонента по stage_num
            sorted_stages = sorted(quenching_stages_for_component, key=lambda s: s.get("stage_num", 0))

            # Ищем первую незавершенную стадию закалки для этого компонента
            next_stage = None
            for stage in sorted_stages:
                if stage.get("finish") is None:
                    next_stage = stage
                    break  # Только первая незавершённая для этого компонента

            if next_stage:
                # Добавляем контекст
                next_stage["task_id"] = task["id"]
                next_stage["task_name"] = f"#{task['id']} — {task.get('product_name', 'Профиль')}"
                next_stage["component_id"] = component.get("id")
                next_stage["component_name"] = (
                    component["profiletool_component"]["type"]["name"]
                    if component.get("profiletool_component")
                    else (component["product_component"]["name"] if component.get("product_component") else "Без имени")
                )
                next_stage["is_quenching"] = True
                quenching_stages.append(next_stage)

    return quenching_stages

def update_stage_dates(stage_id: int, start=None, finish=None):
    data = {}
    if start:
        data["start"] = start
    if finish:
        data["finish"] = finish
    requests.patch(f"{BASE_URL}/task/component/stage/{stage_id}", json=data)