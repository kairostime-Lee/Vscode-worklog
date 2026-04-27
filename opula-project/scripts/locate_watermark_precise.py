"""
精确定位水印 - 扫描右下角所有非均匀像素
"""
from PIL import Image
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"

# 直接扫描合成图的右下角
img = Image.open(os.path.join(OUTPUT_DIR, "comparison_height_extend_v3.png")).convert("RGB")
arr = np.array(img)
h, w, _ = arr.shape

# 扫描右下角 300x300
region = arr[h-300:h, w-300:w].astype(float)
rh, rw, _ = region.shape

# 计算每个像素与其 5x5 邻域均值的差异（检测局部异常）
result = []
for y in range(5, rh-5):
    for x in range(5, rw-5):
        neighborhood = region[y-5:y+5, x-5:x+5, :]
        mean_color = np.mean(neighborhood, axis=(0,1))
        pixel = region[y, x]
        diff = np.sqrt(np.sum((pixel - mean_color)**2))
        if diff > 15:  # 与邻域差异明显
            result.append((x, y, diff, pixel))

if result:
    # 按差异排序，取前20
    result.sort(key=lambda r: -r[2])
    print(f"Found {len(result)} anomalous pixels in bottom-right 300x300")
    print("Top 20:")
    for x, y, diff, px in result[:20]:
        abs_x = w - 300 + x
        abs_y = h - 300 + y
        print(f"  abs({abs_x}, {abs_y}) local({x},{y}) diff={diff:.1f} color={px}")

    # 聚类找水印中心
    xs = [r[0] for r in result[:50]]
    ys = [r[1] for r in result[:50]]
    cx = (min(xs) + max(xs)) // 2
    cy = (min(ys) + max(ys)) // 2
    print(f"\nCluster center (local): ({cx}, {cy})")
    print(f"Cluster center (abs): ({w-300+cx}, {h-300+cy})")
    print(f"Cluster bounds (abs): x=[{w-300+min(xs)}, {w-300+max(xs)}] y=[{h-300+min(ys)}, {h-300+max(ys)}]")
else:
    print("No anomalous pixels found")
