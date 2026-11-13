# -*- coding: utf-8 -*-
"""生成 2 张流程图 PNG（简洁流程图基线）。"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *  # noqa

OUT = ".agents/20261113-HSE隐患上报与闭环/assets"
os.makedirs(OUT, exist_ok=True)


def dash(d, p1, p2, color=T3, width=2, dash=9, gap=7):
    x1, y1 = p1; x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return
    ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
    t = 0.0
    while t < dist:
        t2 = min(t + dash, dist)
        d.line([(x1 + ux * t, y1 + uy * t), (x1 + ux * t2, y1 + uy * t2)], fill=color, width=width)
        t = t2 + gap


def dashed_arrow(d, pts, color=T3, width=2):
    for i in range(len(pts) - 2):
        dash(d, pts[i], pts[i + 1], color, width)
    dash(d, pts[-2], pts[-1], color, width, dash=9, gap=2)
    arrow(d, pts[-2], pts[-1], color=color, width=width, head=9)


# ------------------------------------------------------ 图2-1 泳道图
def loop_swimlane():
    W, H = 1760, 920
    img, d = canvas(W, H)
    text(d, (60, 30), "HSE 隐患上报与闭环 · 整体业务闭环（泳道图）", 24, T1, True, "lm")

    x0, x1, y0, y1 = 40, 1700, 64, 888
    lanes = [("上报人", "（现场人员）"), ("系统", ""), ("安全管理人员", ""), ("责任人", "（整改人）")]
    h = (y1 - y0) / 4
    d.rectangle([x0, y0, x1, y1], fill=CARD)
    d.rectangle([x0, y0, 190, y1], fill="#f5f7fa")
    for i in range(5):
        y = y0 + i * h
        d.line([(x0, y), (x1, y)], fill="#e4e7ed", width=2)
    d.line([(190, y0), (190, y1)], fill="#e4e7ed", width=2)
    d.rectangle([x0, y0, x1, y1], outline="#e4e7ed", width=2)
    for i, (a, b) in enumerate(lanes):
        cy = y0 + i * h + h / 2
        d.text((115, cy - (14 if b else 0)), a, font=font(21, True), fill=T1, anchor="mm")
        if b:
            d.text((115, cy + 16), b, font=font(16), fill=T3, anchor="mm")
    L1, L2, L3, L4 = 167, 373, 579, 785

    # 节点
    node_box(d, 260, L1, 150, 56, ["发现隐患"], bold=True)
    node_box(d, 450, L1, 150, 64, ["填写并提交", "上报表单"], bold=True)
    diamond(d, 680, L1, 150, 96, ["校验通过?"], bold=True)
    node_box(d, 680, L2, 240, 64, ["生成编号", "状态=待审核 · 写入台账"])
    node_box(d, 1080, L2, 180, 64, ["状态=整改中", "更新流转记录"])
    node_box(d, 1360, L2, 180, 64, ["状态=待验收", "更新流转记录"])
    node_box(d, 1565, L2, 180, 64, ["状态=已关闭", "看板统计同步"])
    node_box(d, 900, L3, 190, 64, ["审核隐患并分派", "责任人 / 整改期限"], bold=True)
    diamond(d, 1230, L3, 160, 100, ["验收通过?"], bold=True)
    node_box(d, 900, L4, 170, 64, ["整改执行并提交", "措施与结果"], bold=True)
    d.ellipse([1671, L2 - 14, 1699, L2 + 14], fill=T2)

    # 连线
    arrow(d, (335, L1), (375, L1))
    arrow(d, (525, L1), (605, L1))
    polyline_arrow(d, [(680, 119), (680, 90), (450, 90), (450, 135)])
    label_bg(d, (488, 76), "不通过：返回修改", 16, DANGER)
    arrow(d, (680, 215), (680, 341))
    label_bg(d, (692, 280), "通过", 16, T2)
    polyline_arrow(d, [(680, 405), (680, 460), (900, 460), (900, 547)])
    arrow(d, (900, 611), (900, 757))
    label_bg(d, (914, 684), "分派给责任人", 16, T2)
    dashed_arrow(d, [(960, 547), (960, 500), (1080, 500), (1080, 405)])
    polyline_arrow(d, [(985, 785), (1230, 785), (1230, 629)])
    label_bg(d, (1030, 803), "提交整改", 16, T2)
    dashed_arrow(d, [(985, 765), (1105, 765), (1105, 470), (1360, 470), (1360, 405)])
    polyline_arrow(d, [(1310, 579), (1565, 579), (1565, 405)])
    label_bg(d, (1350, 564), "通过：验收关闭", 16, T2)
    polyline_arrow(d, [(1230, 629), (1230, 850), (985, 850)])
    polyline_arrow(d, [(985, 850), (985, 817)])
    label_bg(d, (1100, 834), "退回：再次整改", 16, DANGER)
    arrow(d, (1657, L2), (1669, L2))

    text(d, (60, 906), "实线：业务操作流转        虚线：系统自动响应        ● 起点 / 终点        状态变化以「状态=××」标注于系统泳道",
         16, T3, anchor="lm")
    img.save(f"{OUT}/flow_business_loop.png")


# ------------------------------------------------------ 图2-2 状态流转图
def state_flow():
    W, H = 1240, 640
    img, d = canvas(W, H)
    text(d, (60, 30), "HSE 隐患上报与闭环 · 状态流转图（唯一合法迁移）", 24, T1, True, "lm")

    def state(cx, cy, label, kind, w=150, h=64):
        fg, bg, bd = KIND[kind]
        d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=12,
                            fill=bg, outline=fg, width=2)
        d.text((cx, cy), label, font=font(20, True), fill=fg, anchor="mm")

    start_end(d, 90, 340, 14)
    state(250, 340, "待审核", "warning")
    state(560, 220, "整改中", "primary")
    state(880, 220, "待验收", "info")
    state(1120, 220, "已关闭", "success")

    arrow(d, (104, 340), (173, 340))
    label_bg(d, (104, 368), "上报提交", 15, T2)
    polyline_arrow(d, [(250, 308), (250, 262), (485, 262), (485, 220)])
    label_bg(d, (300, 248), "审核并分派  assign", 15, T2)
    arrow(d, (635, 220), (803, 220))
    label_bg(d, (620, 198), "提交整改  rectification", 15, T2)
    arrow(d, (955, 220), (1043, 220))
    label_bg(d, (1000, 176), "验收通过  accepted=true", 15, SUCCESS)
    polyline_arrow(d, [(880, 252), (880, 342), (560, 342), (560, 252)])
    label_bg(d, (640, 364), "验收退回  accepted=false", 15, DANGER)

    rrect(d, [150, 470, 760, 566], 8, INFO_BG, INFO_BD, 1)
    text(d, (178, 498), "非法状态操作（如对「已关闭」隐患执行验收）→ 后端返回 HTTP 409", 17, T3, anchor="lm")
    text(d, (178, 530), "前端提示「当前状态已变化，请刷新后重试」（规则 R2）", 17, T3, anchor="lm")
    text(d, (150, 606), "节点配色与 2.2 状态标签约定一致：待审核=warning / 整改中=primary / 待验收=info / 已关闭=success",
         16, T3, anchor="lm")
    img.save(f"{OUT}/flow_state.png")


if __name__ == "__main__":
    loop_swimlane(); state_flow()
    for f in ["flow_business_loop.png", "flow_state.png"]:
        print(f, os.path.getsize(f"{OUT}/{f}"))
