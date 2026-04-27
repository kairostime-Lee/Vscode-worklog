"""
用 OpenCV 在 o3j4xn 上修改左灯灯头角度
策略：选中左灯灯头区域 → 旋转使其更水平 → 无缝融合回原图
"""
import cv2
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"
img_path = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4xno3j4xno3j4.png")

img = cv2.imread(img_path)
h, w = img.shape[:2]
print(f"Image: {w}x{h}")

# 先保存一份标注图，标出我认为的灯头区域，供用户确认
debug = img.copy()

# 左灯灯头区域（目测 o3j4xn）
# 左灯整体在画面左侧，灯头在左上区域
# 大约 x: 180-750, y: 200-550
cv2.rectangle(debug, (180, 200), (750, 550), (0, 255, 0), 3)
cv2.putText(debug, "LEFT head", (200, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

# 右灯灯头区域
# 大约 x: 1950-2580, y: 100-450
cv2.rectangle(debug, (1950, 100), (2580, 450), (0, 0, 255), 3)
cv2.putText(debug, "RIGHT head", (1970, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

debug_path = os.path.join(OUTPUT_DIR, "_debug_head_regions.png")
cv2.imwrite(debug_path, debug)
print(f"Saved debug: {debug_path}")
