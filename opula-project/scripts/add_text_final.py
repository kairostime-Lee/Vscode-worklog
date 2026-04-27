"""
在 o3j4-Final 上添加文字排版
主标题: Adapts to Any Setup
副标题: Premium aluminum design for single or dual monitor workspaces
左标签: Single Monitor · Compact mode
右标签: Dual Monitor · Extended mode
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"

def cv_read(path):
    with open(path, 'rb') as f:
        data = np.frombuffer(f.read(), np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

# 用 PIL 处理文字（字体渲染更好）
img_cv = cv_read(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4-Final.png"))
img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
img = Image.fromarray(img_rgb)
w, h = img.size
print(f"Image: {w}x{h}")

draw = ImageDraw.Draw(img)

# 加载字体
font_bold = None
font_regular = None
font_light = None

# 尝试多个字体路径
bold_paths = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
]
regular_paths = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
]
light_paths = [
    r"C:\Windows\Fonts\segoeuil.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]

for fp in bold_paths:
    if os.path.exists(fp):
        font_bold = fp
        break
for fp in regular_paths:
    if os.path.exists(fp):
        font_regular = fp
        break
for fp in light_paths:
    if os.path.exists(fp):
        font_light = fp
        break

# 字体大小
title_font = ImageFont.truetype(font_bold, 68)
subtitle_font = ImageFont.truetype(font_regular, 30)
label_font = ImageFont.truetype(font_bold, 36)
sublabel_font = ImageFont.truetype(font_light, 26)

# 颜色
title_color = (35, 42, 52)
subtitle_color = (90, 100, 118)
label_color = (50, 58, 70)
sublabel_color = (110, 120, 138)
accent_color = (50, 120, 190)

# =============================================
# 主标题（顶部居中）
# =============================================
title_text = "Adapts to Any Setup"
title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
title_w = title_bbox[2] - title_bbox[0]
title_x = (w - title_w) // 2
title_y = 55
draw.text((title_x, title_y), title_text, fill=title_color, font=title_font)

# =============================================
# 副标题
# =============================================
subtitle_text = "Premium aluminum design for single or dual monitor workspaces"
sub_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
sub_w = sub_bbox[2] - sub_bbox[0]
sub_x = (w - sub_w) // 2
sub_y = title_y + 85
draw.text((sub_x, sub_y), subtitle_text, fill=subtitle_color, font=subtitle_font)

# =============================================
# 底部标签
# =============================================
bottom_y = h - 130

# 左灯标签 - 左灯中心大约在 x=500
left_cx = 480
label1 = "Single Monitor"
label1_bbox = draw.textbbox((0, 0), label1, font=label_font)
label1_w = label1_bbox[2] - label1_bbox[0]
draw.text((left_cx - label1_w // 2, bottom_y), label1, fill=label_color, font=label_font)

sublabel1 = "Compact Mode"
sl1_bbox = draw.textbbox((0, 0), sublabel1, font=sublabel_font)
sl1_w = sl1_bbox[2] - sl1_bbox[0]
draw.text((left_cx - sl1_w // 2, bottom_y + 45), sublabel1, fill=sublabel_color, font=sublabel_font)

# 右灯标签 - 右灯中心大约在 x=2050
right_cx = 2050
label2 = "Dual Monitor"
label2_bbox = draw.textbbox((0, 0), label2, font=label_font)
label2_w = label2_bbox[2] - label2_bbox[0]
draw.text((right_cx - label2_w // 2, bottom_y), label2, fill=label_color, font=label_font)

sublabel2 = "Extended Mode"
sl2_bbox = draw.textbbox((0, 0), sublabel2, font=sublabel_font)
sl2_w = sl2_bbox[2] - sl2_bbox[0]
draw.text((right_cx - sl2_w // 2, bottom_y + 45), sublabel2, fill=sublabel_color, font=sublabel_font)

# =============================================
# 中间箭头
# =============================================
arrow_cx = w // 2
arrow_cy = h // 2 + 50

# 用 PIL 画箭头
arrow_len = 45
# 箭头线
for dx in range(-arrow_len, arrow_len + 1):
    for dy in range(-2, 3):
        px = arrow_cx + dx
        py = arrow_cy + dy
        if 0 <= px < w and 0 <= py < h:
            draw.point((px, py), fill=accent_color)

# 箭头头部（三角形）
triangle = [
    (arrow_cx + arrow_len + 2, arrow_cy),
    (arrow_cx + arrow_len - 14, arrow_cy - 12),
    (arrow_cx + arrow_len - 14, arrow_cy + 12),
]
draw.polygon(triangle, fill=accent_color)

# =============================================
# 保存
# =============================================
# 转回 BGR 保存
result = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
output_path = os.path.join(OUTPUT_DIR, "poster_adapts_to_any_setup.png")
ok, buf = cv2.imencode('.png', result)
with open(output_path, 'wb') as f:
    f.write(buf.tobytes())
print(f"Done: {output_path}")
