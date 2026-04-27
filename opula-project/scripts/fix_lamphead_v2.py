"""
修改 o3j4xn 左灯灯头 v2
- 加大旋转角度到15度
- 灯头整体右移，缩短伸出距离
- 更好的融合
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

img = cv_read(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4xno3j4xno3j4.png"))
h, w = img.shape[:2]

# 更大的 ROI，包含整个灯头+折臂上半部分
roi_x1, roi_y1 = 80, 180
roi_x2, roi_y2 = 780, 540

# 旋转中心：灯臂与灯头的连接点（铰链位置）
# 在原图中大约 (640, 430)
pivot_abs = (640, 430)
pivot_rel = (pivot_abs[0] - roi_x1, pivot_abs[1] - roi_y1)

angle = -15  # 顺时针15度
# 同时加一点平移（向右推灯头）
tx = 30  # 右移30px

roi = img[roi_y1:roi_y2, roi_x1:roi_x2].copy()
roi_h, roi_w = roi.shape[:2]

# 旋转+平移矩阵
M = cv2.getRotationMatrix2D(pivot_rel, angle, 1.0)
M[0, 2] += tx  # 加上水平平移

rotated = cv2.warpAffine(roi, M, (roi_w, roi_h),
                          flags=cv2.INTER_LANCZOS4,
                          borderMode=cv2.BORDER_REPLICATE)

# 更精细的融合蒙版
# 只对灯头部分（上半区域）应用修改，下半区域保留原样
mask = np.zeros((roi_h, roi_w), dtype=np.uint8)

# 灯头主体区域（上半部分的中心）
# 用多边形定义灯头范围
pts = np.array([
    [50, 30],       # 左上
    [roi_w - 80, 30],  # 右上
    [roi_w - 40, roi_h // 2 + 20],  # 右中
    [80, roi_h // 2 + 40],   # 左中
], dtype=np.int32)
cv2.fillPoly(mask, [pts], 255)

# 大范围模糊实现羽化
mask = cv2.GaussianBlur(mask, (61, 61), 30)

# 混合
mask_f = mask.astype(float) / 255.0
mask_3ch = cv2.merge([mask_f, mask_f, mask_f])

original_roi = img[roi_y1:roi_y2, roi_x1:roi_x2].astype(float)
rotated_f = rotated.astype(float)
blended = rotated_f * mask_3ch + original_roi * (1 - mask_3ch)
img[roi_y1:roi_y2, roi_x1:roi_x2] = blended.astype(np.uint8)

# 保存
output_path = os.path.join(OUTPUT_DIR, "o3j4xn_fixed_v2.png")
cv_write(output_path, img)
print(f"Done: {output_path}")
