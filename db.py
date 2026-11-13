"""数据库连接与初始化。"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def connect(database: str) -> sqlite3.Connection:
    """打开一个 SQLite 连接，行以字典方式访问。"""
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def get_db() -> sqlite3.Connection:
    """取得当前请求共用的数据库连接（首次调用时建立）。"""
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(exception: Exception | None = None) -> None:
    """请求结束时关闭连接。"""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(conn: sqlite3.Connection) -> None:
    """执行 schema.sql，建表（可重复执行）。"""
    conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    conn.commit()


def init_app(app) -> None:
    """把数据库相关的清理函数注册到应用上。"""
    app.teardown_appcontext(close_db)
