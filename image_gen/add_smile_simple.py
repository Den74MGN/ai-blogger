#!/usr/bin/env python3
"""Add smile using SDXL-Turbo - composite approach: generate smile patch and blend."""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import torch
from diffusers import StableDiffusionXLImg2ImgPipeline

SRC = Path(r"D:\OpenCode\ai-blogger\image_gen\output\reference_portrait.png")
OUT = Path(r"D:\OpenCode\ai-blogger\image_gen\output\reference_portrait_smile.png")

# Load reference
img = cv2.imread(str(SRC))
h, w = img.shape[:2]

# Use SadTalker's face detection from the venv
# Instead, let's use simple face detection with adjusted params
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Try detecting the main face
faces = face_cascade.detectMultiScale(gray, 1.02, 3, minSize=(150, 150))
print(f"Faces detected: {len(faces)}")

if len(faces) == 0:
    # fallback - assume face is in upper center portion
    print("No face detected, using center region")
    # guess face region based on typical portrait composition
    fx, fy, fw, fh = w//3, h//6, w//3, h//2
else:
    fx, fy, fw, fh = max(faces, key=lambda r: r[2]*r[3])
    
print(f"Face region: ({fx},{fy}) {fw}x{fh}")

# Face mouth region
my1 = fy + int(fh * 0.55)
my2 = fy + int(fh * 0.8)
mx1 = fx + int(fw * 0.15)
mx2 = fx + int(fw * 0.85)

# Extract face and mouth
face_img = img[fy:fy+fh, fx:fx+fw]
face_pil = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))

print("Loading SDXL-Turbo...")
pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float32,
    variant="fp16",
    use_safetensors=True,
)
pipe = pipe.to("cuda")

# resize face to SDXL size
face_resized = face_pil.resize((768, 1024), Image.LANCZOS)

# Run on face area with low strength
prompt = (
    "photo of woman with perfect natural open smile showing white teeth, "
    "Hollywood smile, veneers, happy confident expression, "
    "photorealistic portrait, professional photography, natural look"
)
negative = "closed mouth, frown, serious, ugly, deformed, blurry, low quality, cartoon, drawing"

print("Generating smile on face region...")
try:
    result_face = pipe(
        prompt=prompt,
        negative_prompt=negative,
        image=face_resized,
        strength=0.3,
        num_inference_steps=4,
        guidance_scale=0.0,
        generator=torch.Generator("cuda").manual_seed(42),
    ).images[0]
    
    result_face_resized = np.array(result_face.resize((fw, fh), Image.LANCZOS))
    result_face_resized = cv2.cvtColor(result_face_resized, cv2.COLOR_RGB2BGR)
    
    # Blend: use only the mouth region from result, keep rest from original
    mouth_orig = img[my1:my2, mx1:mx2].astype(np.float32)
    mouth_new = result_face_resized[my1-fy:my2-fy, mx1-fx:mx2-fx].astype(np.float32)
    
    if mouth_orig.shape[:2] == mouth_new.shape[:2] and mouth_orig.size > 0:
        # Feather blend around mouth region
        mh, mw = mouth_orig.shape[:2]
        mask = np.zeros((mh, mw), dtype=np.float32)
        cv2.ellipse(mask, (mw//2, mh//2), (mw//2, mh//2), 0, 0, 360, 1.0, -1)
        mask = cv2.GaussianBlur(mask, (21, 21), 7)
        mask_3ch = np.stack([mask, mask, mask], axis=2)
        
        blended = mouth_orig * (1 - mask_3ch * 0.8) + mouth_new * (mask_3ch * 0.8)
        img[my1:my2, mx1:mx2] = np.clip(blended, 0, 255).astype(np.uint8)
        print(f"Mouth region blended: {mw}x{mh}")
    else:
        print(f"Shape mismatch: orig={mouth_orig.shape} new={mouth_new.shape}")
        # Just use the whole face result
        img[fy:fy+fh, fx:fx+fw] = result_face_resized
    
    cv2.imwrite(str(OUT), img)
    print(f"Saved: {OUT}")
except Exception as e:
    print(f"Error: {e}")
    cv2.imwrite(str(OUT), img)
    print("Saved original as fallback")
