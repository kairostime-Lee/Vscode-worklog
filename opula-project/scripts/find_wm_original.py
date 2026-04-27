"""
在原始 Gemini 图上扫描水印 - 检查整个底部区域
"""
from PIL import Image
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
name = "Gemini_Generated_Image_bjq553bjq553bjq5.png"
img = Image.open(os.path.join(OUTPUT_DIR, name)).convert("RGB")
arr = np.array(img).astype(float)
h, w, _ = arr.shape

# 扫描底部 200px, 右侧 300px
region = arr[h-200:, w-300:]
rh, rw, _ = region.shape

# 用局部对比度检测
anomalies = []
step = 2
for y in range(8, rh-8, step):
    for x in range(8, rw-8, step):
        center = region[y, x]
        surround = np.mean(region[max(0,y-8):y+8, max(0,x-8):x+8], axis=(0,1))
        diff = np.sqrt(np.sum((center - surround)**2))
        if diff > 10:
            anomalies.append((w-300+x, h-200+y, diff, center))

if anomalies:
    anomalies.sort(key=lambda r: -r[2])
    print(f"Found {len(anomalies)} anomalies")
    # Group by proximity
    clusters = []
    used = set()
    for i, (ax, ay, ad, ac) in enumerate(anomalies[:100]):
        if i in used:
            continue
        cluster = [(ax, ay, ad)]
        used.add(i)
        for j, (bx, by, bd, bc) in enumerate(anomalies[:100]):
            if j not in used and abs(ax-bx) < 40 and abs(ay-by) < 40:
                cluster.append((bx, by, bd))
                used.add(j)
        if len(cluster) >= 3:
            clusters.append(cluster)

    for ci, cluster in enumerate(clusters[:5]):
        xs = [p[0] for p in cluster]
        ys = [p[1] for p in cluster]
        print(f"Cluster {ci}: {len(cluster)} pts, "
              f"x=[{min(xs)},{max(xs)}] y=[{min(ys)},{max(ys)}] "
              f"center=({(min(xs)+max(xs))//2},{(min(ys)+max(ys))//2})")
else:
    print("No anomalies found")

# Also check: what does the very bottom-right corner look like?
print(f"\nBottom-right 60x60 brightness stats:")
br = arr[h-60:, w-60:]
print(f"  Mean: {np.mean(br):.1f}, Std: {np.std(br):.1f}")
print(f"  Min: {np.min(br):.0f}, Max: {np.max(br):.0f}")

# Sample specific pixels in bottom-right
for dy in [20, 30, 40, 50]:
    for dx in [20, 30, 40, 50]:
        px = arr[h-dy, w-dx]
        print(f"  ({w-dx},{h-dy}): RGB=({px[0]:.0f},{px[1]:.0f},{px[2]:.0f})")
