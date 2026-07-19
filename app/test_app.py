import json
from app import app


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health():
    c = client()
    resp = c.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_index():
    c = client()
    resp = c.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["service"] == "task-api"


def test_create_and_get_task():
    c = client()
    resp = c.post("/tasks", data=json.dumps({"title": "Learn Kubernetes"}),
                   content_type="application/json")
    assert resp.status_code == 201
    task = resp.get_json()
    assert task["title"] == "Learn Kubernetes"
    assert task["done"] is False

    resp = c.get("/tasks")
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_create_task_missing_title():
    c = client()
    resp = c.post("/tasks", data=json.dumps({}), content_type="application/json")
    assert resp.status_code == 400


def test_update_task_not_found():
    c = client()
    resp = c.patch("/tasks/9999", data=json.dumps({"done": True}),
                    content_type="application/json")
    assert resp.status_code == 404


def test_delete_task_not_found():
    c = client()
    resp = c.delete("/tasks/9999")
    assert resp.status_code == 404
