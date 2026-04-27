"""
用 OpenCV 修改 o3j4xn 左灯灯头角度
Unicode 路径用 numpy + imdecode 解决
"""
import cv2
import numpy as np
import os

OUTPUT_DIR = r"D:\ClaudeWork\海报输出"

def cv_read(path):
    with open(path, 'rb') as f:
        data = np.frombuffer(f.read(), np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

def cv_write(path, img):
    ext = os.path.splitext(path)[1]
    ok, buf = cv2.imencode(ext, img)
    with open(path, 'wb') as f:
        f.write(buf.tobytes())

img_path = os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4xno3j4xno3j4.png")
img = cv_read(img_path)
h, w = img.shape[:2]
print(f"Image: {w}x{h}")

# 标注灯头区域供确认
debug = img.copy()
cv2.rectangle(debug, (180, 200), (750, 550), (0, 255, 0), 3)
cv2.putText(debug, "LEFT head", (200, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.rectangle(debug, (1950, 100), (2580, 450), (0, 0, 255), 3)
cv2.putText(debug, "RIGHT head", (1970, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

debug_path = os.path.join(OUTPUT_DIR, "_debug_head_regions.png")
cv_write(debug_path, debug)
print(f"Saved: {debug_path}")
