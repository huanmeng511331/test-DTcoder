"""应用配置：路径、业务阈值与分页常量。"""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "demo.db"

DB_PATH_ENV = "DEMO_DB_PATH"

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日报突出提示阈值（较前一日变化百分比；None 表示该方向不设阈值）
METRIC_THRESHOLDS = {
    "crude_oil_output": {"label": "原油产量", "unit": "吨", "drop": 5.0, "rise": None},
    "natural_gas_output": {"label": "天然气产量", "unit": "万立方米", "drop": 5.0, "rise": None},
    "water_injection": {"label": "注水量", "unit": "立方米", "drop": 10.0, "rise": None},
    "energy_consumption": {"label": "能耗", "unit": "万千瓦时", "drop": None, "rise": 10.0},
}

DEFAULT_TREND_DAYS = 7
MAX_TREND_DAYS = 30

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


def get_db_path() -> Path:
    """返回 SQLite 数据库文件路径，支持 DEMO_DB_PATH 环境变量覆盖。"""
    return Path(os.environ.get(DB_PATH_ENV, str(DEFAULT_DB_PATH)))
