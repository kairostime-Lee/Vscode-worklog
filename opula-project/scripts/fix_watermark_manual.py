"""
手动修复水印 - 基于视觉定位
水印是 Gemini 的菱形小图标，在原图右下角
在合成图中位于右侧图的右下区域
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
img = Image.open(os.path.join(OUTPUT_DIR, "comparison_height_extend_v3.png")).convert("RGB")
arr = np.array(img)
h, w, _ = arr.shape

# 从v3合成图来看，水印在右下角大约 (3020-3100, 1400-1480) 区域
# 还有左图可能有一个在底部电源线附近

# 方法：用 inpainting 风格修复 —— 从上方取一行像素往下复制
def patch_area(arr, x1, y1, x2, y2, ref_offset=-10):
    """用参考行（上方 ref_offset 行）的像素覆盖目标区域"""
    for y in range(y1, min(y2, arr.shape[0])):
        for x in range(x1, min(x2, arr.shape[1])):
            ref_y = y1 + ref_offset
            if 0 <= ref_y < arr.shape[0]:
                arr[y, x] = arr[ref_y, x]

# 尝试多个可能的水印位置（右下角区域）
# 搜索右下角 400x400 范围内的半透明白色图案
scan_region = arr[h-400:h, w-400:w].copy()
scan_h, scan_w, _ = scan_region.shape

# 计算局部背景（3x3 块平均）
# 水印特征：比周围像素稍亮且偏白
# 用局部方差检测
# 手动做
# 简单策略：对右下角区域做轻微模糊覆盖
region_y1, region_y2 = h-250, h-180
region_x1, region_x2 = w-130, w-40

# 用区域上方的像素行覆盖
for y in range(region_y1, region_y2):
    for x in range(region_x1, region_x2):
        arr[y, x] = arr[region_y1 - 8, x]

# 同时处理左图底部可能的水印
# 左图电源线末端附近
region2_y1, region2_y2 = h-280, h-220
region2_x1, region2_x2 = 740, 830

for y in range(region2_y1, region2_y2):
    for x in range(region2_x1, region2_x2):
        arr[y, x] = arr[region2_y1 - 8, x]

result = Image.fromarray(arr)

# 最后整体做一次轻微的背景统一：
# 对画布边缘做一圈模糊融合
output_path = os.path.join(OUTPUT_DIR, "comparison_height_extend_final.png")
result.save(output_path, "PNG")
print(f"Done: {output_path}, size: {w}x{h}")
