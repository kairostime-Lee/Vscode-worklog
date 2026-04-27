"""
在 o3j4xn 上替换灯头：
- 保留 o3j4xn 的完美排版、背景、灯杆
- 用原始照片的灯头替换掉 Gemini 想象的灯头
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
PHOTO_DIR = r"D:\ClaudeWork\产品图片\产品实物照片"

# 加载图片
base = Image.open(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4xno3j4xno3j4.png")).convert("RGBA")
photo_compact = Image.open(os.path.join(PHOTO_DIR, "894A8944.JPG")).convert("RGBA")
photo_extended = Image.open(os.path.join(PHOTO_DIR, "894A8937.JPG")).convert("RGBA")

base_w, base_h = base.size
print(f"Base: {base_w}x{base_h}")

# ============================
# 步骤1: 从原始照片中裁出灯头区域
# ============================

# 894A8944 (收起状态) - 照片是横拍的，灯头在图片右上区域
# 照片尺寸 6720x4480
# 灯头（水平条+折臂顶部）大约在：
# 实际观察照片，灯头+折臂上部区域
compact_head_crop = photo_compact.crop((3200, 200, 5800, 2200))
print(f"Compact head crop: {compact_head_crop.size}")

# 894A8937 (展开状态) - 灯头拉出更远
extended_head_crop = photo_extended.crop((2800, 0, 6000, 2200))
print(f"Extended head crop: {extended_head_crop.size}")

# 保存裁剪结果供检查
compact_head_crop.save(os.path.join(OUTPUT_DIR, "_debug_compact_head.png"))
extended_head_crop.save(os.path.join(OUTPUT_DIR, "_debug_extended_head.png"))
print("Saved debug crops for inspection")
