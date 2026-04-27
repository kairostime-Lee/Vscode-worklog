"""
最终修复：
1. 先在两张原始 Gemini 图上修复水印
2. 重新合成对比图
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"

def inpaint_region(arr, x1, y1, x2, y2, margin=5):
    """用上方参考行填充指定区域"""
    for y in range(max(0, y1-margin), min(arr.shape[0], y2+margin)):
        for x in range(max(0, x1-margin), min(arr.shape[1], x2+margin)):
            # 取上方 margin+5 行的像素
            ref_y = max(0, y1 - margin - 5)
            arr[y, x] = arr[ref_y, x]
    return arr

# ===== 修复原图水印 =====
# bjq553 水印在 (2590, 1375) 到 (2700, 1475)
img_e = np.array(Image.open(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_bjq553bjq553bjq5.png")).convert("RGB"))
img_e = inpaint_region(img_e, 2585, 1370, 2700, 1480)
img_expanded_clean = Image.fromarray(img_e)

# tpx0lh 也找一下水印
img_f_pil = Image.open(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_tpx0lhtpx0lhtpx0.png")).convert("RGB")
img_f = np.array(img_f_pil).astype(float)
fh, fw, _ = img_f.shape
# 扫描
region_f = img_f[fh-200:, fw-300:]
anomalies_f = []
for y in range(8, region_f.shape[0]-8, 2):
    for x in range(8, region_f.shape[1]-8, 2):
        center = region_f[y, x]
        surround = np.mean(region_f[max(0,y-8):y+8, max(0,x-8):x+8], axis=(0,1))
        diff = np.sqrt(np.sum((center - surround)**2))
        if diff > 10:
            anomalies_f.append((fw-300+x, fh-200+y))

if anomalies_f:
    xs = [p[0] for p in anomalies_f]
    ys = [p[1] for p in anomalies_f]
    print(f"Folded watermark: x=[{min(xs)},{max(xs)}] y=[{min(ys)},{max(ys)}]")
    img_f_int = img_f.astype(np.uint8)
    img_f_int = inpaint_region(img_f_int, min(xs)-10, min(ys)-10, max(xs)+10, max(ys)+10)
    img_folded_clean = Image.fromarray(img_f_int)
else:
    print("No watermark found in folded image")
    img_folded_clean = img_f_pil

# ===== 重新合成 =====
CANVAS_W, CANVAS_H = 3200, 1800

def get_bg_color(img, samples=50):
    arr = np.array(img)
    h, w, _ = arr.shape
    colors = []
    for i in range(samples):
        colors.append(arr[h*i//samples, 3])
        colors.append(arr[h*i//samples, w-3])
        colors.append(arr[3, w*i//samples])
    return tuple(int(np.mean([c[ch] for c in colors])) for ch in range(3))

bg_f = get_bg_color(img_folded_clean)
bg_e = get_bg_color(img_expanded_clean)
BG_COLOR = tuple((a+b)//2 for a, b in zip(bg_f, bg_e))

# 画布渐变
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H))
draw_bg = ImageDraw.Draw(canvas)
for y in range(CANVAS_H):
    ratio = y / CANVAS_H
    r = int(BG_COLOR[0] + (220-BG_COLOR[0]) * ratio * 0.15)
    g = int(BG_COLOR[1] + (225-BG_COLOR[1]) * ratio * 0.15)
    b = int(BG_COLOR[2] + (230-BG_COLOR[2]) * ratio * 0.15)
    draw_bg.line([(0, y), (CANVAS_W, y)], fill=(min(r,255), min(g,255), min(b,255)))

# 产品提取
def extract_product(img, bg_color, feather=20):
    w, h = img.size
    img_rgba = img.convert("RGBA")
    arr = np.array(img).astype(float)
    bg = np.array(bg_color).reshape(1, 1, 3).astype(float)
    diff = np.sqrt(np.sum((arr - bg)**2, axis=2))
    mask_arr = np.where(diff > 22, 255, 0).astype(np.uint8)
    mask_img = Image.fromarray(mask_arr)
    mask_blur = mask_img.filter(ImageFilter.GaussianBlur(radius=6))
    mask_arr2 = np.array(mask_blur)
    mask_arr2 = np.where(mask_arr2 > 60, 255, mask_arr2).astype(np.uint8)
    final_mask = Image.fromarray(mask_arr2).filter(ImageFilter.GaussianBlur(radius=feather))
    img_rgba.putalpha(final_mask)
    return img_rgba

product_folded = extract_product(img_folded_clean, bg_f)
product_expanded = extract_product(img_expanded_clean, bg_e)

# 缩放
target_h_expanded = int(CANVAS_H * 0.58)
scale_e = target_h_expanded / product_expanded.size[1]
new_expanded = product_expanded.resize(
    (int(product_expanded.size[0] * scale_e), target_h_expanded), Image.LANCZOS)

target_h_folded = int(CANVAS_H * 0.52)
scale_f = target_h_folded / product_folded.size[1]
new_folded = product_folded.resize(
    (int(product_folded.size[0] * scale_f), target_h_folded), Image.LANCZOS)

# 布局
bottom_line = CANVAS_H - 240
center_gap = 120
expanded_x = CANVAS_W // 2 + center_gap // 2
expanded_y = bottom_line - new_expanded.size[1]
folded_x = CANVAS_W // 2 - center_gap // 2 - new_folded.size[0]
folded_y = bottom_line - new_folded.size[1]
folded_x = max(80, folded_x)
expanded_x = min(CANVAS_W - new_expanded.size[0] - 80, expanded_x)

canvas.paste(new_folded, (folded_x, folded_y), new_folded)
canvas.paste(new_expanded, (expanded_x, expanded_y), new_expanded)

# 标注
draw = ImageDraw.Draw(canvas)
font_title = font_sub = font_label = None
for fp in [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    if os.path.exists(fp):
        font_title = ImageFont.truetype(fp, 60)
        break
for fp in [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]:
    if os.path.exists(fp):
        font_sub = ImageFont.truetype(fp, 34)
        font_label = ImageFont.truetype(fp, 40)
        break

title_color = (40, 48, 58)
sub_color = (90, 100, 118)
accent_color = (55, 125, 195)
line_color = (130, 145, 168)

draw.text((CANVAS_W//2, 65), "Adjustable Height & Extendable Head",
          fill=title_color, font=font_title, anchor="mt")
draw.text((CANVAS_W//2, 140), "Effortlessly adapt to any workspace",
          fill=sub_color, font=font_sub, anchor="mt")

folded_cx = folded_x + new_folded.size[0] // 2
expanded_cx = expanded_x + new_expanded.size[0] // 2
draw.text((folded_cx, bottom_line+25), "Compact", fill=sub_color, font=font_label, anchor="mt")
draw.text((expanded_cx, bottom_line+25), "Extended", fill=sub_color, font=font_label, anchor="mt")

# 箭头
arrow_cx = CANVAS_W // 2
arrow_cy = (max(folded_y, expanded_y) + bottom_line) // 2
arrow_len = 40
draw.line([(arrow_cx-arrow_len, arrow_cy), (arrow_cx+arrow_len, arrow_cy)], fill=accent_color, width=4)
draw.polygon([(arrow_cx+arrow_len+2, arrow_cy),
              (arrow_cx+arrow_len-16, arrow_cy-12),
              (arrow_cx+arrow_len-16, arrow_cy+12)], fill=accent_color)

# 高度虚线
def draw_dashed_vline(draw, x, y1, y2, color, width=2, dash=10, gap=7):
    y = y1
    while y < y2:
        end = min(y+dash, y2)
        draw.line([(x, y), (x, end)], fill=color, width=width)
        y = end + gap

hl_x = folded_x - 45
draw_dashed_vline(draw, hl_x, folded_y+20, bottom_line, line_color)
draw.line([(hl_x-12, folded_y+20), (hl_x+12, folded_y+20)], fill=line_color, width=2)
draw.line([(hl_x-12, bottom_line), (hl_x+12, bottom_line)], fill=line_color, width=2)

hr_x = expanded_x + new_expanded.size[0] + 45
draw_dashed_vline(draw, hr_x, expanded_y+20, bottom_line, line_color)
draw.line([(hr_x-12, expanded_y+20), (hr_x+12, expanded_y+20)], fill=line_color, width=2)
draw.line([(hr_x-12, bottom_line), (hr_x+12, bottom_line)], fill=line_color, width=2)

output_path = os.path.join(OUTPUT_DIR, "comparison_height_extend_final.png")
canvas.save(output_path, "PNG")
print(f"Done: {output_path}")
