#!/usr/bin/env python3
"""Upscale SadTalker output to Full HD with correct aspect ratio."""
import subprocess, sys, os
from pathlib import Path

VENV_PYTHON = r"D:\OpenCode\SadTalker\venv\Scripts\python.exe"
INPUT = r"D:\OpenCode\ai-blogger\content\final\mira_extcrop_raw.mp4"
OUTPUT = r"D:\OpenCode\ai-blogger\content\final\mira_v6_fhd.mp4"
AUDIO = r"D:\OpenCode\ai-blogger\content\audio\voice_test.mp3"
TEMP_DIR = Path(r"D:\OpenCode\ai-blogger\content\final\temp_frames")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Step 1: extract frames
sys.stdout.write("Extracting frames...\n")
subprocess.run([
    "ffmpeg", "-y", "-i", INPUT,
    "-qscale:v", "1", "-qmin", "1", "-qmax", "1",
    str(TEMP_DIR / "frame_%04d.png")
], check=True, capture_output=True)

frames = sorted(TEMP_DIR.glob("*.png"))
sys.stdout.write(f"  {len(frames)} frames extracted\n")

# Step 2: upscale with Real-ESRGAN
sys.stdout.write("Upscaling with Real-ESRGAN...\n")
upscale_script = f"""
import torch, sys, os
sys.argv = ['realesrgan-ncnn-vulkan']
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from PIL import Image
import numpy as np

model_path = r"D:\\OpenCode\\SadTalker\\gfpgan\\weights\\RealESRGAN_x4plus.pth"
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
upsampler = RealESRGANer(scale=4, model_path=model_path, model=model, tile=0, tile_pad=10, pre_pad=0, half=False if not torch.cuda.is_available() else True)

input_dir = r"{TEMP_DIR}"
for i, fname in enumerate(sorted(os.listdir(input_dir))):
    if not fname.endswith('.png'):
        continue
    fpath = os.path.join(input_dir, fname)
    img = Image.open(fpath).convert('RGB')
    img_np = np.array(img)
    output, _ = upsampler.enhance(img_np, outscale=4)
    out_img = Image.fromarray(output)
    out_img.save(os.path.join(input_dir, f'up_{fname}'))
    if (i+1) % 10 == 0:
        sys.stdout.write(f'  {{i+1}}/{{len(os.listdir(input_dir))}} frames\\n')
        sys.stdout.flush()
os.system(f'ffmpeg -y -r 12.5 -i {{input_dir}}\\\up_frame_%04d.png -i r"{AUDIO}" -c:v libx264 -preset slow -crf 18 -vf "scale=1080:1080:flags=lanczos,pad=1080:1920:0:(oh-ih)/2:color=#1a1a2e,unsharp=3:3:0.5,format=yuv420p" -c:a aac -b:a 128k -shortest r"{OUTPUT}"')
sys.stdout.write("Done!\\n")
"""

subprocess.run([
    VENV_PYTHON, "-c", upscale_script
], check=True, timeout=600)

# Cleanup
for f in TEMP_DIR.glob("*"):
    f.unlink()
TEMP_DIR.rmdir()

sys.stdout.write(f"Output: {OUTPUT}\n")
