import httpx

def test_get_departaments():
    resp = httpx.get("http://localhost:8000/departaments")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert all("id" in d and "name" in d for d in data)

def test_add_and_get_task_profile():
    # Предварительно создать профиль и вариант
    profile = httpx.post("http://localhost:8000/profile_types", json={"article": "TEST-ART", "name": "Тестовый профиль"}).json()
    assert "id" in profile
    # Вариант профиля (добавить вручную в БД или реализовать эндпоинт)
    # Здесь предполагается, что id_variant=1 существует
    payload = {
        "id_product": None,
        "id_profile_type": profile["id"],
        "id_departament": 1,
        "equipment": "Плита 1, Плита 2",
        "stage": "",
        "deadline": "2025-07-10",
        "position": 0,
        "id_type_work": 1,
        "profile_components": [
            {"variant": 1, "name": "Плита 1", "geometry": "geom1"},
            {"variant": 1, "name": "Плита 2", "geometry": "geom2"}
        ]
    }
    resp = httpx.post("http://localhost:8000/tasks", json=payload)
    assert resp.status_code == 200
    task = resp.json()
    assert "id" in task

def test_add_and_get_task_product():
    # Предварительно создать продукт
    product = httpx.post("http://localhost:8000/products", json={"name": "Тестовый продукт", "id_departament": 1, "sketch": None}).json()
    assert "id" in product
    payload = {
        "id_product": product["id"],
        "id_profile_type": None,
        "id_departament": 1,
        "equipment": "Комп1, Комп2",
        "stage": "",
        "deadline": "2025-07-10",
        "position": 0,
        "id_type_work": 1,
        "product_components": ["Комп1", "Комп2"]
    }
    resp = httpx.post("http://localhost:8000/tasks", json=payload)
    assert resp.status_code == 200
    task = resp.json()
    assert "id" in task
