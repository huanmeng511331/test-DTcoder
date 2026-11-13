# -*- coding: utf-8 -*-
"""PRD 图件绘制样式库：Element Plus 风格低保真线框 + 简洁流程图（用户确认基线）。"""
from PIL import Image, ImageDraw, ImageFont

FDIR = "tmp/fonts"

# Element Plus 色板
BG = "#f5f7fa"; CARD = "#ffffff"; BORDER = "#dcdfe6"; TBORDER = "#ebeef5"
T1 = "#303133"; T2 = "#606266"; T3 = "#909399"; T4 = "#c0c4cc"
PRIMARY = "#409EFF"; PRIMARY_BG = "#ecf5ff"; PRIMARY_BD = "#d9ecff"; PRIMARY_L = "#79bbff"
SUCCESS = "#67C23A"; SUCCESS_BG = "#f0f9eb"; SUCCESS_BD = "#e1f3d8"
WARNING = "#E6A23C"; WARNING_BG = "#fdf6ec"; WARNING_BD = "#faecd8"
DANGER = "#F56C6C"; DANGER_BG = "#fef0f0"; DANGER_BD = "#fde2e2"
INFO = "#909399"; INFO_BG = "#f4f4f5"; INFO_BD = "#e9e9eb"
HEADER_BG = "#fafafa"
STATUS_KIND = {"待审核": "warning", "整改中": "primary", "待验收": "info", "已关闭": "success", "超期": "danger"}
LEVEL_KIND = {"一般": "info", "较大": "warning", "重大": "danger"}
CHART_COLORS = ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399", "#C0C4CC"]

_fonts = {}
def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        name = "NotoSansSC-Bold.otf" if bold else "NotoSansSC-Regular.otf"
        _fonts[key] = ImageFont.truetype(f"{FDIR}/{name}", size)
    return _fonts[key]

def canvas(w, h, bg=BG):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

def hex_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def tw(d, s, size, bold=False):
    return d.textlength(s, font=font(size, bold))

def text(d, xy, s, size=18, color=T1, bold=False, anchor="la"):
    d.text(xy, s, font=font(size, bold), fill=color, anchor=anchor)

def rrect(d, box, r=8, fill=CARD, outline=BORDER, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def wrap(s, max_w, size, bold=False, max_lines=None):
    lines, cur = [], ""
    for ch in s:
        if font(size, bold).getlength(cur + ch) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:-1] + "…"
    return lines

def ellipsis(d, xy, s, max_w, size=18, color=T2, bold=False):
    w = tw(d, s, size, bold)
    if w <= max_w:
        d.text(xy, s, font=font(size, bold), fill=color, anchor="la")
        return
    out = s
    while out and tw(d, out + "…", size, bold) > max_w:
        out = out[:-1]
    d.text(xy, out + "…", font=font(size, bold), fill=color, anchor="la")

KIND = {
    "primary": (PRIMARY, PRIMARY_BG, PRIMARY_BD),
    "success": (SUCCESS, SUCCESS_BG, SUCCESS_BD),
    "warning": (WARNING, WARNING_BG, WARNING_BD),
    "danger": (DANGER, DANGER_BG, DANGER_BD),
    "info": (INFO, INFO_BG, INFO_BD),
}

def tag(d, x, y, label, kind="primary", size=16, h=26):
    """胶囊标签，返回占用宽度。"""
    fg, bg, bd = KIND[kind]
    w = tw(d, label, size) + 22
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg, outline=bd, width=1)
    d.text((x + w / 2, y + h / 2), label, font=font(size), fill=fg, anchor="mm")
    return w

def tag_w(d, label, size=16):
    return tw(d, label, size) + 22

def btn(d, box, label, kind="primary", size=18, r=6):
    if kind == "primary":
        d.rounded_rectangle(box, radius=r, fill=PRIMARY, outline=PRIMARY, width=1)
        fg = "#ffffff"
    elif kind == "plain":
        d.rounded_rectangle(box, radius=r, fill=CARD, outline=BORDER, width=1)
        fg = T2
    elif kind == "danger":
        d.rounded_rectangle(box, radius=r, fill=DANGER, outline=DANGER, width=1)
        fg = "#ffffff"
    else:
        d.rounded_rectangle(box, radius=r, fill=CARD, outline=PRIMARY_BD, width=1)
        fg = PRIMARY
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), label, font=font(size), fill=fg, anchor="mm")

