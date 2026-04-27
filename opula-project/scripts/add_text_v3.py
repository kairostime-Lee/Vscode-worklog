"""
海报文字排版 v3
- 主标题加大，突出灯的升降+拉伸功能
- 副标题说明适配场景
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
font_bold = None
font_regular = None
font_light = None
for fp in [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    if os.path.exists(fp):
        font_bold = fp; break
for fp in [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]:
    if os.path.exists(fp):
        font_regular = fp; break
for fp in [r"C:\Windows\Fonts\segoeuil.ttf", r"C:\Windows\Fonts\segoeui.ttf"]:
    if os.path.exists(fp):
        font_light = fp; break

# 字号加大
title_font = ImageFont.truetype(font_bold, 96)
subtitle_font = ImageFont.truetype(font_regular, 34)
label_font = ImageFont.truetype(font_bold, 36)
sublabel_font = ImageFont.truetype(font_light, 26)

title_color = (35, 42, 52)
subtitle_color = (85, 95, 112)
label_color = (50, 58, 70)
sublabel_color = (110, 120, 138)

# =============================================
# 主标题（大号，突出功能）
# =============================================
title_text = "Rise. Extend. Illuminate."
title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
title_w = title_bbox[2] - title_bbox[0]
title_x = (w - title_w) // 2
title_y = 35
draw.text((title_x, title_y), title_text, fill=title_color, font=title_font)

# =============================================
# 副标题（说明功能 + 材质）
# =============================================
subtitle_text = "Freely adjustable height & extendable head · Premium aluminum build"
sub_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
sub_w = sub_bbox[2] - sub_bbox[0]
sub_x = (w - sub_w) // 2
sub_y = title_y + 110
draw.text((sub_x, sub_y), subtitle_text, fill=subtitle_color, font=subtitle_font)

# =============================================
# 底部标签
# =============================================
bottom_y = h - 130

# 左灯
left_cx = 480
label1 = "Laptop Mode"
l1_bbox = draw.textbbox((0, 0), label1, font=label_font)
draw.text((left_cx - (l1_bbox[2] - l1_bbox[0]) // 2, bottom_y), label1, fill=label_color, font=label_font)

sublabel1 = "Compact · Perfect for laptops"
sl1_bbox = draw.textbbox((0, 0), sublabel1, font=sublabel_font)
draw.text((left_cx - (sl1_bbox[2] - sl1_bbox[0]) // 2, bottom_y + 45), sublabel1, fill=sublabel_color, font=sublabel_font)

# 右灯
right_cx = 2050
label2 = "Monitor Mode"
l2_bbox = draw.textbbox((0, 0), label2, font=label_font)
draw.text((right_cx - (l2_bbox[2] - l2_bbox[0]) // 2, bottom_y), label2, fill=label_color, font=label_font)

sublabel2 = "Extended · Single or dual monitors"
sl2_bbox = draw.textbbox((0, 0), sublabel2, font=sublabel_font)
draw.text((right_cx - (sl2_bbox[2] - sl2_bbox[0]) // 2, bottom_y + 45), sublabel2, fill=sublabel_color, font=sublabel_font)

# 保存
result = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
output_path = os.path.join(OUTPUT_DIR, "poster_adapts_v3.png")
ok, buf = cv2.imencode('.png', result)
with open(output_path, 'wb') as f:
    f.write(buf.tobytes())
print(f"Done: {output_path}")
