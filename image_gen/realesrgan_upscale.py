#!/usr/bin/env python3
"""Upscale SadTalker video frames using Real-ESRGAN for realistic quality."""
import cv2
import numpy as np
import os
import sys
import tempfile
from pathlib import Path
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from PIL import Image

RAW_VIDEO = r"D:\OpenCode\ai-blogger\content\final\2026_05_15_14.19.48.mp4"
OUT_VIDEO = r"D:\OpenCode\ai-blogger\content\final\mira_v6_realesrgan.mp4"

print("Loading Real-ESRGAN model...")
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
upsampler = RealESRGANer(
    scale=4,
    model_path=r"D:\OpenCode\SadTalker\gfpgan\weights\RealESRGAN_x4plus.pth",
    model=model,
    tile=400,
    tile_pad=10,
    pre_pad=0,
    half=True,
    device='cuda',
)

# Extract & process frames
cap = cv2.VideoCapture(RAW_VIDEO)
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Video: {total_frames} frames @ {fps}fps")

frame_dir = Path(tempfile.mkdtemp())
processed_dir = Path(tempfile.mkdtemp())
print(f"Extracting frames to {frame_dir}...")

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imwrite(str(frame_dir / f"frame_{frame_idx:06d}.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    frame_idx += 1
cap.release()
print(f"Extracted {frame_idx} frames")

print("Processing frames with Real-ESRGAN (4x upscale)...")
for i in range(frame_idx):
    in_path = frame_dir / f"frame_{i:06d}.jpg"
    out_path = processed_dir / f"frame_{i:06d}.jpg"
    
    img = cv2.imread(str(in_path), cv2.IMREAD_COLOR)
    if img is None:
        continue
    
    try:
        output, _ = upsampler.enhance(img, outscale=4)
        out_1080 = cv2.resize(output, (1080, 1080), interpolation=cv2.INTER_LANCZOS4)
        h, w = out_1080.shape[:2]
        top = (1920 - h) // 2
        bottom = 1920 - h - top
        padded = cv2.copyMakeBorder(out_1080, top, bottom, 0, 0, cv2.BORDER_CONSTANT, value=(30, 26, 26))
        cv2.imwrite(str(out_path), padded, [cv2.IMWRITE_JPEG_QUALITY, 95])
    except Exception as e:
        print(f"  Frame {i} error: {e}")
        out_1080 = cv2.resize(img, (1080, 1080), interpolation=cv2.INTER_LANCZOS4)
        top = (1920 - 1080) // 2
        padded = cv2.copyMakeBorder(out_1080, top, top, 0, 0, cv2.BORDER_CONSTANT, value=(30, 26, 26))
        cv2.imwrite(str(out_path), padded, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    if i % 25 == 0:
        print(f"  Processed {i}/{frame_idx} frames ({i/frame_idx*100:.0f}%)")

# Assemble video with ffmpeg
print("Assembling video...")
import subprocess
ffmpeg = r"C:\Users\denk0\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"

# Get audio from original
audio_file = str(processed_dir.parent / "audio.aac")
cmd_extract = [ffmpeg, "-y", "-i", RAW_VIDEO, "-vn", "-c:a", "copy", audio_file]
subprocess.run(cmd_extract, capture_output=True)

# Build video from frames
cmd_build = [
    ffmpeg, "-y",
    "-framerate", str(fps),
    "-i", str(processed_dir / "frame_%06d.jpg"),
    "-i", audio_file,
    "-c:v", "libx264", "-preset", "slow", "-crf", "16",
    "-c:a", "aac",
    "-pix_fmt", "yuv420p",
    "-shortest",
    OUT_VIDEO
]
subprocess.run(cmd_build, capture_output=True)

print(f"DONE: {OUT_VIDEO}")

# Cleanup
import shutil
shutil.rmtree(frame_dir)
shutil.rmtree(processed_dir)
