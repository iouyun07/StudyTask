"""自动化测试：覆盖实验指导书第二章 2.5 节的 T1–T10，以及若干校验/边界用例。

运行方式（在项目根目录）：
    .venv\\Scripts\\python.exe -m pytest -v
"""

import re
import sqlite3
from datetime import date, timedelta

from app import create_app

BASE = {
    "name": "示例任务",
    "course": "数据结构",
    "description": "",
    "due_date": "2026-12-31",
    "priority": "中",
    "status": "待完成",
}


def create_task(client, **overrides):
    """通过新建页面提交一个任务，返回响应。"""
    data = dict(BASE)
    data.update(overrides)
    return client.post("/tasks/new", data=data, follow_redirects=True)


def db_rows(app):
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    finally:
        conn.close()


def db_count(app):
    return len(db_rows(app))


def stat_values(html):
    """从首页 HTML 中取出 总数 / 已完成 / 完成率 三个数字。"""
    total = re.search(r'<span class="stat-value">(\d+)</span>\s*<span class="stat-label">任务总数</span>', html)
    done = re.search(r'<span class="stat-value">(\d+)</span>\s*<span class="stat-label">已完成</span>', html)
    rate = re.search(r'<span class="stat-value">(\d+)%</span>\s*<span class="stat-label">完成率</span>', html)
    return (
        int(total.group(1)) if total else None,
        int(done.group(1)) if done else None,
        int(rate.group(1)) if rate else None,
    )


# ---------- T1 新建任务 ----------
def test_t1_create_task_shows_in_list(client, app):
    resp = create_task(
        client,
        name="线性表复习",
        course="数据结构",
        due_date="2026-11-20",
        priority="高",
    )
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "线性表复习" in html
    assert "数据结构" in html
    assert "2026-11-20" in html
    assert db_count(app) == 1


# ---------- T2 名称为空 ----------
def test_t2_empty_name_rejected_without_dirty_data(client, app):
    resp = create_task(client, name="")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "请输入任务名称" in html
    assert db_count(app) == 0


# ---------- T3 修改描述与优先级 ----------
def test_t3_edit_description_and_priority_persists(client, app):
    create_task(client, name="链表练习", priority="低")
    task_id = db_rows(app)[0]["id"]

    resp = client.post(
        f"/tasks/{task_id}/edit",
        data={
            "name": "链表练习",
            "course": "数据结构",
            "description": "完成单链表反转与合并",
            "due_date": "2026-12-01",
            "priority": "高",
            "status": "待完成",
        },
        follow_redirects=True,
    )
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "完成单链表反转与合并" in html
    assert "高" in html

    # 刷新后从数据库读，确认真的写入
    row = db_rows(app)[0]
    assert row["description"] == "完成单链表反转与合并"
    assert row["priority"] == "高"


# ---------- T4 状态三态调整 ----------
def test_t4_status_transitions(client, app):
    create_task(client, name="状态测试")
    task_id = db_rows(app)[0]["id"]

    resp = client.post(f"/tasks/{task_id}/status", data={"status": "进行中"}, follow_redirects=True)
    assert "进行中" in resp.get_data(as_text=True)
    assert db_rows(app)[0]["status"] == "进行中"

    resp = client.post(f"/tasks/{task_id}/status", data={"status": "已完成"}, follow_redirects=True)
    assert "已完成" in resp.get_data(as_text=True)
    assert db_rows(app)[0]["status"] == "已完成"


def test_t4_status_rejects_unknown_value(client, app):
    create_task(client, name="状态测试")
    task_id = db_rows(app)[0]["id"]
    resp = client.post(f"/tasks/{task_id}/status", data={"status": "已归档"})
    assert resp.status_code == 400
    assert db_rows(app)[0]["status"] == "待完成"


