"""
海报文字排版 v6
- 标题适中（不遮挡灯具）
- 副标题/要点字体加大
- 要点放在底部标签上方，不与灯具重叠
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

title_font = ImageFont.truetype(font_bold, 88)
subtitle_font = ImageFont.truetype(font_regular, 38)
feature_font = ImageFont.truetype(font_regular, 32)
label_font = ImageFont.truetype(font_bold, 38)
sublabel_font = ImageFont.truetype(font_regular, 28)

title_color = (30, 38, 48)
subtitle_color = (65, 75, 92)
feature_color = (70, 82, 100)
sep_color = (155, 165, 180)
label_color = (50, 58, 70)
sublabel_color = (105, 115, 132)

# =============================================
# 主标题（顶部居中，一行）
# =============================================
title_text = "Rise & Extend Eye-Care Desk Lamp"
tb = draw.textbbox((0, 0), title_text, font=title_font)
tw = tb[2] - tb[0]
title_y = 30
draw.text(((w - tw) // 2, title_y), title_text, fill=title_color, font=title_font)

# =============================================
# 副标题（功能说明，加大字号）
# =============================================
subtitle_text = "Adjustable Height & Extendable Head · Premium Aluminum"
sb = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
sw = sb[2] - sb[0]
sub_y = title_y + 100
draw.text(((w - sw) // 2, sub_y), subtitle_text, fill=subtitle_color, font=subtitle_font)

# =============================================
# 特性条（底部标签上方，字体加大）
# =============================================
features = ["Flicker-Free", "Low Blue Light", "Full Spectrum Ra≥97", "Voice Control"]
separator = "   |   "
feature_line = separator.join(features)
fb = draw.textbbox((0, 0), feature_line, font=feature_font)
fw = fb[2] - fb[0]
feat_y = h - 195

# 逐段绘制
x_cursor = (w - fw) // 2
for i, feat in enumerate(features):
    draw.text((x_cursor, feat_y), feat, fill=feature_color, font=feature_font)
    ftb = draw.textbbox((0, 0), feat, font=feature_font)
    x_cursor += ftb[2] - ftb[0]
    if i < len(features) - 1:
        draw.text((x_cursor, feat_y), separator, fill=sep_color, font=feature_font)
        stb = draw.textbbox((0, 0), separator, font=feature_font)
        x_cursor += stb[2] - stb[0]

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
draw.text((left_cx - (sl1b[2] - sl1b[0]) // 2, bottom_y + 48), sublabel1, fill=sublabel_color, font=sublabel_font)

right_cx = 2050
label2 = "Monitor Mode"
l2b = draw.textbbox((0, 0), label2, font=label_font)
draw.text((right_cx - (l2b[2] - l2b[0]) // 2, bottom_y), label2, fill=label_color, font=label_font)
sublabel2 = "Extended · Behind single or dual monitors"
sl2b = draw.textbbox((0, 0), sublabel2, font=sublabel_font)
draw.text((right_cx - (sl2b[2] - sl2b[0]) // 2, bottom_y + 48), sublabel2, fill=sublabel_color, font=sublabel_font)

# 保存
result = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
output_path = os.path.join(OUTPUT_DIR, "poster_adapts_v6.png")
ok, buf = cv2.imencode('.png', result)
with open(output_path, 'wb') as f:
    f.write(buf.tobytes())
print(f"Done: {output_path}")
