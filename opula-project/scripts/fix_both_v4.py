"""
v4: 左灯灯头右移 155px + 接缝处用周围像素填充
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
# 修改1：左灯灯头右移 155px + 接缝修复
# =============================================
head_x1, head_y1 = 100, 330
head_x2, head_y2 = 750, 610
shift_right = 155

head_region = img[head_y1:head_y2, head_x1:head_x2].copy()
head_h, head_w = head_region.shape[:2]

# 背景填充（逐列取上方背景色）
for x in range(head_x1, min(head_x1 + shift_right + 40, w)):
    bg1 = img[head_y1 - 25, x].astype(float)
    bg2 = img[head_y1 - 15, x].astype(float)
    avg_bg = ((bg1 + bg2) / 2).astype(np.uint8)
    img[head_y1:head_y2, x] = avg_bg

# 粘贴灯头（右侧不羽化，直接硬接）
new_x1 = head_x1 + shift_right
new_x2 = min(new_x1 + head_w, w)
paste_w = new_x2 - new_x1

mask = np.ones((head_h, paste_w), dtype=np.float32)
# 只对左侧和上下羽化
feather_left = 25
for i in range(feather_left):
    mask[:, i] = i / feather_left
feather_tb = 12
for i in range(feather_tb):
    mask[i, :] *= i / feather_tb
    if head_h - 1 - i >= 0:
        mask[head_h - 1 - i, :] *= i / feather_tb
# 右侧完全不羽化，让灯头叠在灯臂上

mask_3ch = cv2.merge([mask, mask, mask])
target = img[head_y1:head_y2, new_x1:new_x2].astype(float)
source = head_region[:, :paste_w].astype(float)
blended = source * mask_3ch + target * (1 - mask_3ch)
img[head_y1:head_y2, new_x1:new_x2] = blended.astype(np.uint8)

# 接缝修复：在灯头右端和灯臂交界处做 inpaint
# 交界处大约在 x=840~870（shift后灯头右端在 head_x2+shift=750+155=905 附近）
# 但灯臂折弯在约 x=820
# 所以灯头现在应该叠盖了灯臂的一部分，连接应该更紧密
# 用 OpenCV inpaint 修复残留缝隙
joint_x1 = new_x2 - 30  # 灯头右端附近
joint_x2 = new_x2 + 20
joint_y1 = head_y1 + 10
joint_y2 = head_y2 - 10

# 在接缝区域检测异常像素（和周围差异大的点）
joint_region = img[joint_y1:joint_y2, joint_x1:joint_x2]
gray = cv2.cvtColor(joint_region, cv2.COLOR_BGR2GRAY)

# 用中值滤波平滑接缝
smoothed = cv2.medianBlur(joint_region, 5)
diff = cv2.absdiff(joint_region, smoothed)
diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
_, inpaint_mask = cv2.threshold(diff_gray, 15, 255, cv2.THRESH_BINARY)

if np.any(inpaint_mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    inpaint_mask = cv2.dilate(inpaint_mask, kernel, iterations=1)
    repaired = cv2.inpaint(joint_region, inpaint_mask, 5, cv2.INPAINT_TELEA)
    img[joint_y1:joint_y2, joint_x1:joint_x2] = repaired

print("Left lamp fixed")

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

print("Right pole shortened")

# 保存 + 检查
output = os.path.join(OUTPUT_DIR, "o3j4_final_v4.png")
cv_write(output, img)

# 放大连接处
crop = img[330:620, 720:950]
zoomed = cv2.resize(crop, (crop.shape[1]*3, crop.shape[0]*3), interpolation=cv2.INTER_LANCZOS4)
cv_write(os.path.join(OUTPUT_DIR, "_check_joint_v4.png"), zoomed)
print("Done")
