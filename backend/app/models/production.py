"""生产记录数据模型：SQLite 表结构与行映射。"""

TABLE_NAME = "production_records"

TABLE_DDL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    production_date      TEXT    NOT NULL UNIQUE,
    crude_oil_output     REAL    NOT NULL,
    natural_gas_output   REAL    NOT NULL,
    water_injection      REAL    NOT NULL,
    energy_consumption   REAL    NOT NULL,
    shutdown_well_count  INTEGER NOT NULL DEFAULT 0,
    abnormal_description TEXT    NOT NULL DEFAULT '',
    created_at           TEXT    NOT NULL,
    updated_at           TEXT    NOT NULL
);
"""

RECORD_FIELDS = (
    "id",
    "production_date",
    "crude_oil_output",
    "natural_gas_output",
    "water_injection",
    "energy_consumption",
    "shutdown_well_count",
    "abnormal_description",
    "created_at",
    "updated_at",
)


def row_to_dict(row) -> dict:
    """将 sqlite3.Row 转换为业务字典。"""
    return {field: row[field] for field in RECORD_FIELDS}
