"""业务逻辑：输入校验、逾期/即将到期判定、统计。

这里只放纯函数，不依赖 Flask，方便单独测试。
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

PRIORITIES = ("高", "中", "低")
STATUSES = ("待完成", "进行中", "已完成")

NAME_MAX = 100
COURSE_MAX = 60
DESCRIPTION_MAX = 1000
DUE_SOON_DAYS = 3

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def clean(value: str | None) -> str:
    """去掉首尾空白，None 视为空串。"""
    return (value or "").strip()


def parse_date(text: str) -> date | None:
    """把 YYYY-MM-DD 解析为日期对象，非法返回 None。"""
    if not _DATE_RE.match(text or ""):
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def validate_task(form: dict) -> tuple[dict, dict]:
    """校验表单，返回 (清洗后的数据, 错误信息)。

    错误信息按字段名存放，模板据此在对应输入框旁提示。
    """
    data = {
        "name": clean(form.get("name")),
        "course": clean(form.get("course")),
        "description": clean(form.get("description")),
        "due_date": clean(form.get("due_date")),
        "priority": clean(form.get("priority")) or "中",
        "status": clean(form.get("status")) or "待完成",
    }
    errors: dict[str, str] = {}

    if not data["name"]:
        errors["name"] = "请输入任务名称"
    elif len(data["name"]) > NAME_MAX:
        errors["name"] = f"任务名称不能超过 {NAME_MAX} 字"

    if not data["course"]:
        errors["course"] = "请输入所属课程"
    elif len(data["course"]) > COURSE_MAX:
        errors["course"] = f"所属课程不能超过 {COURSE_MAX} 字"

    if len(data["description"]) > DESCRIPTION_MAX:
        errors["description"] = f"任务描述不能超过 {DESCRIPTION_MAX} 字"

    if not data["due_date"]:
        errors["due_date"] = "请选择截止日期"
    elif parse_date(data["due_date"]) is None:
        errors["due_date"] = "截止日期格式应为 YYYY-MM-DD，且必须是有效日期"

    if data["priority"] not in PRIORITIES:
        errors["priority"] = "优先级只能是 高、中、低"

    if data["status"] not in STATUSES:
        errors["status"] = "状态只能是 待完成、进行中、已完成"

    return data, errors


def is_overdue(task, today: date | None = None) -> bool:
    """未完成且截止日期早于今天 → 逾期。"""
    if task["status"] == "已完成":
        return False
    due = parse_date(task["due_date"])
    if due is None:
        return False
    return due < (today or date.today())


def is_due_soon(task, today: date | None = None) -> bool:
    """未完成且在今天起 3 天内（含今天）到期 → 即将到期。"""
    if task["status"] == "已完成":
        return False
    due = parse_date(task["due_date"])
    if due is None:
        return False
    now = today or date.today()
    return now <= due <= now + timedelta(days=DUE_SOON_DAYS)


def summarize(tasks) -> dict:
    """统计总数、已完成数与完成率（整数百分比）。"""
    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "已完成")
    rate = round(done * 100 / total) if total else 0
    return {"total": total, "done": done, "rate": rate}
