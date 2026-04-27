"""
用 OpenCV 精确修改左灯灯头 - 坐标已通过网格确认
灯头区域: x=180~820, y=380~580
旋转锚点（折臂连接处）: (800, 490)
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

img = cv_read(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4xno3j4xno3j4.png"))
h, w = img.shape[:2]
original = img.copy()

# === 精确的灯头区域 ===
# 扩大 ROI 范围，给旋转留余量
roi_x1, roi_y1 = 100, 280
roi_x2, roi_y2 = 880, 650

# 旋转锚点（折臂连接处，相对于 ROI）
pivot = (800 - roi_x1, 490 - roi_y1)  # (700, 210)

# 旋转角度：顺时针 20 度
angle = -20

# 提取 ROI
roi = img[roi_y1:roi_y2, roi_x1:roi_x2].copy()
roi_h, roi_w = roi.shape[:2]

# 旋转矩阵（绕锚点）
M = cv2.getRotationMatrix2D(pivot, angle, 1.0)
# 加一点向右平移（让灯头收拢）
M[0, 2] += 30

# 旋转
rotated = cv2.warpAffine(roi, M, (roi_w, roi_h),
                          flags=cv2.INTER_LANCZOS4,
                          borderMode=cv2.BORDER_REPLICATE)

# === 创建精确蒙版 ===
# 只对灯头水平条部分应用修改（多边形蒙版）
mask = np.zeros((roi_h, roi_w), dtype=np.uint8)

# 灯头多边形（相对于 ROI 的坐标）
# 原始图坐标 - roi_x1/roi_y1
head_pts = np.array([
    [160 - roi_x1, 390 - roi_y1],   # 灯头左端顶部
    [820 - roi_x1, 340 - roi_y1],   # 右端顶部
    [840 - roi_x1, 520 - roi_y1],   # 右端中
    [800 - roi_x1, 590 - roi_y1],   # 右端底部
    [160 - roi_x1, 570 - roi_y1],   # 左端底部
], dtype=np.int32)

cv2.fillPoly(mask, [head_pts], 255)

# 大范围高斯模糊实现羽化（柔和过渡）
mask_blur = cv2.GaussianBlur(mask, (81, 81), 35)
mask_f = mask_blur.astype(float) / 255.0
mask_3ch = cv2.merge([mask_f, mask_f, mask_f])

# 混合
original_roi = img[roi_y1:roi_y2, roi_x1:roi_x2].astype(float)
rotated_f = rotated.astype(float)
blended = rotated_f * mask_3ch + original_roi * (1 - mask_3ch)
img[roi_y1:roi_y2, roi_x1:roi_x2] = np.clip(blended, 0, 255).astype(np.uint8)

# === 保存 ===
output = os.path.join(OUTPUT_DIR, "o3j4xn_fixed_final.png")
cv_write(output, img)
print(f"Done: {output}")

# 对比图
cmp = np.hstack([cv2.resize(original, (w//2, h//2)), cv2.resize(img, (w//2, h//2))])
cv_write(os.path.join(OUTPUT_DIR, "_compare_final.png"), cmp)
print("Comparison saved")
