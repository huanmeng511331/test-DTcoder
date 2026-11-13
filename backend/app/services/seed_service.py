"""演示初始数据：首次启动时自动写入最近 7 天的模拟生产数据。"""

from datetime import date, datetime, timedelta

from ..config import DATE_FORMAT, DATETIME_FORMAT
from ..models.production import TABLE_NAME

# (距今日偏移天数, 原油产量吨, 天然气产量万方, 注水量方, 能耗万千瓦时, 停井数, 异常说明)
SEED_TEMPLATES = [
    (-6, 1285.4, 92.3, 3250, 47.6, 0, ""),
    (-5, 1290.2, 91.8, 3180, 46.9, 1, "3号注水泵例行保养，午后恢复正常"),
    (-4, 1272.6, 93.5, 3210, 48.2, 0, ""),
    (-3, 1268.9, 90.7, 3160, 47.1, 0, ""),
    (-2, 1241.3, 88.4, 3080, 49.5, 2, "7-12井因地面管线压力异常临时关井"),
    (-1, 1176.4, 85.2, 3050, 50.3, 1, "5-8井抽油机皮带更换，预计明日恢复生产"),
    (0, 1190.5, 87.6, 3095, 48.8, 0, ""),
]


def seed_initial_data_if_empty(conn) -> int:
    """表为空时写入近 7 天模拟数据（含一条降幅超阈值与停井异常的演示日），返回写入条数。"""
    total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
    if total > 0:
        return 0

    today = date.today()
    now = datetime.now().strftime(DATETIME_FORMAT)
    inserted = 0
    for offset, oil, gas, water, energy, wells, abnormal in SEED_TEMPLATES:
        production_date = (today + timedelta(days=offset)).strftime(DATE_FORMAT)
        conn.execute(
            f"""
            INSERT INTO {TABLE_NAME}
                (production_date, crude_oil_output, natural_gas_output, water_injection,
                 energy_consumption, shutdown_well_count, abnormal_description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (production_date, oil, gas, water, energy, wells, abnormal, now, now),
        )
        inserted += 1
    conn.commit()
    return inserted
