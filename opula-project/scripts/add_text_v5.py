"""
海报文字排版 v5 - 参考效果1的大标题+要点风格
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"

def cv_read(path):
    with open(path, 'rb') as f:
        data = np.frombuffer(f.read(), np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

img_cv = cv_read(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4-Final.png"))
img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
img = Image.fromarray(img_rgb)
w, h = img.size
draw = ImageDraw.Draw(img)

# 字体
font_bold = font_regular = font_light = None
for fp in [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    if os.path.exists(fp): font_bold = fp; break
for fp in [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]:
    if os.path.exists(fp): font_regular = fp; break
for fp in [r"C:\Windows\Fonts\segoeuil.ttf", r"C:\Windows\Fonts\segoeui.ttf"]:
    if os.path.exists(fp): font_light = fp; break

# 超大标题 + 中号要点（参考效果1比例）
title_font_large = ImageFont.truetype(font_bold, 130)
bullet_font = ImageFont.truetype(font_regular, 34)
label_font = ImageFont.truetype(font_bold, 36)
sublabel_font = ImageFont.truetype(font_light, 26)

title_color = (30, 38, 48)
bullet_color = (55, 65, 80)
dot_color = (80, 95, 115)
label_color = (50, 58, 70)
sublabel_color = (110, 120, 138)

# =============================================
# 超大主标题（两行）
# =============================================
line1 = "Rise & Extend"
line2 = "Eye-Care Desk Lamp"

# 第一行
l1_bbox = draw.textbbox((0, 0), line1, font=title_font_large)
l1_w = l1_bbox[2] - l1_bbox[0]
l1_y = 15
draw.text(((w - l1_w) // 2, l1_y), line1, fill=title_color, font=title_font_large)

# 第二行
l2_bbox = draw.textbbox((0, 0), line2, font=title_font_large)
l2_w = l2_bbox[2] - l2_bbox[0]
l2_y = l1_y + 125
draw.text(((w - l2_w) // 2, l2_y), line2, fill=title_color, font=title_font_large)

# =============================================
# 要点横排（圆点 + 文字，参考效果1）
# =============================================
bullets = [
    "Full Spectrum\nCRI Ra≥97",
    "Flicker-Free\nLow Blue Light",
    "Smart Voice\nControl"
]

bullet_y = l2_y + 145
# 三个要点等间距分布
positions = [w * 0.2, w * 0.5, w * 0.8]

for i, (text, cx) in enumerate(zip(bullets, positions)):
    lines = text.split("\n")
    # 圆点
    dot_r = 6
    dot_y = bullet_y + 5

    # 计算文本块宽度（取最宽行）
    max_line_w = 0
    for line in lines:
        lb = draw.textbbox((0, 0), line, font=bullet_font)
        lw = lb[2] - lb[0]
        max_line_w = max(max_line_w, lw)

    block_w = dot_r * 2 + 12 + max_line_w
    start_x = int(cx - block_w / 2)

    # 画圆点
    draw.ellipse([start_x, dot_y, start_x + dot_r * 2, dot_y + dot_r * 2], fill=dot_color)

    # 画文字（每行）
    text_x = start_x + dot_r * 2 + 12
    for j, line in enumerate(lines):
        draw.text((text_x, bullet_y + j * 40), line, fill=bullet_color, font=bullet_font)

# =============================================
# 底部标签
# =============================================
bottom_y = h - 120

left_cx = 480
label1 = "Laptop Mode"
l1b = draw.textbbox((0, 0), label1, font=label_font)
draw.text((left_cx - (l1b[2] - l1b[0]) // 2, bottom_y), label1, fill=label_color, font=label_font)
sublabel1 = "Compact · Perfect for laptops"
sl1b = draw.textbbox((0, 0), sublabel1, font=sublabel_font)
draw.text((left_cx - (sl1b[2] - sl1b[0]) // 2, bottom_y + 44), sublabel1, fill=sublabel_color, font=sublabel_font)

right_cx = 2050
label2 = "Monitor Mode"
l2b = draw.textbbox((0, 0), label2, font=label_font)
draw.text((right_cx - (l2b[2] - l2b[0]) // 2, bottom_y), label2, fill=label_color, font=label_font)
sublabel2 = "Extended · Behind single or dual monitors"
sl2b = draw.textbbox((0, 0), sublabel2, font=sublabel_font)
draw.text((right_cx - (sl2b[2] - sl2b[0]) // 2, bottom_y + 44), sublabel2, fill=sublabel_color, font=sublabel_font)

# 保存
result = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
output_path = os.path.join(OUTPUT_DIR, "poster_adapts_v5.png")
ok, buf = cv2.imencode('.png', result)
with open(output_path, 'wb') as f:
    f.write(buf.tobytes())
print(f"Done: {output_path}")
