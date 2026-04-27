"""
提升图片清晰度和分辨率
1. LANCZOS 2x 放大
2. Unsharp Mask 锐化
3. 对比度微调
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
    ok, buf = cv2.imencode(ext, img, [cv2.IMWRITE_PNG_COMPRESSION, 3])
    with open(path, 'wb') as f:
        f.write(buf.tobytes())

img = cv_read(os.path.join(OUTPUT_DIR, "Gemini_Generated_Image_o3j4xno3j4xno3j4.png"))
h, w = img.shape[:2]
print(f"Original: {w}x{h}")

# 1. 放大 2x（用 INTER_LANCZOS4，最高质量插值）
scale = 2
upscaled = cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_LANCZOS4)
print(f"Upscaled: {upscaled.shape[1]}x{upscaled.shape[0]}")

# 2. Unsharp Mask 锐化
# 原理：锐化 = 原图 + (原图 - 模糊图) * amount
def unsharp_mask(image, sigma=1.5, amount=1.2, threshold=0):
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
    # 防止溢出
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    return sharpened

sharp = unsharp_mask(upscaled, sigma=1.5, amount=1.0)

# 3. 轻微对比度增强（CLAHE - 自适应直方图均衡）
lab = cv2.cvtColor(sharp, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
l_enhanced = clahe.apply(l)
enhanced = cv2.merge([l_enhanced, a, b])
result = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

# 保存
output_path = os.path.join(OUTPUT_DIR, "o3j4xn_enhanced_2x.png")
cv_write(output_path, result)

# 文件大小
size_mb = os.path.getsize(output_path) / 1024 / 1024
print(f"Done: {output_path}")
print(f"Output: {result.shape[1]}x{result.shape[0]}, {size_mb:.1f} MB")
