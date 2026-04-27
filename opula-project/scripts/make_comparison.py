"""
合成升降对比海报
- 左：收起状态 (tpx0lh) — 缩小以对齐底座
- 右：展开状态 (bjq553)
- 去掉右下角 Gemini 水印
- 加标注箭头和文字
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ========== 配置 ==========
OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
IMG_FOLDED = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_tpx0lhtpx0lhtpx0.png")   # 收起
IMG_EXPANDED = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_bjq553bjq553bjq5.png")  # 展开

# 最终画布尺寸 (16:9 适合 Amazon)
CANVAS_W, CANVAS_H = 3200, 1800
BG_COLOR = (210, 218, 226)  # 浅蓝灰，匹配原图背景

# ========== 加载图片 ==========
img_folded = Image.open(IMG_FOLDED).convert("RGBA")
img_expanded = Image.open(IMG_EXPANDED).convert("RGBA")

# ========== 去水印：右下角区域用背景色覆盖 ==========
def remove_watermark(img, size=80):
    """用周围背景色覆盖右下角水印"""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    # 采样水印上方的背景色
    sample_x, sample_y = w - size - 30, h - size - 50
    bg_sample = img.getpixel((sample_x, sample_y))[:3]
    # 覆盖右下角
    draw.rectangle([w - size - 20, h - size - 20, w, h], fill=bg_sample + (255,))
    return img

img_folded = remove_watermark(img_folded)
img_expanded = remove_watermark(img_expanded)

# ========== 裁剪：去掉多余的底部和侧边空白 ==========
# 收起状态：产品偏大，需要缩小一点让底座和展开状态对齐
# 展开状态：产品偏小，保持原尺寸或稍微放大

# 先把两张都裁成产品区域（去掉边缘空白）
def crop_to_content(img, padding=30):
    """裁掉纯色边缘，保留产品内容"""
    # 转换为 RGB 用于分析
    rgb = img.convert("RGB")
    w, h = rgb.size
    # 取四角平均色作为背景参考
    corners = [rgb.getpixel((5, 5)), rgb.getpixel((w-5, 5)),
               rgb.getpixel((5, h-5)), rgb.getpixel((w-5, h-5))]
    bg_r = sum(c[0] for c in corners) // 4
    bg_g = sum(c[1] for c in corners) // 4
    bg_b = sum(c[2] for c in corners) // 4

    threshold = 30
    # 找内容边界
    left, top, right, bottom = w, h, 0, 0
    # 采样而非逐像素（性能优化）
    step = 4
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = rgb.getpixel((x, y))
            if abs(r - bg_r) > threshold or abs(g - bg_g) > threshold or abs(b - bg_b) > threshold:
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)

    # 加 padding
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(w, right + padding)
    bottom = min(h, bottom + padding)

    return img.crop((left, top, right, bottom))

cropped_folded = crop_to_content(img_folded, padding=20)
cropped_expanded = crop_to_content(img_expanded, padding=20)

print(f"裁剪后 - 收起: {cropped_folded.size}, 展开: {cropped_expanded.size}")

# ========== 缩放对齐 ==========
# 关键：让两张图的底座宽度视觉一致
# 收起状态的灯偏大（近景），需要缩小
# 展开状态的灯偏小（远景），保持或稍放大

# 目标：两张图放在画布左右两侧，高度占画布的 ~75%
target_h = int(CANVAS_H * 0.72)

# 展开状态按目标高度缩放（作为基准）
scale_expanded = target_h / cropped_expanded.size[1]
new_expanded = cropped_expanded.resize(
    (int(cropped_expanded.size[0] * scale_expanded), target_h),
    Image.LANCZOS
)

# 收起状态：缩小更多一点（约 85% 的展开高度），因为收起时灯更矮
# 但底座要对齐，所以实际上需要让底座宽度一致
# 简单方案：收起状态高度设为展开状态的 80%，底部对齐
folded_target_h = int(target_h * 0.82)
scale_folded = folded_target_h / cropped_folded.size[1]
new_folded = cropped_folded.resize(
    (int(cropped_folded.size[0] * scale_folded), folded_target_h),
    Image.LANCZOS
)

print(f"缩放后 - 收起: {new_folded.size}, 展开: {new_expanded.size}")

# ========== 合成画布 ==========
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# 左侧放收起状态，右侧放展开状态
gap = 80  # 中间间距
total_w = new_folded.size[0] + gap + new_expanded.size[0]
start_x = (CANVAS_W - total_w) // 2

# 底部对齐
bottom_y = CANVAS_H - 180  # 底部留空放文字

# 收起状态（左）
folded_x = start_x
folded_y = bottom_y - new_folded.size[1]
canvas.paste(new_folded, (folded_x, folded_y), new_folded)

# 展开状态（右）
expanded_x = start_x + new_folded.size[0] + gap
expanded_y = bottom_y - new_expanded.size[1]
canvas.paste(new_expanded, (expanded_x, expanded_y), new_expanded)

# ========== 添加标注 ==========
draw = ImageDraw.Draw(canvas)

# 尝试加载字体
font_paths = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
]
font_large = None
font_small = None
for fp in font_paths:
    if os.path.exists(fp):
        font_large = ImageFont.truetype(fp, 56)
        font_small = ImageFont.truetype(fp, 40)
        break
if font_large is None:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 标题文字
title_color = (50, 55, 65)
sub_color = (100, 110, 125)

# 顶部标题
draw.text((CANVAS_W // 2, 60), "Adjustable Height & Extendable Head",
          fill=title_color, font=font_large, anchor="mt")

# 左标签：Compact Mode
folded_center_x = folded_x + new_folded.size[0] // 2
draw.text((folded_center_x, bottom_y + 20), "Compact Mode",
          fill=sub_color, font=font_small, anchor="mt")

# 右标签：Extended Mode
expanded_center_x = expanded_x + new_expanded.size[0] // 2
draw.text((expanded_center_x, bottom_y + 20), "Extended Mode",
          fill=sub_color, font=font_small, anchor="mt")

# 中间箭头（→）
arrow_y = (folded_y + bottom_y) // 2
arrow_x = start_x + new_folded.size[0] + gap // 2
# 画箭头线
arrow_left = arrow_x - 30
arrow_right = arrow_x + 30
draw.line([(arrow_left, arrow_y), (arrow_right, arrow_y)], fill=title_color, width=4)
# 箭头头部
draw.polygon([(arrow_right, arrow_y), (arrow_right - 15, arrow_y - 10), (arrow_right - 15, arrow_y + 10)], fill=title_color)

# 高度标注线（左侧 - 虚线效果）
line_color = (130, 140, 155)
# 收起状态高度线
h_line_x = folded_x - 40
for y in range(folded_y, bottom_y, 12):
    draw.line([(h_line_x, y), (h_line_x, min(y + 6, bottom_y))], fill=line_color, width=2)
# 顶部横线
draw.line([(h_line_x - 10, folded_y), (h_line_x + 10, folded_y)], fill=line_color, width=2)
# 底部横线
draw.line([(h_line_x - 10, bottom_y), (h_line_x + 10, bottom_y)], fill=line_color, width=2)

# 展开状态高度线
h_line_x2 = expanded_x + new_expanded.size[0] + 40
for y in range(expanded_y, bottom_y, 12):
    draw.line([(h_line_x2, y), (h_line_x2, min(y + 6, bottom_y))], fill=line_color, width=2)
draw.line([(h_line_x2 - 10, expanded_y), (h_line_x2 + 10, expanded_y)], fill=line_color, width=2)
draw.line([(h_line_x2 - 10, bottom_y), (h_line_x2 + 10, bottom_y)], fill=line_color, width=2)

# ========== 保存 ==========
output_path = os.path.join(OUTPUT_DIR, "对比图_升降展开.png")
canvas.convert("RGB").save(output_path, quality=95)
print(f"\nDone: {output_path}")
print(f"  尺寸: {CANVAS_W}x{CANVAS_H}")
