"""
在 v3 基础上修复水印：直接在最终图上用背景色覆盖水印区域
"""
from PIL import Image, ImageDraw, ImageFilter
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
img = Image.open(os.path.join(OUTPUT_DIR, "comparison_height_extend_v3.png")).convert("RGB")
draw = ImageDraw.Draw(img)

w, h = img.size

# 右下角水印区域：采样附近背景色后覆盖
# 水印大约在右下角 (w-120, h-300) 到 (w-30, h-220) 区域
# 采样周围背景色
sample_colors = []
for sx in range(w-200, w-150):
    for sy in range(h-350, h-320):
        sample_colors.append(img.getpixel((sx, sy)))

avg_r = sum(c[0] for c in sample_colors) // len(sample_colors)
avg_g = sum(c[1] for c in sample_colors) // len(sample_colors)
avg_b = sum(c[2] for c in sample_colors) // len(sample_colors)
bg = (avg_r, avg_g, avg_b)

# 覆盖水印区域（稍大范围保证覆盖）
draw.rectangle([w-140, h-310, w-20, h-210], fill=bg)

# 左图底部也可能有水印残留，检查并覆盖
# 左图的电源线末端区域
sample_colors2 = []
for sx in range(700, 750):
    for sy in range(h-310, h-280):
        sample_colors2.append(img.getpixel((sx, sy)))
avg_r2 = sum(c[0] for c in sample_colors2) // len(sample_colors2)
avg_g2 = sum(c[1] for c in sample_colors2) // len(sample_colors2)
avg_b2 = sum(c[2] for c in sample_colors2) // len(sample_colors2)

output_path = os.path.join(OUTPUT_DIR, "comparison_height_extend_final.png")
img.save(output_path, "PNG")
print(f"Done: {output_path}")
