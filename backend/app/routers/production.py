"""生产数据与日报 REST API 路由。"""

from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import get_connection
from ..schemas.production import (
    DailyReport,
    ProductionRecordIn,
    ProductionRecordOut,
    ProductionRecordPage,
    TrendPoint,
)
from ..services import record_service, report_service

router = APIRouter()


def _db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _ensure_date_order(start_date: date_type | None, end_date: date_type | None) -> None:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date 不能晚于 end_date")


@router.get("/production-records", response_model=ProductionRecordPage)
def list_production_records(
    start_date: date_type | None = Query(default=None, description="起始日期 YYYY-MM-DD"),
    end_date: date_type | None = Query(default=None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    conn=Depends(_db),
):
    _ensure_date_order(start_date, end_date)
    return record_service.list_records(
        conn,
        start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
        end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
        page=page,
        page_size=page_size,
    )


@router.get("/production-records/{record_id}", response_model=ProductionRecordOut)
def get_production_record(record_id: int, conn=Depends(_db)):
    record = record_service.get_record(conn, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="生产记录不存在")
    return record


@router.post("/production-records", response_model=ProductionRecordOut, status_code=201)
def create_production_record(payload: ProductionRecordIn, conn=Depends(_db)):
    try:
        return record_service.create_record(conn, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.put("/production-records/{record_id}", response_model=ProductionRecordOut)
def update_production_record(record_id: int, payload: ProductionRecordIn, conn=Depends(_db)):
    try:
        record = record_service.update_record(conn, record_id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if record is None:
        raise HTTPException(status_code=404, detail="生产记录不存在")
    return record


@router.get("/daily-reports/{report_date}", response_model=DailyReport)
def get_daily_report(report_date: date_type, conn=Depends(_db)):
    date_text = report_date.strftime("%Y-%m-%d")
    record = record_service.get_record_by_date(conn, date_text)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{date_text} 暂无生产数据，请先录入后再生成日报")
    previous_record = record_service.get_previous_record(conn, date_text)
    return report_service.build_daily_report(record, previous_record)


@router.get("/production-trends", response_model=list[TrendPoint])
def get_production_trends(days: int = Query(default=7, ge=1, le=30), conn=Depends(_db)):
    return record_service.get_trend_points(conn, days)
