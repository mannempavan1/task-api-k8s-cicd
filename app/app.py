from flask import Flask, jsonify, request
from datetime import datetime, timezone
import os
import socket

app = Flask(__name__)

# In-memory store (simple by design — the point of this project is the infra, not the app)
tasks = []
next_id = 1


@app.route("/health", methods=["GET"])
def health():
    """Liveness/readiness probe target for Kubernetes."""
    return jsonify({"status": "healthy", "hostname": socket.gethostname()}), 200


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "task-api",
        "version": os.environ.get("APP_VERSION", "dev"),
        "hostname": socket.gethostname(),
        "time": datetime.now(timezone.utc).isoformat()
    })


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    data = request.get_json(force=True, silent=True) or {}
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = data.get("done", t["done"])
            return jsonify(t), 200
    return jsonify({"error": "task not found"}), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == before:
        return jsonify({"error": "task not found"}), 404
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
