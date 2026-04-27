"""
修改 o3j4xn 左灯灯头：旋转使其更水平收拢
步骤：
1. 裁出左灯灯头区域（含 margin）
2. 绕灯头与灯臂连接点旋转（顺时针约8-10度）
3. 用 seamlessClone 无缝融合回原图
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
original = img.copy()

# ============================
# 左灯灯头修改
# ============================
# 灯头区域（精确一点）
# 灯头水平条大约在: x=180-680, y=280-420
# 灯臂与灯头连接点大约在: (620, 400) — 这是旋转中心

# 扩大选区，包含灯头及周围背景
pad = 60
roi_x1, roi_y1 = 130, 220
roi_x2, roi_y2 = 740, 500

# 旋转参数
pivot = (620 - roi_x1, 400 - roi_y1)  # 相对于 ROI 的旋转中心
angle = -8  # 顺时针旋转8度，让灯头更水平

# 提取 ROI
roi = img[roi_y1:roi_y2, roi_x1:roi_x2].copy()
roi_h, roi_w = roi.shape[:2]

# 创建旋转矩阵
M = cv2.getRotationMatrix2D(pivot, angle, 1.0)

# 旋转 ROI
rotated_roi = cv2.warpAffine(roi, M, (roi_w, roi_h),
                              flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT_101)

# 创建融合蒙版：中心不透明，边缘渐变
mask = np.zeros((roi_h, roi_w), dtype=np.uint8)
# 椭圆蒙版，中心区域完全不透明
center = (roi_w // 2, roi_h // 2)
axes = (roi_w // 2 - pad, roi_h // 2 - pad)
cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
# 模糊蒙版边缘
mask = cv2.GaussianBlur(mask, (41, 41), 20)

# 用蒙版混合旋转后的 ROI 和原始图像
mask_3ch = cv2.merge([mask, mask, mask]).astype(float) / 255.0
blended_roi = (rotated_roi.astype(float) * mask_3ch +
               img[roi_y1:roi_y2, roi_x1:roi_x2].astype(float) * (1 - mask_3ch))
img[roi_y1:roi_y2, roi_x1:roi_x2] = blended_roi.astype(np.uint8)

# ============================
# 去水印（右下角 Gemini 菱形图标）
# ============================
# 水印大约在右下角
# 用周围背景色覆盖
wm_region = img[h-120:h-40, w-120:w-40]
# 取水印上方的背景色
bg_sample = img[h-140:h-130, w-120:w-40]
bg_color = np.mean(bg_sample, axis=(0, 1)).astype(np.uint8)
# 检测水印像素（比背景亮或不同的）
wm_gray = cv2.cvtColor(wm_region, cv2.COLOR_BGR2GRAY)
bg_gray = int(np.mean(cv2.cvtColor(bg_sample, cv2.COLOR_BGR2GRAY)))
# 用 inpaint 修复
wm_mask = np.abs(wm_gray.astype(int) - bg_gray) > 20
wm_mask = wm_mask.astype(np.uint8) * 255
if np.any(wm_mask):
    # 膨胀蒙版
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    wm_mask = cv2.dilate(wm_mask, kernel, iterations=2)
    inpainted = cv2.inpaint(wm_region, wm_mask, 10, cv2.INPAINT_TELEA)
    img[h-120:h-40, w-120:w-40] = inpainted
    print("Watermark inpainted")
else:
    print("No watermark detected in expected region")

# 保存
output_path = os.path.join(OUTPUT_DIR, "o3j4xn_fixed.png")
cv_write(output_path, img)
print(f"Done: {output_path}")

# 也保存一个对比图
comparison = np.hstack([
    cv2.resize(original, (w//2, h//2)),
    cv2.resize(img, (w//2, h//2))
])
cv_write(os.path.join(OUTPUT_DIR, "_debug_before_after.png"), comparison)
print("Saved before/after comparison")