def input_box(d, box, placeholder="", select=False, r=6, value=None, value_color=T1):
    d.rounded_rectangle(box, radius=r, fill=CARD, outline=BORDER, width=1)
    x = box[0] + 12
    cy = (box[1] + box[3]) / 2
    if value is not None:
        d.text((x, cy), value, font=font(17), fill=value_color, anchor="lm")
    elif placeholder:
        d.text((x, cy), placeholder, font=font(17), fill=T4, anchor="lm")
    if select:
        cx = box[2] - 18
        d.line([(cx - 4, cy - 2), (cx, cy + 3), (cx + 4, cy - 2)], fill=T3, width=2)

def arrow(d, p1, p2, color=T2, width=2, head=10):
    d.line([p1, p2], fill=color, width=width)
    import math
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    a1 = (p2[0] - head * math.cos(ang - 0.44), p2[1] - head * math.sin(ang - 0.44))
    a2 = (p2[0] - head * math.cos(ang + 0.44), p2[1] - head * math.sin(ang + 0.44))
    d.polygon([p2, a1, a2], fill=color)

def polyline_arrow(d, pts, color=T2, width=2, head=10):
    for i in range(len(pts) - 2):
        d.line([pts[i], pts[i + 1]], fill=color, width=width)
    arrow(d, pts[-2], pts[-1], color=color, width=width, head=head)

def label_bg(d, xy, s, size=16, color=T2, bold=False, pad=4, bg="#ffffff"):
    w = tw(d, s, size, bold)
    x, y = xy
    d.rectangle([x - pad, y - size // 2 - pad, x + w + pad, y + size // 2 + pad], fill=bg)
    d.text((x, y), s, font=font(size, bold), fill=color, anchor="lm")

def node_box(d, cx, cy, w, h, lines, fill=CARD, outline=T3, ow=2, tcolor=T1, size=19, r=8, bold=False):
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=r,
                        fill=fill, outline=outline, width=ow)
    n = len(lines)
    lh = size + 10
    y0 = cy - (n - 1) * lh / 2
    for i, s in enumerate(lines):
        d.text((cx, y0 + i * lh), s, font=font(size, bold), fill=tcolor, anchor="mm")

def diamond(d, cx, cy, w, h, lines, fill=CARD, outline=T3, ow=2, tcolor=T1, size=18, bold=False):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    d.polygon(pts, fill=fill, outline=outline, width=ow)
    n = len(lines)
    lh = size + 8
    y0 = cy - (n - 1) * lh / 2
    for i, s in enumerate(lines):
        d.text((cx, y0 + i * lh), s, font=font(size, bold), fill=tcolor, anchor="mm")

def start_end(d, cx, cy, r=14, fill=T2, ring=True):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=fill, width=1)

def admin_frame(d, W, H, active, role="安全管理人员"):
    """管理后台框架：顶栏 + 左侧菜单。返回内容区左上 x。"""
    d.rectangle([0, 0, W, 64], fill=CARD, outline=TBORDER)
    d.rectangle([20, 16, 52, 48], radius=6, fill=PRIMARY) if False else d.rounded_rectangle([20, 16, 52, 48], radius=6, fill=PRIMARY)
    d.text((64, 32), "HSE 隐患上报与闭环管理系统", font=font(22, True), fill=T1, anchor="lm")
    sel = role
    bw = tw(d, "当前角色：" + sel, 17) + 60
    bx0 = W - 170 - bw
    input_box(d, [bx0, 16, bx0 + bw, 48], value="当前角色：" + sel, select=True)
    d.ellipse([W - 138, 16, W - 106, 48], fill=PRIMARY_BG, outline=PRIMARY_BD)
    d.text((W - 122, 32), role[0], font=font(16), fill=PRIMARY, anchor="mm")
    d.rectangle([0, 64, 220, H], fill=CARD, outline=TBORDER)
    menus = ["隐患台账", "统计看板"]
    for i, m in enumerate(menus):
        y = 110 + i * 64
        on = (m == active)
        if on:
            d.rectangle([0, y, 220, y + 56], fill=PRIMARY_BG)
            d.rectangle([0, y, 4, y + 56], fill=PRIMARY)
        d.rounded_rectangle([30, y + 18, 50, y + 38], radius=4,
                            outline=PRIMARY if on else T3, width=2)
        d.text((66, y + 28), m, font=font(19, on), fill=PRIMARY if on else T2, anchor="lm")
    d.text((30, H - 36), "演示系统 v1.0", font=font(15), fill=T4, anchor="lm")
    return 244
