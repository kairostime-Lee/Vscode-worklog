"""
精确定位水印并用周围像素插值修复
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
img = Image.open(os.path.join(OUTPUT_DIR, "comparison_height_extend_v3.png")).convert("RGB")
arr = np.array(img)
h, w, _ = arr.shape

# 水印是白色/亮色的菱形小图标，在右下角
# 扫描右下角区域找到异常亮的像素
region = arr[h-350:h-180, w-180:w-20]
# 计算区域平均背景亮度
bg_brightness = np.mean(region[:20, :20, :])  # 左上角小块作参考

# 找亮度异常高的区域（水印）
brightness = np.mean(region, axis=2)
watermark_mask = brightness > (bg_brightness + 30)

if np.any(watermark_mask):
    ys, xs = np.where(watermark_mask)
    y_min, y_max = ys.min(), ys.max()
    x_min, x_max = xs.min(), xs.max()
    print(f"Watermark found in region: ({x_min},{y_min}) to ({x_max},{y_max})")
    print(f"Absolute: ({w-180+x_min},{h-350+y_min}) to ({w-180+x_max},{h-350+y_max})")

    # 在原图上用周围背景色填充水印区域（带 margin）
    margin = 8
    abs_y1 = h - 350 + y_min - margin
    abs_y2 = h - 350 + y_max + margin
    abs_x1 = w - 180 + x_min - margin
    abs_x2 = w - 180 + x_max + margin

    # 采样水印上方一行的颜色做渐变填充
    for y in range(abs_y1, min(abs_y2 + 1, h)):
        for x in range(abs_x1, min(abs_x2 + 1, w)):
            # 用上方和左方像素插值
            ref_y = max(abs_y1 - 5, 0)
            ref_x = x
            arr[y, x] = arr[ref_y, ref_x]

    print("Watermark patched")
else:
    print("No obvious watermark detected in scan region")

# 同样处理左图可能的水印残留
# 扫描左图下方
region_left = arr[h-350:h-180, 600:900]
brightness_left = np.mean(region_left, axis=2)
bg_left = np.mean(region_left[:20, :20, :])
wm_left = brightness_left > (bg_left + 35)
if np.any(wm_left):
    ys, xs = np.where(wm_left)
    print(f"Left watermark area: x={xs.min()}-{xs.max()}, y={ys.min()}-{ys.max()}")
    margin = 8
    for y in range(h-350+ys.min()-margin, min(h-350+ys.max()+margin+1, h)):
        for x in range(600+xs.min()-margin, min(600+xs.max()+margin+1, w)):
            ref_y = max(h-350+ys.min()-5, 0)
            arr[y, x] = arr[ref_y, x]
    print("Left watermark patched")

result = Image.fromarray(arr)
output_path = os.path.join(OUTPUT_DIR, "comparison_height_extend_final.png")
result.save(output_path, "PNG")
print(f"Done: {output_path}")
