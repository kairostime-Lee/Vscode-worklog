"""
只修改右灯（截短灯杆），左灯保持原样不动
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
    ok, buf = cv2.imencode('.png', img)
    with open(path, 'wb') as f:
        f.write(buf.tobytes())

img = cv_read(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4-1.png"))
h, w = img.shape[:2]

# 只做右灯截短
cut_y_top = 603
cut_y_bottom = 637
cut_height = cut_y_bottom - cut_y_top
right_lamp_x1 = 1500
right_lamp_x2 = 2650

upper = img[0:cut_y_top, right_lamp_x1:right_lamp_x2].copy()
for x in range(right_lamp_x1, right_lamp_x2):
    img[0:cut_height, x] = img[20, x].copy()
img[cut_height:cut_y_top + cut_height, right_lamp_x1:right_lamp_x2] = upper[0:cut_y_top, :]

seam_y = cut_y_bottom
for dy in range(-8, 8):
    y = seam_y + dy
    if 1 <= y < h - 1:
        img[y, right_lamp_x1:right_lamp_x2] = (
            img[y, right_lamp_x1:right_lamp_x2].astype(float) * 0.6 +
            img[y-1, right_lamp_x1:right_lamp_x2].astype(float) * 0.2 +
            img[y+1, right_lamp_x1:right_lamp_x2].astype(float) * 0.2
        ).astype(np.uint8)

output = os.path.join(OUTPUT_DIR, "o3j4_right_fixed_only.png")
cv_write(output, img)
print(f"Done: {output}")