# ---------- T5 筛选 ----------
def test_t5_filter_by_course_status_priority(client, app):
    create_task(client, name="任务甲", course="数据结构", status="待完成", priority="高", due_date="2026-11-20")
    create_task(client, name="任务乙", course="操作系统", status="已完成", priority="中", due_date="2026-11-21")
    create_task(client, name="任务丙", course="数据结构", status="进行中", priority="高", due_date="2026-11-22")

    html = client.get("/?course=数据结构").get_data(as_text=True)
    assert "任务甲" in html and "任务丙" in html and "任务乙" not in html

    html = client.get("/?status=待完成").get_data(as_text=True)
    assert "任务甲" in html and "任务乙" not in html and "任务丙" not in html

    html = client.get("/?priority=高").get_data(as_text=True)
    assert "任务甲" in html and "任务丙" in html and "任务乙" not in html

    html = client.get("/?course=数据结构&status=进行中&priority=高").get_data(as_text=True)
    assert "任务丙" in html and "任务甲" not in html and "任务乙" not in html


# ---------- T6 逾期 ----------
def test_t6_overdue_badge(client, app):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = create_task(client, name="逾期任务", due_date=yesterday)
    assert "逾期" in resp.get_data(as_text=True)


def test_t6_completed_task_has_no_overdue_badge(client, app):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    create_task(client, name="已完成的旧任务", due_date=yesterday, status="已完成")
    html = client.get("/").get_data(as_text=True)
    assert "已完成的旧任务" in html
    assert "逾期" not in html


# ---------- T7 即将到期 ----------
def test_t7_due_soon_badge(client, app):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    resp = create_task(client, name="即将到期任务", due_date=tomorrow)
    html = resp.get_data(as_text=True)
    assert "即将到期" in html
    assert "逾期" not in html


# ---------- T8 统计 ----------
def test_t8_stats_total_done_rate(client, app):
    for i in range(5):
        create_task(client, name=f"统计任务{i + 1}", due_date=f"2026-12-0{i + 1}")
    ids = [row["id"] for row in db_rows(app)]
    for task_id in ids[:2]:
        client.post(f"/tasks/{task_id}/status", data={"status": "已完成"})

    html = client.get("/").get_data(as_text=True)
    total, done, rate = stat_values(html)
    assert (total, done, rate) == (5, 2, 40)


def test_stats_zero_when_empty(client):
    html = client.get("/").get_data(as_text=True)
    assert stat_values(html) == (0, 0, 0)


# ---------- T9 删除确认 ----------
def test_t9_delete_keeps_data_until_confirmed(client, app):
    create_task(client, name="待删除任务")
    task_id = db_rows(app)[0]["id"]

    # 打开确认页（取消 = 不提交删除）
    resp = client.get(f"/tasks/{task_id}/delete")
    assert resp.status_code == 200
    assert "确认删除" in resp.get_data(as_text=True)
    assert db_count(app) == 1

    # 确认删除
    resp = client.post(f"/tasks/{task_id}/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert db_count(app) == 0
    assert "待删除任务" not in resp.get_data(as_text=True)


# ---------- T10 重启后数据仍在 ----------
def test_t10_data_survives_restart(app):
    client = app.test_client()
    create_task(client, name="重启后仍存在")

    # 用同一个数据库文件重新创建一个应用实例，模拟“关闭并重新启动”
    second_app = create_app(
        {"TESTING": True, "DATABASE": app.config["DATABASE"], "SECRET_KEY": "test-key"}
    )
    html = second_app.test_client().get("/").get_data(as_text=True)
    assert "重启后仍存在" in html


# ---------- 其他校验 ----------
def test_invalid_due_date_rejected(client, app):
    resp = create_task(client, due_date="2026-13-40")
    assert "截止日期格式" in resp.get_data(as_text=True)
    assert db_count(app) == 0


def test_missing_task_returns_404(client):
    assert client.get("/tasks/9999").status_code == 404
    assert client.get("/tasks/9999/edit").status_code == 404
