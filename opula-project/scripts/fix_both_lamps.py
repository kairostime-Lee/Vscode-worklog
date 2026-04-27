"""
在 o3j4-1 原图上执行两个修改：
1. 左灯：灯头向右平移，连接上灯臂
2. 右灯：在红色标记处截掉一小节灯杆（约34px高），降低上半部分
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

# 用 o3j4-1 作为原图（没有红色标记的干净版）
img = cv_read(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4-1.png"))
h, w = img.shape[:2]
print(f"Image: {w}x{h}")

# =============================================
# 修改1：左灯灯头向右平移
# =============================================
# 从网格图确认：左灯灯头在 x=180~700, y=380~570
# 灯臂连接处在约 x=760
# 灯头需要向右平移约 60-80px 才能接上灯臂

# 选区：左灯灯头部分（不包括灯臂）
head_x1, head_y1 = 140, 360
head_x2, head_y2 = 720, 590
shift_right = 70  # 向右平移像素数

# 提取灯头区域
head_region = img[head_y1:head_y2, head_x1:head_x2].copy()
head_h, head_w = head_region.shape[:2]

# 先用背景色填充原来灯头的位置（左侧留出的空白）
# 采样灯头左上方的背景色
bg_sample = img[head_y1-30:head_y1-10, head_x1:head_x1+50]
bg_color = np.mean(bg_sample, axis=(0, 1)).astype(np.uint8)

# 填充灯头原位置的左侧（只填移动留出的空白部分）
img[head_y1:head_y2, head_x1:head_x1+shift_right] = bg_color

# 将灯头粘贴到右移后的位置
new_x1 = head_x1 + shift_right
new_x2 = new_x1 + head_w
# 确保不超出范围
if new_x2 <= w:
    # 用渐变蒙版混合边缘
    # 创建水平渐变蒙版（左边缘羽化）
    mask = np.ones((head_h, head_w), dtype=np.float32)
    feather = 25
    for i in range(feather):
        mask[:, i] = i / feather
    # 右边缘也羽化
    for i in range(feather):
        mask[:, head_w - 1 - i] = i / feather

    mask_3ch = cv2.merge([mask, mask, mask])

    target = img[head_y1:head_y2, new_x1:new_x2].astype(float)
    source = head_region.astype(float)
    blended = source * mask_3ch + target * (1 - mask_3ch)
    img[head_y1:head_y2, new_x1:new_x2] = blended.astype(np.uint8)

print("Left lamp head shifted right")

# =============================================
# 修改2：右灯截短灯杆
# =============================================
# 红色标记位置：y=603~637（在右灯灯杆上，x=1617~1684）
# 需要截掉这 34px 的灯杆高度
# 方法：把红色标记以上的部分（灯头+灯杆上段）整体下移34px

cut_y_top = 603    # 截断起点
cut_y_bottom = 637  # 截断终点
cut_height = cut_y_bottom - cut_y_top  # 34px

# 右灯的 x 范围（大约）
right_lamp_x1 = 1500
right_lamp_x2 = 2650

# 把截断线以上、右灯区域内的所有像素下移 cut_height
# 先保存上方区域
upper_region = img[0:cut_y_top, right_lamp_x1:right_lamp_x2].copy()

# 用背景色填充顶部空出的区域
bg_sample_right = img[50:80, right_lamp_x1+50:right_lamp_x1+100]
bg_color_right = np.mean(bg_sample_right, axis=(0, 1)).astype(np.uint8)
img[0:cut_height, right_lamp_x1:right_lamp_x2] = bg_color_right

# 将上方区域下移
img[cut_height:cut_y_top+cut_height, right_lamp_x1:right_lamp_x2] = upper_region[0:cut_y_top, :]

# 在接缝处做融合（cut_y_bottom 附近）
# 上下各取10px做渐变混合
seam_y = cut_height + cut_y_top  # 接缝位置（应该等于 cut_y_bottom + cut_height ... 不对）
# 重新理解：上方区域下移了 cut_height，所以原来 y=0~603 的内容现在在 y=34~637
# 原来 y=637 以下的内容没动
# 接缝在 y=637 附近

seam_y = cut_y_bottom
blend_range = 15
for dy in range(-blend_range, blend_range):
    y = seam_y + dy
    if 0 <= y < h:
        alpha = (dy + blend_range) / (2 * blend_range)
        # 上方（已移动的）和下方（未移动的）混合
        if y - 1 >= 0 and y + 1 < h:
            img[y, right_lamp_x1:right_lamp_x2] = (
                img[y, right_lamp_x1:right_lamp_x2].astype(float) * 0.7 +
                img[y-1, right_lamp_x1:right_lamp_x2].astype(float) * 0.15 +
                img[y+1, right_lamp_x1:right_lamp_x2].astype(float) * 0.15
            ).astype(np.uint8)

print("Right lamp pole shortened")

# =============================================
# 保存
# =============================================
output = os.path.join(OUTPUT_DIR, "o3j4_final_fixed.png")
cv_write(output, img)
print(f"Done: {output}")
