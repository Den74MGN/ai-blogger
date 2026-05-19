import cv2
import numpy as np
import os
import subprocess
import sys
import json

TEMP_DIR = r'D:\OpenCode\ai-blogger\content\temp_studio'
os.makedirs(TEMP_DIR, exist_ok=True)
REF_DIR = r'D:\OpenCode\ai-blogger\content\ref_photos'
OUTPUT = r'D:\OpenCode\ai-blogger\content\final\ref00_studio_fhd.mp4'

FPS = 25
TOTAL_FRAMES = 499
W, H = 1080, 1920

VIDEO_SOURCE = r'D:\OpenCode\ai-blogger\content\final\2026_05_15_16.07.09.mp4'

BACKGROUNDS = [
    os.path.join(REF_DIR, 'ref_05.png'),
    os.path.join(REF_DIR, 'ref_01.png'),
    os.path.join(REF_DIR, 'ref_02.png'),
    os.path.join(REF_DIR, 'ref_06.png'),
    os.path.join(REF_DIR, 'ref_04.png'),
]

def load_image(path):
    img = cv2.imread(path)
    if img is None:
        print(f'  WARN: cannot load {path}')
        return None
    h, w = img.shape[:2]
    target = (W, H)
    scale = max(W / w, H / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    y = (new_h - H) // 2
    x = (new_w - W) // 2
    cropped = resized[y:y+H, x:x+W]
    return cropped

def smoothstep(t):
    return t * t * (3 - 2 * t)

def get_background(frame_idx):
    n = len(BACKGROUNDS)
    seg_len = TOTAL_FRAMES // n
    seg = frame_idx // seg_len
    local = (frame_idx % seg_len) / seg_len
    idx_a = min(seg, n - 1)
    idx_b = min(seg + 1, n - 1)

    bg_a = getattr(get_background, 'cache', {}).get(idx_a)
    if bg_a is None:
        bg_a = load_image(BACKGROUNDS[idx_a])
        if not hasattr(get_background, 'cache'):
            get_background.cache = {}
        get_background.cache[idx_a] = bg_a

    if idx_a == idx_b:
        return bg_a

    bg_b = getattr(get_background, 'cache', {}).get(idx_b)
    if bg_b is None:
        bg_b = load_image(BACKGROUNDS[idx_b])
        get_background.cache[idx_b] = bg_b

    t = smoothstep(local)
    return cv2.addWeighted(bg_a, 1 - t, bg_b, t, 0)

def extract_foreground(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    kernel = np.ones((15, 15), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.GaussianBlur(mask, (21, 21), 0)
    mask_f = mask.astype(np.float32) / 255.0
    return mask_f[..., None]

def breathing_transform(frame, t):
    h, w = frame.shape[:2]
    breath = 1.0 + 0.003 * np.sin(t * 2 * np.pi * 0.3)
    sway_x = 2.0 * np.sin(t * 2 * np.pi * 0.15)
    sway_y = 1.0 * np.sin(t * 2 * np.pi * 0.2)
    M = np.float32([[breath, 0, sway_x], [0, breath, sway_y]])
    return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

print('Loading video frames...')
cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print('ERROR: cannot open video source')
    sys.exit(1)

orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f'Source: {orig_w}x{orig_h}')

frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()
print(f'Loaded {len(frames)} frames')

if len(frames) == 0:
    print('ERROR: no frames loaded')
    sys.exit(1)

print(f'Compositing {TOTAL_FRAMES} frames...')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(OUTPUT, fourcc, FPS, (W, H))

for i in range(TOTAL_FRAMES):
    src_idx = i % len(frames)
    t = i / FPS

    bg = get_background(i)

    fg_frame = frames[src_idx].copy()
    fg_h, fg_w = fg_frame.shape[:2]

    scale = W / fg_w
    new_w, new_h = W, int(fg_h * scale)
    fg_scaled = cv2.resize(fg_frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    canvas = np.zeros((H, W, 3), dtype=np.uint8)
    y_offset = (H - new_h) // 2
    canvas[y_offset:y_offset+new_h, :] = fg_scaled

    mask = np.zeros((H, W), dtype=np.float32)
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask_bin = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    mask_bin = cv2.morphologyEx(mask_bin, cv2.MORPH_CLOSE, kernel)
    mask_bin = cv2.morphologyEx(mask_bin, cv2.MORPH_OPEN, kernel)
    mask = cv2.GaussianBlur(mask_bin.astype(np.float32), (15, 15), 0) / 255.0

    body_animated = breathing_transform(canvas, t)

    mask_3ch = np.stack([mask]*3, axis=2)
    result = (bg * (1 - mask_3ch) + body_animated * mask_3ch).astype(np.uint8)

    out.write(result)

    if (i + 1) % 50 == 0:
        print(f'  {i+1}/{TOTAL_FRAMES}')

out.release()
print('Done composing')

ffmpeg = r'C:\Users\denk0\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe'
final = r'D:\OpenCode\ai-blogger\content\final\ref00_studio_fhd_final.mp4'
cmd = [ffmpeg, '-y', '-i', OUTPUT, '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
       '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', final]
subprocess.run(cmd, check=True)
final_size = os.path.getsize(final)
print(f'Final: {final}')
print(f'Size: {final_size/1024/1024:.1f} MB')
