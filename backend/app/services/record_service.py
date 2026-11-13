"""生产记录业务逻辑：查询、录入、修改与趋势数据。"""

import sqlite3
from datetime import datetime

from ..config import DATETIME_FORMAT, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MAX_TREND_DAYS
from ..models.production import TABLE_NAME, row_to_dict

DUPLICATE_DATE_ERROR = "该日期已存在生产数据，请直接编辑该日记录"


def _now() -> str:
    return datetime.now().strftime(DATETIME_FORMAT)


def list_records(
    conn: sqlite3.Connection,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict:
    """按日期范围分页查询生产记录，日期倒序。"""
    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)

    conditions: list[str] = []
    params: list = []
    if start_date:
        conditions.append("production_date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("production_date <= ?")
        params.append(end_date)
    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""

    total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}{where}", params).fetchone()[0]
    offset = (page - 1) * page_size
    rows = conn.execute(
        f"SELECT * FROM {TABLE_NAME}{where} ORDER BY production_date DESC LIMIT ? OFFSET ?",
        [*params, page_size, offset],
    ).fetchall()
    return {
        "items": [row_to_dict(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_record(conn: sqlite3.Connection, record_id: int) -> dict | None:
    """按主键查询生产记录。"""
    row = conn.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (record_id,)).fetchone()
    return row_to_dict(row) if row else None


def get_record_by_date(conn: sqlite3.Connection, production_date: str) -> dict | None:
    """按生产日期查询记录（日期唯一）。"""
    row = conn.execute(
        f"SELECT * FROM {TABLE_NAME} WHERE production_date = ?", (production_date,)
    ).fetchone()
    return row_to_dict(row) if row else None


def get_previous_record(conn: sqlite3.Connection, production_date: str) -> dict | None:
    """查询指定日期之前最近的一条生产记录（允许日期不连续）。"""
    row = conn.execute(
        f"SELECT * FROM {TABLE_NAME} WHERE production_date < ? ORDER BY production_date DESC LIMIT 1",
        (production_date,),
    ).fetchone()
    return row_to_dict(row) if row else None


def create_record(conn: sqlite3.Connection, data: dict) -> dict:
    """新增单日生产数据；日期重复时抛出 ValueError。"""
    if get_record_by_date(conn, data["production_date"]):
        raise ValueError(DUPLICATE_DATE_ERROR)
    now = _now()
    cursor = conn.execute(
        f"""
        INSERT INTO {TABLE_NAME}
            (production_date, crude_oil_output, natural_gas_output, water_injection,
             energy_consumption, shutdown_well_count, abnormal_description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["production_date"],
            data["crude_oil_output"],
            data["natural_gas_output"],
            data["water_injection"],
            data["energy_consumption"],
            data["shutdown_well_count"],
            data["abnormal_description"],
            now,
            now,
        ),
    )
    conn.commit()
    return get_record(conn, cursor.lastrowid)


def update_record(conn: sqlite3.Connection, record_id: int, data: dict) -> dict | None:
    """修改生产数据；记录不存在返回 None，日期冲突抛出 ValueError。"""
    existing = get_record(conn, record_id)
    if existing is None:
        return None
    if data["production_date"] != existing["production_date"]:
        clash = get_record_by_date(conn, data["production_date"])
        if clash:
            raise ValueError(DUPLICATE_DATE_ERROR)
    conn.execute(
        f"""
        UPDATE {TABLE_NAME}
        SET production_date = ?, crude_oil_output = ?, natural_gas_output = ?, water_injection = ?,
            energy_consumption = ?, shutdown_well_count = ?, abnormal_description = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            data["production_date"],
            data["crude_oil_output"],
            data["natural_gas_output"],
            data["water_injection"],
            data["energy_consumption"],
            data["shutdown_well_count"],
            data["abnormal_description"],
            _now(),
            record_id,
        ),
    )
    conn.commit()
    return get_record(conn, record_id)


TREND_FIELDS = (
    "production_date",
    "crude_oil_output",
    "natural_gas_output",
    "water_injection",
    "energy_consumption",
)


def get_trend_points(conn: sqlite3.Connection, days: int) -> list[dict]:
    """返回最近 N 天的趋势数据点，按日期升序。"""
    days = min(max(days, 1), MAX_TREND_DAYS)
    rows = conn.execute(
        f"""
        SELECT production_date, crude_oil_output, natural_gas_output, water_injection, energy_consumption
        FROM {TABLE_NAME}
        ORDER BY production_date DESC
        LIMIT ?
        """,
        (days,),
    ).fetchall()
    return [{field: row[field] for field in TREND_FIELDS} for row in reversed(rows)]
