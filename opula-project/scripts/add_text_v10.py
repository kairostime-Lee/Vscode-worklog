"""
海报文字排版 v10
- 基于v9调整：
  1. 右侧 Monitor Mode 标签右移
  2. 副标题移到底部灯具下方居中，加粗放大
  3. 特性条上移紧跟主标题
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
font_bold = font_regular = None
for fp in [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    if os.path.exists(fp): font_bold = fp; break
for fp in [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]:
    if os.path.exists(fp): font_regular = fp; break

title_font = ImageFont.truetype(font_bold, 88)
subtitle_font = ImageFont.truetype(font_bold, 42)  # 加粗 + 放大（从regular 38 → bold 42）
feature_font = ImageFont.truetype(font_bold, 36)
label_font = ImageFont.truetype(font_bold, 38)
sublabel_font = ImageFont.truetype(font_regular, 28)

title_color = (30, 38, 48)
subtitle_color = (65, 75, 92)
feature_color = (55, 70, 95)
sep_color = (150, 160, 178)
label_color = (50, 58, 70)
sublabel_color = (105, 115, 132)

# =============================================
# 顶部：主标题 + 特性条（两行紧凑）
# =============================================
# 主标题
title_text = "Rise & Extend Eye-Care Desk Lamp"
tb = draw.textbbox((0, 0), title_text, font=title_font)
tw = tb[2] - tb[0]
title_y = 8
draw.text(((w - tw) // 2, title_y), title_text, fill=title_color, font=title_font)

# 特性条（紧跟主标题下方）
features = ["Flicker-Free", "Low Blue Light", "Full Spectrum Ra≥97", "Voice Control"]
separator = "   |   "
feature_line = separator.join(features)
fb = draw.textbbox((0, 0), feature_line, font=feature_font)
fw = fb[2] - fb[0]
feat_y = title_y + 110  # 标题下方留间距

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
# 底部：副标题（居中）+ 左右标签
# =============================================

# 副标题放在底部灯具下方，水平居中
subtitle_text = "Adjustable Height & Extendable Head · Premium Aluminum"
sb = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
sw = sb[2] - sb[0]
sub_y = h - 122  # 灯具底座下方
draw.text(((w - sw) // 2, sub_y), subtitle_text, fill=subtitle_color, font=subtitle_font)

# 底部标签
bottom_y = h - 115

# 左侧 Laptop Mode（不动）
left_cx = 480
label1 = "Laptop Mode"
l1b = draw.textbbox((0, 0), label1, font=label_font)
draw.text((left_cx - (l1b[2] - l1b[0]) // 2, bottom_y), label1, fill=label_color, font=label_font)
sublabel1 = "Compact · Perfect for laptops"
sl1b = draw.textbbox((0, 0), sublabel1, font=sublabel_font)
draw.text((left_cx - (sl1b[2] - sl1b[0]) // 2, bottom_y + 48), sublabel1, fill=sublabel_color, font=sublabel_font)

# 右侧 Monitor Mode（右移）
right_cx = 2250  # 从2050右移到2250
label2 = "Monitor Mode"
l2b = draw.textbbox((0, 0), label2, font=label_font)
draw.text((right_cx - (l2b[2] - l2b[0]) // 2, bottom_y), label2, fill=label_color, font=label_font)
sublabel2 = "Extended · Behind single or dual monitors"
sl2b = draw.textbbox((0, 0), sublabel2, font=sublabel_font)
draw.text((right_cx - (sl2b[2] - sl2b[0]) // 2, bottom_y + 48), sublabel2, fill=sublabel_color, font=sublabel_font)

# 保存
result = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
output_path = os.path.join(OUTPUT_DIR, "poster_adapts_v10.png")
ok, buf = cv2.imencode('.png', result)
with open(output_path, 'wb') as f:
    f.write(buf.tobytes())
print(f"Done: {output_path}, size: {w}x{h}")
