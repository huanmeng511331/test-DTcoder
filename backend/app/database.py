"""SQLite 连接与建库初始化。"""

import sqlite3

from .config import get_db_path
from .models.production import TABLE_DDL


def get_connection() -> sqlite3.Connection:
    """建立 SQLite 连接并设置行工厂。"""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection | None = None) -> None:
    """创建数据表，已存在则跳过。"""
    owned = conn is None
    conn = conn or get_connection()
    try:
        conn.executescript(TABLE_DDL)
        conn.commit()
    finally:
        if owned:
            conn.close()
