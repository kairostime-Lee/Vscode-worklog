"""
合成升降对比海报 v2
- 用蒙版羽化边缘融合背景
- 更好的水印处理
- 底座底部对齐
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
IMG_FOLDED = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_tpx0lhtpx0lhtpx0.png")
IMG_EXPANDED = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_bjq553bjq553bjq5.png")

CANVAS_W, CANVAS_H = 3200, 1800

# ========== 分析原图背景色 ==========
img_f = Image.open(IMG_FOLDED).convert("RGB")
img_e = Image.open(IMG_EXPANDED).convert("RGB")

# 取两张图的平均背景色（从边缘采样）
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
# 用两张图背景的平均色作为画布色
BG_COLOR = tuple((a + b) // 2 for a, b in zip(bg_f, bg_e))
print(f"BG colors - folded: {bg_f}, expanded: {bg_e}, canvas: {BG_COLOR}")

# ========== 创建渐变背景画布 ==========
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H))
draw_bg = ImageDraw.Draw(canvas)
# 从上到下轻微渐变
for y in range(CANVAS_H):
    ratio = y / CANVAS_H
    r = int(BG_COLOR[0] * (1 - ratio * 0.08))
    g = int(BG_COLOR[1] * (1 - ratio * 0.06))
    b = int(BG_COLOR[2] * (1 - ratio * 0.04))
    draw_bg.line([(0, y), (CANVAS_W, y)], fill=(r, g, b))

# ========== 处理产品图：用蒙版提取产品 ==========
def extract_product_with_feather(img, bg_color, feather=40):
    """
    创建一个蒙版：产品区域不透明，背景区域透明，边缘羽化过渡
    """
    w, h = img.size
    img_rgba = img.convert("RGBA")

    # 计算每个像素与背景色的差异
    arr = np.array(img)
    bg = np.array(bg_color).reshape(1, 1, 3)
    diff = np.sqrt(np.sum((arr.astype(float) - bg.astype(float)) ** 2, axis=2))

    # 创建蒙版：差异大的是产品（不透明），差异小的是背景（透明）
    threshold = 25
    mask = np.where(diff > threshold, 255, 0).astype(np.uint8)

    # 膨胀蒙版填充产品内部空洞
    mask_img = Image.fromarray(mask)
    # 模糊后重新阈值化来平滑边缘
    mask_blur = mask_img.filter(ImageFilter.GaussianBlur(radius=8))
    mask_arr = np.array(mask_blur)
    mask_arr = np.where(mask_arr > 80, 255, mask_arr).astype(np.uint8)

    # 最终羽化
    final_mask = Image.fromarray(mask_arr).filter(ImageFilter.GaussianBlur(radius=feather))

    img_rgba.putalpha(final_mask)
    return img_rgba

product_folded = extract_product_with_feather(img_f, bg_f, feather=30)
product_expanded = extract_product_with_feather(img_e, bg_e, feather=30)

# ========== 裁掉水印区域（底部裁掉一点点） ==========
def crop_watermark(img, bottom_crop=60):
    w, h = img.size
    return img.crop((0, 0, w, h - bottom_crop))

product_folded = crop_watermark(product_folded, 60)
product_expanded = crop_watermark(product_expanded, 60)

# ========== 缩放 ==========
# 展开状态作为基准，占画布高度 70%
target_h_expanded = int(CANVAS_H * 0.70)
scale_e = target_h_expanded / product_expanded.size[1]
new_expanded = product_expanded.resize(
    (int(product_expanded.size[0] * scale_e), target_h_expanded),
    Image.LANCZOS
)

# 收起状态：高度为展开的 82%（显示矮一些）
target_h_folded = int(target_h_expanded * 0.85)
scale_f = target_h_folded / product_folded.size[1]
new_folded = product_folded.resize(
    (int(product_folded.size[0] * scale_f), target_h_folded),
    Image.LANCZOS
)

print(f"Resized - folded: {new_folded.size}, expanded: {new_expanded.size}")

# ========== 布局 ==========
# 底部对齐线
bottom_line = CANVAS_H - 200

# 展开状态放右侧
expanded_x = CANVAS_W // 2 + 60
expanded_y = bottom_line - new_expanded.size[1]

# 收起状态放左侧，底部对齐
folded_x = CANVAS_W // 2 - 60 - new_folded.size[0]
folded_y = bottom_line - new_folded.size[1]

# 粘贴（带 alpha 通道融合）
canvas.paste(new_folded, (folded_x, folded_y), new_folded)
canvas.paste(new_expanded, (expanded_x, expanded_y), new_expanded)

# ========== 标注 ==========
draw = ImageDraw.Draw(canvas)

# 字体
font_paths = [
    r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]
font_title = None
font_sub = None
font_label = None
for fp in font_paths:
    if os.path.exists(fp):
        font_title = ImageFont.truetype(fp, 64)
        font_sub = ImageFont.truetype(fp, 36)
        font_label = ImageFont.truetype(fp, 44)
        break

title_color = (40, 48, 58)
sub_color = (90, 100, 115)
accent_color = (60, 130, 200)  # 蓝色强调
line_color = (140, 155, 175)

# 顶部标题
draw.text((CANVAS_W // 2, 70), "Adjustable Height & Extendable Head",
          fill=title_color, font=font_title, anchor="mt")
draw.text((CANVAS_W // 2, 145), "Effortlessly adapt to any workspace",
          fill=sub_color, font=font_sub, anchor="mt")

# 底部标签
folded_cx = folded_x + new_folded.size[0] // 2
expanded_cx = expanded_x + new_expanded.size[0] // 2

draw.text((folded_cx, bottom_line + 30), "Compact",
          fill=sub_color, font=font_label, anchor="mt")
draw.text((expanded_cx, bottom_line + 30), "Extended",
          fill=sub_color, font=font_label, anchor="mt")

# 中间箭头
arrow_cx = CANVAS_W // 2
arrow_cy = (folded_y + bottom_line) // 2 + 40

# 箭头主体（粗线）
arrow_len = 50
draw.line([(arrow_cx - arrow_len, arrow_cy), (arrow_cx + arrow_len, arrow_cy)],
          fill=accent_color, width=5)
# 箭头头部
pts = [(arrow_cx + arrow_len, arrow_cy),
       (arrow_cx + arrow_len - 18, arrow_cy - 14),
       (arrow_cx + arrow_len - 18, arrow_cy + 14)]
draw.polygon(pts, fill=accent_color)

# 高度标注虚线 — 左侧
def draw_dashed_line(draw, x, y1, y2, color, width=2, dash=10, gap=8):
    y = y1
    while y < y2:
        end = min(y + dash, y2)
        draw.line([(x, y), (x, end)], fill=color, width=width)
        y = end + gap

# 左侧高度线
hl_x = folded_x - 50
draw_dashed_line(draw, hl_x, folded_y + 20, bottom_line, line_color)
draw.line([(hl_x - 12, folded_y + 20), (hl_x + 12, folded_y + 20)], fill=line_color, width=2)
draw.line([(hl_x - 12, bottom_line), (hl_x + 12, bottom_line)], fill=line_color, width=2)

# 右侧高度线
hr_x = expanded_x + new_expanded.size[0] + 50
draw_dashed_line(draw, hr_x, expanded_y + 20, bottom_line, line_color)
draw.line([(hr_x - 12, expanded_y + 20), (hr_x + 12, expanded_y + 20)], fill=line_color, width=2)
draw.line([(hr_x - 12, bottom_line), (hr_x + 12, bottom_line)], fill=line_color, width=2)

# ========== 保存 ==========
output_path = os.path.join(OUTPUT_DIR, "comparison_height_extend_v2.png")
canvas.save(output_path, "PNG")
print(f"Done: {output_path}")
print(f"Size: {CANVAS_W}x{CANVAS_H}")
