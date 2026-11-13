"""StudyTask 应用入口：创建应用、注册路由。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

import db
import tasks


def create_app(test_config: dict | None = None) -> Flask:
    """应用工厂；测试时可传入 test_config 覆盖数据库路径等配置。"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key-change-me",
        DATABASE=str(Path(app.instance_path) / "studytask.db"),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    _ensure_database(app)

    register_routes(app)
    return app


def _ensure_database(app: Flask) -> None:
    """首次启动时建表（schema 使用 IF NOT EXISTS，可重复执行）。"""
    conn = db.connect(app.config["DATABASE"])
    try:
        db.init_db(conn)
    finally:
        conn.close()


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _safe_next(default: str) -> str:
    """只允许跳回本站相对路径，防止被利用做外部跳转。"""
    target = request.form.get("next") or request.args.get("next") or ""
    if target.startswith("/") and not target.startswith("//"):
        return target
    return default


def _find_task(conn, task_id: int):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        abort(404)
    return row


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index():
        conn = db.get_db()
        filters = {
            "course": request.args.get("course", "").strip(),
            "status": request.args.get("status", "").strip(),
            "priority": request.args.get("priority", "").strip(),
        }

        sql = "SELECT * FROM tasks WHERE 1 = 1"
        params: list[str] = []
        if filters["course"]:
            sql += " AND course = ?"
            params.append(filters["course"])
        if filters["status"]:
            sql += " AND status = ?"
            params.append(filters["status"])
        if filters["priority"]:
            sql += " AND priority = ?"
            params.append(filters["priority"])
        sql += " ORDER BY due_date ASC, id DESC"
        rows = conn.execute(sql, params).fetchall()

        stats = tasks.summarize(conn.execute("SELECT status FROM tasks").fetchall())
        courses = [
            row["course"]
            for row in conn.execute("SELECT DISTINCT course FROM tasks ORDER BY course")
        ]

        items = [
            {
                "task": row,
                "overdue": tasks.is_overdue(row),
                "due_soon": tasks.is_due_soon(row),
            }
            for row in rows
        ]
        return render_template(
            "index.html",
            items=items,
            stats=stats,
            courses=courses,
            filters=filters,
            filtered=any(filters.values()),
            statuses=tasks.STATUSES,
            priorities=tasks.PRIORITIES,
        )

    @app.route("/tasks/new", methods=["GET", "POST"])
    def new_task():
        data = {
            "name": "",
            "course": "",
            "description": "",
            "due_date": "",
            "priority": "中",
            "status": "待完成",
        }
        errors: dict[str, str] = {}
        if request.method == "POST":
            data, errors = tasks.validate_task(request.form)
            if not errors:
                now = _now()
                conn = db.get_db()
                conn.execute(
                    """INSERT INTO tasks
                       (name, course, description, due_date, priority, status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        data["name"],
                        data["course"],
                        data["description"],
                        data["due_date"],
                        data["priority"],
                        data["status"],
                        now,
                        now,
                    ),
                )
                conn.commit()
                flash("任务已创建", "success")
                return redirect(url_for("index"))
        return render_template(
            "form.html",
            title="新建任务",
            action=url_for("new_task"),
            data=data,
            errors=errors,
            statuses=tasks.STATUSES,
            priorities=tasks.PRIORITIES,
        )

    @app.route("/tasks/<int:task_id>")
    def task_detail(task_id: int):
        conn = db.get_db()
        task = _find_task(conn, task_id)
        return render_template(
            "detail.html",
            task=task,
            overdue=tasks.is_overdue(task),
            due_soon=tasks.is_due_soon(task),
            statuses=tasks.STATUSES,
        )

    @app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
    def edit_task(task_id: int):
        conn = db.get_db()
        task = _find_task(conn, task_id)
        data = dict(task)
        errors: dict[str, str] = {}
        if request.method == "POST":
            data, errors = tasks.validate_task(request.form)
            if not errors:
                conn.execute(
                    """UPDATE tasks
                       SET name = ?, course = ?, description = ?, due_date = ?,
                           priority = ?, status = ?, updated_at = ?
                       WHERE id = ?""",
                    (
                        data["name"],
                        data["course"],
                        data["description"],
                        data["due_date"],
                        data["priority"],
                        data["status"],
                        _now(),
                        task_id,
                    ),
                )
                conn.commit()
                flash("任务已更新", "success")
                return redirect(url_for("task_detail", task_id=task_id))
        return render_template(
            "form.html",
            title="编辑任务",
            action=url_for("edit_task", task_id=task_id),
            data=data,
            errors=errors,
            statuses=tasks.STATUSES,
            priorities=tasks.PRIORITIES,
        )

    @app.post("/tasks/<int:task_id>/status")
    def update_status(task_id: int):
        new_status = request.form.get("status", "")
        if new_status not in tasks.STATUSES:
            abort(400)
        conn = db.get_db()
        _find_task(conn, task_id)
        conn.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, _now(), task_id),
        )
        conn.commit()
        flash(f"状态已改为「{new_status}」", "success")
        return redirect(_safe_next(url_for("index")))

    @app.route("/tasks/<int:task_id>/delete", methods=["GET", "POST"])
    def delete_task(task_id: int):
        conn = db.get_db()
        task = _find_task(conn, task_id)
        if request.method == "POST":
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            flash("任务已删除", "success")
            return redirect(url_for("index"))
        return render_template("confirm_delete.html", task=task)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
