"""
精确定位两张 Gemini 图的水印位置
"""
from PIL import Image
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"

for name in ["Gemini_Generated_Image_tpx0lhtpx0lhtpx0.png",
             "Gemini_Generated_Image_bjq553bjq553bjq5.png"]:
    img = Image.open(os.path.join(OUTPUT_DIR, name)).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape

    # 扫描整个底部 1/4 区域，找高亮度异常点
    bottom = arr[int(h*0.7):, :, :]
    mean_bright = np.mean(bottom, axis=2)
    bg_val = np.median(mean_bright)

    # 找比背景亮 40+ 的像素簇
    bright_mask = mean_bright > (bg_val + 40)
    if np.any(bright_mask):
        ys, xs = np.where(bright_mask)
        print(f"{name}:")
        print(f"  Image size: {w}x{h}")
        print(f"  BG median brightness: {bg_val:.0f}")
        print(f"  Bright pixels: {len(ys)}")
        print(f"  Region: x=[{xs.min()}, {xs.max()}], y=[{ys.min()+int(h*0.7)}, {ys.max()+int(h*0.7)}]")
        print(f"  Center: ({(xs.min()+xs.max())//2}, {(ys.min()+ys.max())//2 + int(h*0.7)})")
    else:
        print(f"{name}: no bright anomaly found")
    print()
