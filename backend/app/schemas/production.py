"""生产记录与日报的请求/响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductionRecordIn(BaseModel):
    """新增/修改生产数据请求体。"""

    production_date: str = Field(..., description="生产日期，格式 YYYY-MM-DD")
    crude_oil_output: float = Field(..., ge=0, description="原油产量（吨）")
    natural_gas_output: float = Field(..., ge=0, description="天然气产量（万立方米）")
    water_injection: float = Field(..., ge=0, description="注水量（立方米）")
    energy_consumption: float = Field(..., ge=0, description="能耗（万千瓦时）")
    shutdown_well_count: int = Field(default=0, ge=0, description="停井数量（口）")
    abnormal_description: str = Field(default="", max_length=500, description="异常说明")

    @field_validator("production_date")
    @classmethod
    def _validate_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("production_date 必须是 YYYY-MM-DD 格式的有效日期") from exc
        return value


class ProductionRecordOut(BaseModel):
    """生产数据响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    production_date: str
    crude_oil_output: float
    natural_gas_output: float
    water_injection: float
    energy_consumption: float
    shutdown_well_count: int
    abnormal_description: str
    created_at: str
    updated_at: str


class ProductionRecordPage(BaseModel):
    """分页查询结果。"""

    items: list[ProductionRecordOut]
    total: int
    page: int
    page_size: int


class MetricComparison(BaseModel):
    """单指标环比对比。"""

    metric: str
    label: str
    unit: str
    current: float
    previous: float | None = None
    delta: float | None = None
    change_ratio: float | None = None
    direction: str
    alert: str | None = None


class AlertItem(BaseModel):
    """日报突出提示项。"""

    level: str = "warning"
    scope: str
    message: str


class DailyReport(BaseModel):
    """结构化生产日报。"""

    report_date: str
    record: ProductionRecordOut
    previous_record: ProductionRecordOut | None = None
    comparisons: list[MetricComparison]
    alerts: list[AlertItem]
    summary: list[str]
    generated_at: str


class TrendPoint(BaseModel):
    """趋势图数据点。"""

    production_date: str
    crude_oil_output: float
    natural_gas_output: float
    water_injection: float
    energy_consumption: float
