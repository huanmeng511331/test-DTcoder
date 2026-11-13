"""生产记录服务测试：CRUD、分页筛选、唯一性与趋势数据。"""

import pytest

from app.services import record_service


def _data(**overrides):
    base = {
        "production_date": "2026-11-13",
        "crude_oil_output": 1200.0,
        "natural_gas_output": 88.0,
        "water_injection": 3100.0,
        "energy_consumption": 48.0,
        "shutdown_well_count": 0,
        "abnormal_description": "",
    }
    base.update(overrides)
    return base


def test_create_and_get_record(conn):
    created = record_service.create_record(conn, _data())
    assert created["id"] > 0
    assert created["production_date"] == "2026-11-13"

    fetched = record_service.get_record(conn, created["id"])
    assert fetched["crude_oil_output"] == 1200.0
    assert fetched["created_at"] == fetched["updated_at"]


def test_create_duplicate_date_raises(conn):
    record_service.create_record(conn, _data())
    with pytest.raises(ValueError, match="该日期已存在生产数据"):
        record_service.create_record(conn, _data())


def test_update_record(conn):
    created = record_service.create_record(conn, _data())
    updated = record_service.update_record(
        conn, created["id"], _data(crude_oil_output=1150.5, abnormal_description="设备检修")
    )
    assert updated["crude_oil_output"] == 1150.5
    assert updated["abnormal_description"] == "设备检修"
    assert updated["updated_at"] >= created["created_at"]


def test_update_missing_record_returns_none(conn):
    assert record_service.update_record(conn, 999, _data()) is None


def test_update_to_existing_date_raises(conn):
    first = record_service.create_record(conn, _data(production_date="2026-11-12"))
    record_service.create_record(conn, _data(production_date="2026-11-13"))
    with pytest.raises(ValueError, match="该日期已存在生产数据"):
        record_service.update_record(conn, first["id"], _data(production_date="2026-11-13"))


def test_list_records_pagination_and_filter(conn):
    for day in ("2026-11-11", "2026-11-12", "2026-11-13"):
        record_service.create_record(conn, _data(production_date=day))

    page_one = record_service.list_records(conn, page=1, page_size=2)
    assert page_one["total"] == 3
    assert len(page_one["items"]) == 2
    assert page_one["items"][0]["production_date"] == "2026-11-13"

    filtered = record_service.list_records(conn, start_date="2026-11-12", end_date="2026-11-12")
    assert filtered["total"] == 1
    assert filtered["items"][0]["production_date"] == "2026-11-12"


def test_previous_record_skips_missing_dates(conn):
    record_service.create_record(conn, _data(production_date="2026-11-10"))
    record_service.create_record(conn, _data(production_date="2026-11-13"))
    previous = record_service.get_previous_record(conn, "2026-11-13")
    assert previous["production_date"] == "2026-11-10"
    assert record_service.get_previous_record(conn, "2026-11-10") is None


def test_trend_points_ascending_and_limited(conn):
    for day in ("2026-11-11", "2026-11-12", "2026-11-13"):
        record_service.create_record(conn, _data(production_date=day))

    points = record_service.get_trend_points(conn, 7)
    assert [point["production_date"] for point in points] == [
        "2026-11-11", "2026-11-12", "2026-11-13",
    ]

    limited = record_service.get_trend_points(conn, 2)
    assert [point["production_date"] for point in limited] == ["2026-11-12", "2026-11-13"]
