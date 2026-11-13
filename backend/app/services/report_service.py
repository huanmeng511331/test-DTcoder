"""日报生成业务逻辑：环比计算、阈值告警与规则摘要。"""

from datetime import datetime

from ..config import DATETIME_FORMAT, METRIC_THRESHOLDS

ALERT_LEVEL_WARNING = "warning"

DIRECTION_TEXT = {"up": "上升", "down": "下降", "flat": "持平"}


def compute_comparison(metric: str, current: float, previous: float | None) -> dict:
    """计算单指标环比，并按阈值生成突出提示。"""
    spec = METRIC_THRESHOLDS[metric]
    comparison = {
        "metric": metric,
        "label": spec["label"],
        "unit": spec["unit"],
        "current": current,
        "previous": previous,
        "delta": None,
        "change_ratio": None,
        "direction": "flat",
        "alert": None,
    }
    if previous is None:
        return comparison

    delta = round(current - previous, 2)
    change_ratio = round((current - previous) / previous * 100, 1) if previous != 0 else None
    direction = "up" if delta > 0 else ("down" if delta < 0 else "flat")
    comparison.update(delta=delta, change_ratio=change_ratio, direction=direction)
    comparison["alert"] = _build_metric_alert(spec, direction, change_ratio)
    return comparison


def _build_metric_alert(spec: dict, direction: str, change_ratio: float | None) -> str | None:
    if change_ratio is None:
        return None
    ratio = abs(change_ratio)
    if direction == "down" and spec["drop"] is not None and ratio > spec["drop"]:
        return f"{spec['label']}较前一日下降 {ratio}%，超过 {spec['drop']}% 关注阈值"
    if direction == "up" and spec["rise"] is not None and ratio > spec["rise"]:
        return f"{spec['label']}较前一日上升 {ratio}%，超过 {spec['rise']}% 关注阈值"
    return None


def build_alerts(record: dict, comparisons: list[dict]) -> list[dict]:
    """汇总日报突出提示：异常说明、停井数量与核心指标超阈值。"""
    alerts: list[dict] = []
    wells = record["shutdown_well_count"]
    if wells > 0:
        alerts.append({
            "level": ALERT_LEVEL_WARNING,
            "scope": "shutdown_wells",
            "message": f"当日停井 {wells} 口，请核实停井原因与恢复计划",
        })
    if record["abnormal_description"]:
        alerts.append({
            "level": ALERT_LEVEL_WARNING,
            "scope": "abnormal",
            "message": f"异常说明：{record['abnormal_description']}",
        })
    for comparison in comparisons:
        if comparison["alert"]:
            alerts.append({
                "level": ALERT_LEVEL_WARNING,
                "scope": comparison["metric"],
                "message": comparison["alert"],
            })
    return alerts


def _format_ratio(comparison: dict) -> str:
    if comparison["change_ratio"] is None:
        return "无前一日数据"
    if comparison["direction"] == "flat":
        return "与前一日持平"
    return f"较前一日{DIRECTION_TEXT[comparison['direction']]} {abs(comparison['change_ratio']):.1f}%"


def build_summary(record: dict, comparisons: list[dict], alerts: list[dict]) -> list[str]:
    """按规则模板生成 3-5 条日报摘要。"""
    oil, gas, water, energy = comparisons
    items: list[str] = []
    if oil["previous"] is None:
        items.append(
            f"{record['production_date']} 生产数据为首次录入：原油产量 {oil['current']:.1f} 吨、"
            f"天然气产量 {gas['current']:.1f} 万立方米。"
        )
        items.append(
            f"注水量 {water['current']:.0f} 立方米、能耗 {energy['current']:.1f} 万千瓦时；"
            f"停井 {record['shutdown_well_count']} 口。"
        )
        if record["abnormal_description"]:
            items.append(f"异常事项：{record['abnormal_description']}。")
        items.append("暂无前一日数据，环比指标将于次日生成。")
    else:
        items.append(
            f"原油日产量 {oil['current']:.1f} 吨，{_format_ratio(oil)}（增减 {oil['delta']:+.1f} 吨）。"
        )
        items.append(f"天然气日产量 {gas['current']:.1f} 万立方米，{_format_ratio(gas)}。")
        items.append(
            f"注水量 {water['current']:.0f} 立方米（{_format_ratio(water)}）；"
            f"能耗 {energy['current']:.1f} 万千瓦时（{_format_ratio(energy)}）。"
        )
        if record["shutdown_well_count"] > 0 or record["abnormal_description"]:
            parts = []
            if record["shutdown_well_count"] > 0:
                parts.append(f"停井 {record['shutdown_well_count']} 口")
            if record["abnormal_description"]:
                parts.append(f"异常说明：{record['abnormal_description']}")
            items.append("当日重点关注：" + "；".join(parts) + "。")
        items.append(
            "请关注上述提示事项并及时跟进处理。"
            if alerts
            else "各项生产指标总体平稳，无突出异常事项。"
        )
    return items[:5]


def build_daily_report(record: dict, previous_record: dict | None) -> dict:
    """生成指定日期的结构化日报数据。"""
    comparisons = [
        compute_comparison(
            metric,
            record[metric],
            previous_record[metric] if previous_record else None,
        )
        for metric in METRIC_THRESHOLDS
    ]
    alerts = build_alerts(record, comparisons)
    summary = build_summary(record, comparisons, alerts)
    return {
        "report_date": record["production_date"],
        "record": record,
        "previous_record": previous_record,
        "comparisons": comparisons,
        "alerts": alerts,
        "summary": summary,
        "generated_at": datetime.now().strftime(DATETIME_FORMAT),
    }
