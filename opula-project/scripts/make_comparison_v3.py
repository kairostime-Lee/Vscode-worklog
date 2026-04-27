"""
合成升降对比海报 v3
- 修复底座被切问题
- 整体缩小留呼吸空间
- 更好的水印处理
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
IMG_FOLDED = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_tpx0lhtpx0lhtpx0.png")
IMG_EXPANDED = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_bjq553bjq553bjq5.png")

CANVAS_W, CANVAS_H = 3200, 1800

img_f = Image.open(IMG_FOLDED).convert("RGB")
img_e = Image.open(IMG_EXPANDED).convert("RGB")

# ========== 背景色分析 ==========
def get_bg_color(img, samples=50):
    w, h = img.size
    colors = []
    for i in range(samples):
        colors.append(img.getpixel((5, h * i // samples)))
        colors.append(img.getpixel((w - 5, h * i // samples)))
        colors.append(img.getpixel((w * i // samples, 5)))
    r = sum(c[0] for c in colors) // len(colors)
    g = sum(c[1] for c in colors) // len(colors)
    b = sum(c[2] for c in colors) // len(colors)
    return (r, g, b)

bg_f = get_bg_color(img_f)
bg_e = get_bg_color(img_e)
BG_COLOR = tuple((a + b) // 2 for a, b in zip(bg_f, bg_e))

# ========== 画布（纯色 + 微妙渐变） ==========
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H))
draw_bg = ImageDraw.Draw(canvas)
for y in range(CANVAS_H):
    ratio = y / CANVAS_H
    r = int(BG_COLOR[0] + (220 - BG_COLOR[0]) * ratio * 0.15)
    g = int(BG_COLOR[1] + (225 - BG_COLOR[1]) * ratio * 0.15)
    b = int(BG_COLOR[2] + (230 - BG_COLOR[2]) * ratio * 0.15)
    draw_bg.line([(0, y), (CANVAS_W, y)], fill=(min(r,255), min(g,255), min(b,255)))

# ========== 产品提取（蒙版法） ==========
def extract_product(img, bg_color, feather=25):
    w, h = img.size
    img_rgba = img.convert("RGBA")
    arr = np.array(img).astype(float)
    bg = np.array(bg_color).reshape(1, 1, 3).astype(float)
    diff = np.sqrt(np.sum((arr - bg) ** 2, axis=2))

    # 产品蒙版
    mask_arr = np.where(diff > 22, 255, 0).astype(np.uint8)
    mask_img = Image.fromarray(mask_arr)

    # 平滑 + 膨胀
    mask_blur = mask_img.filter(ImageFilter.GaussianBlur(radius=6))
    mask_arr2 = np.array(mask_blur)
    mask_arr2 = np.where(mask_arr2 > 60, 255, mask_arr2).astype(np.uint8)

    # 羽化边缘
    final_mask = Image.fromarray(mask_arr2).filter(ImageFilter.GaussianBlur(radius=feather))
    img_rgba.putalpha(final_mask)
    return img_rgba

product_folded = extract_product(img_f, bg_f, feather=20)
product_expanded = extract_product(img_e, bg_e, feather=20)

# ========== 缩放（整体更小，留空间） ==========
# 展开状态占画布高度 58%
target_h_expanded = int(CANVAS_H * 0.58)
scale_e = target_h_expanded / product_expanded.size[1]
new_expanded = product_expanded.resize(
    (int(product_expanded.size[0] * scale_e), target_h_expanded),
    Image.LANCZOS
)

# 收起状态：与展开等比缩放（用同样的 scale 基准）
# 但因为收起状态原图中产品占比更大（更近），需要额外缩小
target_h_folded = int(CANVAS_H * 0.52)
scale_f = target_h_folded / product_folded.size[1]
new_folded = product_folded.resize(
    (int(product_folded.size[0] * scale_f), target_h_folded),
    Image.LANCZOS
)

print(f"Resized - folded: {new_folded.size}, expanded: {new_expanded.size}")

# ========== 布局（底座底部对齐） ==========
bottom_line = CANVAS_H - 240  # 底部留更多空间给文字
center_gap = 120  # 中间间隔

# 收起状态放左侧
folded_x = CANVAS_W // 2 - center_gap // 2 - new_folded.size[0]
folded_y = bottom_line - new_folded.size[1]

# 展开状态放右侧
expanded_x = CANVAS_W // 2 + center_gap // 2
expanded_y = bottom_line - new_expanded.size[1]

# 确保不超出画布
folded_x = max(80, folded_x)
expanded_x = min(CANVAS_W - new_expanded.size[0] - 80, expanded_x)

canvas.paste(new_folded, (folded_x, folded_y), new_folded)
canvas.paste(new_expanded, (expanded_x, expanded_y), new_expanded)

# ========== 标注文字 ==========
draw = ImageDraw.Draw(canvas)

# 字体
font_title = None
for fp in [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    if os.path.exists(fp):
        font_title = ImageFont.truetype(fp, 60)
        break

font_sub = None
for fp in [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]:
    if os.path.exists(fp):
        font_sub = ImageFont.truetype(fp, 34)
        font_label = ImageFont.truetype(fp, 40)
        break

title_color = (40, 48, 58)
sub_color = (90, 100, 118)
accent_color = (55, 125, 195)
line_color = (130, 145, 168)

# 标题
draw.text((CANVAS_W // 2, 65), "Adjustable Height & Extendable Head",
          fill=title_color, font=font_title, anchor="mt")
draw.text((CANVAS_W // 2, 140), "Effortlessly adapt to any workspace",
          fill=sub_color, font=font_sub, anchor="mt")

# 底部标签
folded_cx = folded_x + new_folded.size[0] // 2
expanded_cx = expanded_x + new_expanded.size[0] // 2
draw.text((folded_cx, bottom_line + 25), "Compact", fill=sub_color, font=font_label, anchor="mt")
draw.text((expanded_cx, bottom_line + 25), "Extended", fill=sub_color, font=font_label, anchor="mt")

# 中间箭头
arrow_cx = CANVAS_W // 2
arrow_cy = (max(folded_y, expanded_y) + bottom_line) // 2
arrow_len = 40
draw.line([(arrow_cx - arrow_len, arrow_cy), (arrow_cx + arrow_len, arrow_cy)],
          fill=accent_color, width=4)
pts = [(arrow_cx + arrow_len + 2, arrow_cy),
       (arrow_cx + arrow_len - 16, arrow_cy - 12),
       (arrow_cx + arrow_len - 16, arrow_cy + 12)]
draw.polygon(pts, fill=accent_color)

# 高度标注虚线
def draw_dashed_vline(draw, x, y1, y2, color, width=2, dash=10, gap=7):
    y = y1
    while y < y2:
        end = min(y + dash, y2)
        draw.line([(x, y), (x, end)], fill=color, width=width)
        y = end + gap

# 左侧
hl_x = folded_x - 45
draw_dashed_vline(draw, hl_x, folded_y + 30, bottom_line, line_color)
draw.line([(hl_x - 10, folded_y + 30), (hl_x + 10, folded_y + 30)], fill=line_color, width=2)
draw.line([(hl_x - 10, bottom_line), (hl_x + 10, bottom_line)], fill=line_color, width=2)

# 右侧
hr_x = expanded_x + new_expanded.size[0] + 45
draw_dashed_vline(draw, hr_x, expanded_y + 30, bottom_line, line_color)
draw.line([(hr_x - 10, expanded_y + 30), (hr_x + 10, expanded_y + 30)], fill=line_color, width=2)
draw.line([(hr_x - 10, bottom_line), (hr_x + 10, bottom_line)], fill=line_color, width=2)

# ========== 保存 ==========
output_path = os.path.join(OUTPUT_DIR, "comparison_height_extend_v3.png")
canvas.save(output_path, "PNG")
print(f"Done: {output_path}")
