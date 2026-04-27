"""
修改 o3j4-1 v3：
1. 左灯灯头右移 135px，右侧羽化缩小让衔接更紧密
2. 右灯截短灯杆 34px（同 v2）
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
# 修改1：左灯灯头右移 135px
# =============================================
head_x1, head_y1 = 100, 340
head_x2, head_y2 = 740, 600
shift_right = 135

head_region = img[head_y1:head_y2, head_x1:head_x2].copy()
head_h, head_w = head_region.shape[:2]

# 用该列上方背景色填充灯头原始左侧空白
for x in range(head_x1, head_x1 + shift_right + 30):
    if x < w:
        # 逐列取上方背景色（更自然的渐变）
        col_bg = img[head_y1 - 25, x].astype(float)
        col_bg2 = img[head_y1 - 15, x].astype(float)
        avg_bg = ((col_bg + col_bg2) / 2).astype(np.uint8)
        img[head_y1:head_y2, x] = avg_bg

# 粘贴灯头
new_x1 = head_x1 + shift_right
new_x2 = min(new_x1 + head_w, w)
paste_w = new_x2 - new_x1

# 蒙版：左侧羽化30px，右侧只羽化8px（紧密衔接灯臂）
mask = np.ones((head_h, paste_w), dtype=np.float32)
feather_left = 30
feather_right = 8  # 右侧几乎不羽化，让灯头硬接灯臂
for i in range(feather_left):
    mask[:, i] = i / feather_left
for i in range(feather_right):
    if paste_w - 1 - i >= 0:
        mask[:, paste_w - 1 - i] = i / feather_right
# 顶底羽化
feather_tb = 15
for i in range(feather_tb):
    mask[i, :] *= i / feather_tb
    if head_h - 1 - i >= 0:
        mask[head_h - 1 - i, :] *= i / feather_tb

mask_3ch = cv2.merge([mask, mask, mask])

target = img[head_y1:head_y2, new_x1:new_x2].astype(float)
source = head_region[:, :paste_w].astype(float)
blended = source * mask_3ch + target * (1 - mask_3ch)
img[head_y1:head_y2, new_x1:new_x2] = blended.astype(np.uint8)

# =============================================
# 修改2：右灯截短灯杆
# =============================================
cut_y_top = 603
cut_y_bottom = 637
cut_height = cut_y_bottom - cut_y_top
right_lamp_x1 = 1500
right_lamp_x2 = 2650

upper = img[0:cut_y_top, right_lamp_x1:right_lamp_x2].copy()

for x in range(right_lamp_x1, right_lamp_x2):
    bg_col = img[20, x].copy()
    img[0:cut_height, x] = bg_col

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

# 保存
output = os.path.join(OUTPUT_DIR, "o3j4_final_v3.png")
cv_write(output, img)

# 放大检查连接处
crop = img[330:620, 700:950]
zoomed = cv2.resize(crop, (crop.shape[1]*3, crop.shape[0]*3), interpolation=cv2.INTER_LANCZOS4)
cv_write(os.path.join(OUTPUT_DIR, "_check_joint_v3.png"), zoomed)
print("Done")
