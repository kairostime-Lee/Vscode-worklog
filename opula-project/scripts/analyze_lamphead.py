"""
分析 o3j4xn 中两个灯头的位置和大小
以及原始照片中灯头的位置
"""
from PIL import Image
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
PHOTO_DIR = r"D:\ClaudeWork\产品图片\产品实物照片"

# o3j4xn 尺寸
img = Image.open(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4xno3j4xno3j4.png"))
print(f"o3j4xn size: {img.size}")

# 原始照片尺寸
for name in ["894A8944.JPG", "894A8937.JPG"]:
    p = Image.open(os.path.join(PHOTO_DIR, name))
    print(f"{name} size: {p.size}")
