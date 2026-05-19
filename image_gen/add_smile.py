#!/usr/bin/env python3
"""Add smile via SDXL-Turbo img2img full-frame low-strength."""
import torch
from diffusers import AutoPipelineForImage2Image
from pathlib import Path
from PIL import Image

SRC = Path(r"D:\OpenCode\ai-blogger\image_gen\output\reference_portrait.png")
OUT = Path(r"D:\OpenCode\ai-blogger\image_gen\output\reference_portrait_smile.png")

print("Loading model...")
pipe = AutoPipelineForImage2Image.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True,
)
pipe = pipe.to("cuda")
pipe.enable_attention_slicing()
pipe.vae.to(torch.float32)

img = Image.open(SRC).convert("RGB")
w, h = img.size
# SDXL-Turbo native size
target_w, target_h = 768, 1024
img_resized = img.resize((target_w, target_h), Image.LANCZOS)

prompt = (
    "close-up portrait of a woman with a perfect natural Hollywood smile, "
    "showing beautiful white teeth, lips slightly parted, confident happy expression, "
    "professional photo, realistic skin texture, natural makeup"
)
negative = "ugly, deformed, blurry, low quality, distorted, cartoon, anime, painting"

print("Generating smile version (strength=0.2)...")
result = pipe(
    prompt=prompt,
    negative_prompt=negative,
    image=img_resized,
    strength=0.2,
    num_inference_steps=4,
    guidance_scale=0.0,
    generator=torch.Generator("cuda").manual_seed(42),
).images[0]

result = result.resize((w, h), Image.LANCZOS)
result.save(str(OUT))
print(f"Saved: {OUT}")
print("Done!")
