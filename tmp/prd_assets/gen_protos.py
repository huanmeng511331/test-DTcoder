# -*- coding: utf-8 -*-
"""生成 5 张页面低保真原型 PNG（Element Plus 风格基线）。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *  # noqa
from PIL import Image, ImageDraw

OUT = ".agents/20261113-HSE隐患上报与闭环/assets"
os.makedirs(OUT, exist_ok=True)


def dim_overlay(img, alpha=105):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, img.size[0], img.size[1]], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def radio(d, x, y, label, checked, size=18):
    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=CARD, outline=PRIMARY if checked else T3, width=2)
    if checked:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=PRIMARY)
    d.text((x + 20, y), label, font=font(size), fill=T2, anchor="lm")


# ---------------------------------------------------------------- 图3-1 台账页
def page_list():
    W, H = 1500, 940
    img, d = canvas(W, H)
    x0 = admin_frame(d, W, H, "隐患台账")
    text(d, (x0, 90), "隐患台账", 26, T1, True)
    btn(d, [1336, 80, 1476, 118], "＋ 新增上报", "primary")

    # 筛选卡片
    rrect(d, [244, 132, 1476, 232], 10)
    text(d, (268, 176), "状态", 18, T2, anchor="lm")
    input_box(d, [316, 152, 470, 196], value="全部", select=True)
    text(d, (500, 176), "等级", 18, T2, anchor="lm")
    input_box(d, [548, 152, 702, 196], value="全部", select=True)
    text(d, (732, 176), "类型", 18, T2, anchor="lm")
    input_box(d, [780, 152, 934, 196], value="全部", select=True)
    text(d, (964, 176), "关键字", 18, T2, anchor="lm")
    input_box(d, [1012, 152, 1240, 196], placeholder="编号 / 位置 / 描述关键字")
    btn(d, [1268, 152, 1348, 196], "查 询", "primary")
    btn(d, [1360, 152, 1440, 196], "重 置", "plain")

    # 表格卡片
    rrect(d, [244, 252, 1476, 828], 10)
    cols = [(280, 470, "编号"), (470, 610, "隐患类型"), (610, 720, "等级"),
            (720, 990, "位置"), (990, 1100, "责任人"), (1100, 1280, "整改期限"),
            (1280, 1420, "状态"), (1420, 1476, "操作")]
    d.rectangle([245, 253, 1475, 344], fill=HEADER_BG)
    for a, b, name in cols:
        text(d, (a + 12, 298), name, 17, T2, anchor="lm")
    rows = [
        ("YH-20261113-001", "消防安全", "一般", "3号厂房东侧消防通道", "—", "2026-11-18", "待审核", None),
        ("YH-20261112-002", "用电安全", "重大", "配电室B柜旁杂物堆放", "李强", "2026-11-14", "整改中", None),
        ("YH-20261112-003", "消防安全", "一般", "2号仓库灭火器过期", "李强", "2026-11-18", "整改中", None),
        ("YH-20261111-004", "设备设施", "较大", "2号车间行车限位失效", "刘洋", "2026-11-16", "待验收", None),
        ("YH-20261111-005", "环境保护", "一般", "危废暂存间标识缺失", "赵敏", "2026-11-15", "待验收", None),
        ("YH-20261109-007", "用电安全", "一般", "1号厂房插座松动", "刘洋", "2026-11-12", "整改中", "超期"),
        ("YH-20261109-008", "消防安全", "较大", "3号厂房疏散指示损坏", "李强", "2026-11-13", "待验收", None),
        ("YH-20261106-006", "职业健康", "一般", "喷涂工位防尘面具破损", "张伟", "2026-11-08", "整改中", "超期"),
    ]
    for i, (no, typ, lv, loc, owner, due, st, extra) in enumerate(rows):
        ry = 344 + i * 58
        d.line([(245, ry), (1475, ry)], fill=TBORDER, width=1)
        overdue = extra == "超期"
        text(d, (292, ry + 29), no, 17, T1, anchor="lm")
        text(d, (482, ry + 29), typ, 17, T2, anchor="lm")
        tag(d, 622, ry + 16, lv, LEVEL_KIND[lv], 15, 26)
        ellipsis(d, (732, ry + 29), loc, 246, 17, T2)
        text(d, (1002, ry + 29), owner, 17, T2, anchor="lm")
        text(d, (1112, ry + 29), due, 17, DANGER if overdue else T2, anchor="lm")
        if overdue:
            tag(d, 1292, ry + 8, st, STATUS_KIND[st], 15, 24)
            tag(d, 1292, ry + 30, "超期", "danger", 15, 24)
        else:
            tag(d, 1292, ry + 16, st, STATUS_KIND[st], 15, 26)
        text(d, (1448, ry + 29), "查看", 17, PRIMARY, anchor="mm")
    d.line([(245, 808), (1475, 808)], fill=TBORDER, width=1)

    # 分页
    text(d, (252, 862), "共 15 条", 17, T2, anchor="lm")
    pages = [("‹", False), ("1", True), ("2", False), ("›", False)]
    for i, (p, on) in enumerate(pages):
        bx = 1290 + i * 44
        d.rounded_rectangle([bx, 844, bx + 36, 880], radius=6, fill=CARD,
                            outline=PRIMARY if on else BORDER, width=1)
        d.text((bx + 18, 862), p, font=font(17), fill=PRIMARY if on else T2, anchor="mm")
    img.save(f"{OUT}/proto_hazard_list.png")


# ---------------------------------------------------------------- 图3-2 上报弹窗
def page_dialog():
    W, H = 1500, 940
    img, d = canvas(W, H)
    admin_frame(d, W, H, "隐患台账")
    text(d, (244, 90), "隐患台账", 26, T1, True)
    img = dim_overlay(img)
    d = ImageDraw.Draw(img)

    rrect(d, [430, 120, 1070, 800], 12, CARD, BORDER, 1)
    text(d, (460, 152), "隐患上报", 21, T1, True, "lm")
    d.line([(1030, 146), (1044, 160)], fill=T3, width=2)
    d.line([(1030, 160), (1044, 146)], fill=T3, width=2)
    d.line([(430, 182), (1070, 182)], fill=TBORDER, width=1)

    def lab(y, s, req=True):
        if req:
            d.text((470, y), "*", font=font(18), fill=DANGER, anchor="lm")
        d.text((484, y), s, font=font(18), fill=T2, anchor="lm")

    lab(210, "上报人");   input_box(d, [620, 192, 1010, 228], placeholder="请选择上报人", select=True)
    lab(268, "隐患位置"); input_box(d, [620, 250, 1010, 286], placeholder="请输入隐患位置")
    lab(326, "隐患类型"); input_box(d, [620, 308, 1010, 344], placeholder="请选择隐患类型", select=True)
    lab(384, "隐患等级")
    radio(d, 640, 384, "一般", True)
    radio(d, 750, 384, "较大", False)
    radio(d, 860, 384, "重大", False)
    lab(442, "问题描述")
    d.rounded_rectangle([620, 430, 1010, 560], radius=6, fill=CARD, outline=BORDER, width=1)
    d.text((632, 444), "请描述隐患情况（200 字以内）", font=font(17), fill=T4, anchor="la")
    lab(588, "整改期限"); input_box(d, [620, 570, 1010, 606], placeholder="选择日期", select=True)
    lab(646, "图片 URL", req=False); input_box(d, [620, 628, 1010, 664], placeholder="https://…（选填）")

    btn(d, [830, 712, 920, 760], "取 消", "plain")
    btn(d, [934, 712, 1024, 760], "提 交", "primary")
    img.save(f"{OUT}/proto_report_dialog.png")


# ---------------------------------------------------------------- 图3-3 详情页
def page_detail():
    W, H = 1500, 1000
    img, d = canvas(W, H)
    x0 = admin_frame(d, W, H, "隐患台账")
    text(d, (x0, 90), "隐患详情", 26, T1, True)
    text(d, (1476, 90), "← 返回台账", 18, T2, anchor="rm")

    # 基本信息
    rrect(d, [244, 128, 1476, 478], 10)
    text(d, (272, 168), "YH-20261113-001", 22, T1, True, "lm")
    tag(d, 520, 154, "待审核", "warning")
    tag(d, 520 + tag_w(d, "待审核") + 10, 154, "一般", "info")
    d.line([(268, 200), (1452, 200)], fill=TBORDER, width=1)
    grid = [("隐患类型", "消防安全"), ("隐患位置", "3号厂房东侧消防通道"),
            ("上报人", "张伟"), ("上报时间", "2026-11-13 09:12"),
            ("责任人", "—（未分派）"), ("整改期限", "2026-11-18")]
    for i, (k, v) in enumerate(grid):
        r, c = divmod(i, 2)
        y = 228 + r * 46
        kx = 272 if c == 0 else 800
        text(d, (kx, y + 10), k, 17, T3, anchor="lm")
        text(d, (kx + 92, y + 10), v, 17, T4 if k == "责任人" else T1, anchor="lm")
    text(d, (272, 380), "问题描述", 17, T3, anchor="lm")
    text(d, (364, 368), "消防通道堆放杂物，影响应急疏散，存在人员疏散受阻风险。", 17, T2, anchor="la")
    text(d, (272, 434), "图片", 17, T3, anchor="lm")
    ph = [364, 406, 504, 464]
    d.rounded_rectangle(ph, radius=6, fill="#fafafa", outline=T4, width=1)
    d.text(((364 + 504) / 2, 435), "图片占位", font=font(15), fill=T4, anchor="mm")
    text(d, (520, 435), "—（未提供图片 URL）", 17, T3, anchor="lm")

    # 整改信息
    rrect(d, [244, 496, 1476, 652], 10)
    text(d, (272, 520), "整改信息", 20, T1, True, "lm")
    g2 = [("整改要求", "2026-11-18 前完成整改并复核"), ("整改措施", "待责任人提交"),
          ("整改结果", "待责任人提交"), ("验收意见", "待安全管理人员验收")]
    for i, (k, v) in enumerate(g2):
        r, c = divmod(i, 2)
        y = 560 + r * 46
        kx = 272 if c == 0 else 800
        text(d, (kx, y + 10), k, 17, T3, anchor="lm")
        text(d, (kx + 92, y + 10), v, 17, T2 if r == 0 and c == 0 else T4, anchor="lm")

    # 状态流转记录
    rrect(d, [244, 670, 880, 952], 10)
    text(d, (272, 694), "状态流转记录", 20, T1, True, "lm")
    steps = [("上报提交", "张伟 · 2026-11-13 09:12 · 提交隐患信息，等待审核", True),
             ("审核分派", "待安全管理人员处理", False),
             ("提交整改", "待责任人处理", False),
             ("验收关闭", "待验收通过后关闭", False)]
    for i, (act, meta, done) in enumerate(steps):
        y = 740 + i * 56
        if i < len(steps) - 1:
            d.line([(300, y + 10), (300, y + 56)], fill=TBORDER, width=2)
        if done:
            d.ellipse([292, y - 8, 308, y + 8], fill=PRIMARY)
        else:
            d.ellipse([292, y - 8, 308, y + 8], fill=CARD, outline=T4, width=2)
        text(d, (322, y - 9), act, 18, T1 if done else T3, True, "lm")
        text(d, (322, y + 11), meta, 15, T3 if done else T4, anchor="lm")

    # 操作区（待审核 × 安全管理人员）
    rrect(d, [900, 670, 1476, 952], 10)
    text(d, (928, 694), "审核并分派", 20, T1, True, "lm")
    tag(d, 1080, 682, "当前角色：安全管理人员", "primary", 15, 26)

    def lab2(y, s, req=True):
        if req:
            d.text((928, y), "*", font=font(18), fill=DANGER, anchor="lm")
        d.text((942, y), s, font=font(17), fill=T2, anchor="lm")

    lab2(736, "责任人");   input_box(d, [1040, 718, 1448, 754], placeholder="请选择责任人", select=True)
    lab2(792, "整改期限", req=False); input_box(d, [1040, 774, 1448, 810], value="2026-11-18", select=True)
    lab2(848, "审核意见", req=False); input_box(d, [1040, 830, 1448, 866], placeholder="选填，可填写审核说明")
    btn(d, [1040, 892, 1170, 932], "提交分派", "primary")
    text(d, (1184, 912), "提交后状态变更为「整改中」", 15, T4, anchor="lm")
    img.save(f"{OUT}/proto_detail.png")


# ---------------------------------------------------------------- 图3-4 操作区形态
def page_actions():
    W, H = 1560, 800
    img, d = canvas(W, H)

    def panel(box, title):
        rrect(d, box, 10)
        text(d, (box[0] + 24, box[1] + 22), title, 19, T1, True, "lm")
        d.line([(box[0] + 1, box[1] + 44), (box[2] - 1, box[1] + 44)], fill=TBORDER, width=1)

    # A 待审核 × 安全管理人员
    panel([40, 40, 740, 380], "A｜待审核 × 安全管理人员")
    d.text((64, 128), "*", font=font(18), fill=DANGER, anchor="lm")
    text(d, (78, 128), "责任人", 17, T2, anchor="lm")
    input_box(d, [190, 104, 700, 140], placeholder="请选择责任人", select=True)
    text(d, (64, 174), "整改期限", 17, T2, anchor="lm")
    input_box(d, [190, 156, 700, 192], value="2026-11-18", select=True)
    text(d, (64, 220), "审核意见", 17, T2, anchor="lm")
    input_box(d, [190, 208, 700, 244], placeholder="选填，可填写审核说明")
    btn(d, [190, 288, 310, 328], "提交分派", "primary")
    text(d, (324, 308), "提交后状态 → 整改中", 15, T4, anchor="lm")

    # B 整改中 × 责任人
    panel([820, 40, 1520, 380], "B｜整改中 × 责任人")
    d.text((844, 128), "*", font=font(18), fill=DANGER, anchor="lm")
    text(d, (858, 128), "整改措施", 17, T2, anchor="lm")
    d.rounded_rectangle([940, 104, 1480, 180], radius=6, fill=CARD, outline=BORDER, width=1)
    d.text((952, 116), "请输入整改措施", font=font(17), fill=T4, anchor="la")
    d.text((844, 216), "*", font=font(18), fill=DANGER, anchor="lm")
    text(d, (858, 216), "整改结果", 17, T2, anchor="lm")
    input_box(d, [940, 200, 1480, 236], placeholder="请输入整改结果（如：已清理并设置禁放标识）")
    btn(d, [940, 288, 1060, 328], "提交整改", "primary")
    text(d, (1074, 308), "提交后状态 → 待验收", 15, T4, anchor="lm")

    # C 待验收 × 安全管理人员
    panel([40, 420, 740, 760], "C｜待验收 × 安全管理人员")
    text(d, (64, 504), "验收结论", 17, T2, anchor="lm")
    radio(d, 210, 504, "验收通过", True)
    radio(d, 350, 504, "验收退回", False)
    text(d, (64, 550), "验收意见", 17, T2, anchor="lm")
    input_box(d, [190, 532, 700, 568], placeholder="选填，退回时建议填写原因")
    btn(d, [190, 660, 310, 700], "验收通过", "primary")
    d.rounded_rectangle([330, 660, 450, 700], radius=6, fill=CARD, outline=DANGER_BD, width=1)
    d.text((390, 680), "验收退回", font=font(18), fill=DANGER, anchor="mm")
    text(d, (464, 680), "通过 → 已关闭；退回 → 整改中", 15, T4, anchor="lm")

    # D 其他组合
    panel([820, 420, 1520, 760], "D｜其他「角色 × 状态」组合")
    rrect(d, [860, 500, 1480, 610], 8, INFO_BG, INFO_BD, 1)
    d.text((1170, 540), "当前角色为「责任人」，", font=font(18), fill=T3, anchor="mm")
    d.text((1170, 570), "隐患待安全管理人员验收，暂无可执行操作。", font=font(18), fill=T3, anchor="mm")
    img.save(f"{OUT}/proto_detail_actions.png")


# ---------------------------------------------------------------- 图3-5 看板页
def page_dashboard():
    W, H = 1500, 940
    img, d = canvas(W, H)
    x0 = admin_frame(d, W, H, "统计看板")
    text(d, (x0, 90), "统计看板", 26, T1, True)
    text(d, (1476, 90), "数据截至 2026-11-13", 16, T4, anchor="rm")

    cards = [("待审核", 1, WARNING), ("整改中", 4, PRIMARY), ("待验收", 3, INFO),
             ("已关闭", 7, SUCCESS), ("超期未整改", 2, DANGER)]
    for i, (name, v, c) in enumerate(cards):
        cx0 = 244 + i * 246
        rrect(d, [cx0, 128, cx0 + 236, 248], 10)
        d.text((cx0 + 118, 176), str(v), font=font(40, True), fill=c, anchor="mm")
        d.text((cx0 + 118, 220), name, font=font(18), fill=T2, anchor="mm")

    # 等级分布
    rrect(d, [244, 268, 648, 900], 10)
    text(d, (272, 296), "隐患等级分布", 20, T1, True, "lm")
    base, top = 810, 410
    d.line([(300, top - 50), (300, base)], fill=BORDER, width=2)
    d.line([(300, base), (620, base)], fill=BORDER, width=2)
    bars = [("一般", 8, PRIMARY), ("较大", 5, PRIMARY_L), ("重大", 2, "#a0cfff")]
    for i, (name, v, c) in enumerate(bars):
        cx = 370 + i * 100
        h = v / 8 * (base - (top - 50))
        d.rounded_rectangle([cx - 40, base - h, cx + 40, base], radius=4, fill=c)
        d.text((cx, base - h - 16), str(v), font=font(20, True), fill=T2, anchor="mm")
        d.text((cx, base + 22), name, font=font(17), fill=T3, anchor="mm")

    # 类型分布（饼图）
    import math
    rrect(d, [658, 268, 1062, 900], 10)
    text(d, (686, 296), "隐患类型分布", 20, T1, True, "lm")
    cxp, cyp, r = 810, 560, 130
    data = [("消防安全", 4), ("用电安全", 3), ("设备设施", 3), ("环境保护", 2), ("职业健康", 2), ("其他", 1)]
    ang = -90.0
    for i, (name, v) in enumerate(data):
        a2 = ang + v / 15 * 360
        d.pieslice([cxp - r, cyp - r, cxp + r, cyp + r], ang, a2, fill=CHART_COLORS[i], outline=CARD, width=3)
        ang = a2
    for i, (name, v) in enumerate(data):
        ly = 400 + i * 42
        d.rectangle([952, ly - 7, 966, ly + 7], fill=CHART_COLORS[i])
        text(d, (976, ly), f"{name}  {v}", 16, T2, anchor="lm")

    # 近7日趋势
    rrect(d, [1072, 268, 1476, 900], 10)
    text(d, (1100, 296), "近 7 日新增 / 关闭趋势", 20, T1, True, "lm")
    d.line([(1116, 330), (1132, 330)], fill=PRIMARY, width=3)
    text(d, (1140, 330), "新增", 16, T2, anchor="lm")
    d.line([(1200, 330), (1216, 330)], fill=SUCCESS, width=3)
    text(d, (1224, 330), "关闭", 16, T2, anchor="lm")
    x1, x2, yb, scale = 1120, 1450, 800, 148
    for gy in range(4):
        y = yb - gy * scale
        d.line([(x1, y), (x2, y)], fill=TBORDER, width=1)
    xs = [x1 + i * (x2 - x1) / 6 for i in range(7)]
    for i, s in enumerate(["11-07", "11-08", "11-09", "11-10", "11-11", "11-12", "11-13"]):
        d.text((xs[i], yb + 22), s, font=font(14), fill=T3, anchor="mm")
    series = [("新增", [1, 1, 2, 0, 2, 2, 1], PRIMARY), ("关闭", [0, 0, 0, 2, 2, 3, 0], SUCCESS)]
    for _, vals, c in series:
        pts = [(x, yb - v * scale) for x, v in zip(xs, vals)]
        d.line(pts, fill=c, width=3)
        for p in pts:
            d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=CARD, outline=c, width=3)
    img.save(f"{OUT}/proto_dashboard.png")


if __name__ == "__main__":
    page_list(); page_dialog(); page_detail(); page_actions(); page_dashboard()
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(f"{OUT}/{f}"))
