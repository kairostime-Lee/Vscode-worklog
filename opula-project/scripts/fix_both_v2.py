"""
修改 o3j4-1：
1. 左灯灯头右移 115px 接上灯臂
2. 右灯截短灯杆 34px
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

# =============================================
# 修改1：左灯灯头向右平移 115px
# =============================================
# 灯头区域（包含灯头水平条+顶部发光面）
head_x1, head_y1 = 100, 340
head_x2, head_y2 = 730, 600
shift_right = 115

# 提取灯头
head_region = img[head_y1:head_y2, head_x1:head_x2].copy()
head_h, head_w = head_region.shape[:2]

# 采样背景色（灯头上方的背景）
bg_samples = []
for y in range(head_y1-40, head_y1-10):
    for x in range(head_x1, head_x1+200):
        bg_samples.append(img[y, x])
bg_color = np.mean(bg_samples, axis=0).astype(np.uint8)

# 用背景色填充灯头原始位置左侧（平移留出的空白）
# 逐列采样上方背景，更自然
for x in range(head_x1, head_x1 + shift_right + 20):
    if x < w:
        # 取该列上方的背景色
        col_bg = img[head_y1-20, x].copy()
        img[head_y1:head_y2, x] = col_bg

# 粘贴灯头到新位置
new_x1 = head_x1 + shift_right
new_x2 = min(new_x1 + head_w, w)
paste_w = new_x2 - new_x1

# 创建羽化蒙版
mask = np.ones((head_h, paste_w), dtype=np.float32)
feather_left = 30
feather_right = 20
# 左边缘羽化
for i in range(feather_left):
    mask[:, i] = i / feather_left
# 右边缘羽化
for i in range(feather_right):
    if paste_w - 1 - i >= 0:
        mask[:, paste_w - 1 - i] = i / feather_right
# 顶部和底部也羽化
feather_tb = 20
for i in range(feather_tb):
    mask[i, :] *= i / feather_tb
    mask[head_h - 1 - i, :] *= i / feather_tb

mask_3ch = cv2.merge([mask, mask, mask])

target = img[head_y1:head_y2, new_x1:new_x2].astype(float)
source = head_region[:, :paste_w].astype(float)
blended = source * mask_3ch + target * (1 - mask_3ch)
img[head_y1:head_y2, new_x1:new_x2] = blended.astype(np.uint8)

print("Left head shifted 115px right")

# =============================================
# 修改2：右灯截短灯杆
# =============================================
cut_y_top = 603
cut_y_bottom = 637
cut_height = cut_y_bottom - cut_y_top  # 34px

right_lamp_x1 = 1500
right_lamp_x2 = 2650

# 保存截断线以上的区域
upper = img[0:cut_y_top, right_lamp_x1:right_lamp_x2].copy()

# 背景色填充顶部空出的区域（逐列取背景色）
for x_idx in range(right_lamp_x2 - right_lamp_x1):
    x = right_lamp_x1 + x_idx
    bg_col = img[20, x].copy()
    img[0:cut_height, x] = bg_col

# 上方区域下移
img[cut_height:cut_y_top + cut_height, right_lamp_x1:right_lamp_x2] = upper[0:cut_y_top, :]

# 接缝平滑
seam_y = cut_y_bottom
for dy in range(-8, 8):
    y = seam_y + dy
    if 1 <= y < h - 1:
        img[y, right_lamp_x1:right_lamp_x2] = (
            img[y, right_lamp_x1:right_lamp_x2].astype(float) * 0.6 +
            img[y-1, right_lamp_x1:right_lamp_x2].astype(float) * 0.2 +
            img[y+1, right_lamp_x1:right_lamp_x2].astype(float) * 0.2
        ).astype(np.uint8)

print("Right pole shortened")

# 保存
output = os.path.join(OUTPUT_DIR, "o3j4_final_v2.png")
cv_write(output, img)
print(f"Done: {output}")
