"""日报生成业务逻辑测试：环比、阈值告警与摘要规则。"""

from app.services.report_service import build_alerts, build_daily_report, build_summary, compute_comparison


def _record(**overrides):
    base = {
        "production_date": "2026-11-13",
        "crude_oil_output": 1000.0,
        "natural_gas_output": 88.0,
        "water_injection": 3100.0,
        "energy_consumption": 40.0,
        "shutdown_well_count": 0,
        "abnormal_description": "",
    }
    base.update(overrides)
    return base


def _comparisons(record, previous):
    return [
        compute_comparison(metric, record[metric], previous[metric] if previous else None)
        for metric in ("crude_oil_output", "natural_gas_output", "water_injection", "energy_consumption")
    ]


def test_comparison_without_previous():
    result = compute_comparison("crude_oil_output", 1000.0, None)
    assert result["previous"] is None
    assert result["delta"] is None
    assert result["change_ratio"] is None
    assert result["alert"] is None


def test_comparison_up_down_flat():
    up = compute_comparison("crude_oil_output", 1050.0, 1000.0)
    assert up["direction"] == "up"
    assert up["delta"] == 50.0
    assert up["change_ratio"] == 5.0

    down = compute_comparison("crude_oil_output", 950.0, 1000.0)
    assert down["direction"] == "down"
    assert down["change_ratio"] == -5.0

    flat = compute_comparison("crude_oil_output", 1000.0, 1000.0)
    assert flat["direction"] == "flat"
    assert flat["alert"] is None


def test_drop_threshold_boundary():
    # 下降 5.5% 超过 5% 阈值 -> 告警
    alert_case = compute_comparison("crude_oil_output", 945.0, 1000.0)
    assert alert_case["alert"] is not None
    # 下降 4.5% 未超过阈值 -> 不告警
    ok_case = compute_comparison("crude_oil_output", 955.0, 1000.0)
    assert ok_case["alert"] is None
    # 恰好等于阈值 5% -> 不告警（阈值判定为严格大于）
    edge_case = compute_comparison("crude_oil_output", 950.0, 1000.0)
    assert edge_case["alert"] is None


def test_energy_rise_alert():
    rise = compute_comparison("energy_consumption", 45.0, 40.0)
    assert rise["direction"] == "up"
    assert rise["alert"] is not None
    assert "上升" in rise["alert"]

    mild = compute_comparison("energy_consumption", 43.0, 40.0)
    assert mild["alert"] is None


def test_alerts_include_wells_and_abnormal():
    record = _record(shutdown_well_count=2, abnormal_description="7-12井临时关井")
    alerts = build_alerts(record, _comparisons(record, None))
    scopes = {alert["scope"] for alert in alerts}
    assert "shutdown_wells" in scopes
    assert "abnormal" in scopes


def test_summary_length_and_content_with_previous():
    record = _record(crude_oil_output=945.0)
    previous = _record(production_date="2026-11-12")
    comparisons = _comparisons(record, previous)
    alerts = build_alerts(record, comparisons)
    summary = build_summary(record, comparisons, alerts)
    assert 3 <= len(summary) <= 5
    assert any("原油" in item for item in summary)
    assert any("天然气" in item for item in summary)
    assert any("注水量" in item for item in summary)


def test_summary_without_previous():
    record = _record()
    comparisons = _comparisons(record, None)
    summary = build_summary(record, comparisons, [])
    assert 3 <= len(summary) <= 5
    assert any("首次录入" in item for item in summary)


def test_build_daily_report_shape():
    record = _record(crude_oil_output=900.0)
    previous = _record(production_date="2026-11-12")
    report = build_daily_report(record, previous)
    assert report["report_date"] == "2026-11-13"
    assert len(report["comparisons"]) == 4
    assert report["alerts"], "原油下降 10% 应产生告警"
    assert 3 <= len(report["summary"]) <= 5
    assert report["previous_record"]["production_date"] == "2026-11-12"
