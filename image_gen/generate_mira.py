#!/usr/bin/env python3
"""Генерация каноничного изображения Миры."""

import torch
from diffusers import AutoPipelineForText2Image, EulerAncestralDiscreteScheduler
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIRA_PROMPTS = {
    "portrait": (
        "professional photo of young female tech presenter Mira, 27 years old, "
        "pleasant European appearance, shoulder-length dark blonde bob haircut, "
        "one thin neon blue hair streak on front, natural makeup, "
        "intelligent friendly eyes, modern tech-casual outfit, "
        "waist-up portrait, soft studio lighting, AI studio background, "
        "clean high quality, realistic photo, serene confident expression"
    ),
    "tech_host": (
        "professional photo of Mira, female AI presenter, 27, "
        "light blazer, dark top, confident neutral expression, "
        "shoulder-length dark blonde hair with blue streak, "
        "standing in modern AI studio with large screen, "
        "professional look, soft cool lighting, photorealistic"
    ),
    "blogger": (
        "photo of Mira, female tech blogger, 27, "
        "soft light hoodie, friendly genuine smile, "
        "dark blonde bob with subtle blue streak, "
        "casual tech background, warm lighting, "
        "approachable digital creator, waist-up shot"
    ),
    "expert": (
        "photo of Mira, female technology expert, 27, "
        "dark minimalist jacket, holding tablet, "
        "dark blonde hair with blue front streak, "
        "modern studio with analytical screens, "
        "elegant professional aesthetic, realistic photo"
    ),
}

NEGATIVE_PROMPT = (
    "anime, cartoon, child, exaggerated, glamour, "
    "low quality, bad anatomy, extra fingers, "
    "distorted face, unrealistic, jewelry, earrings, "
    "heavy makeup, cleavage, sexy, revealing"
)


def generate_mira(
    style: str = "portrait",
    output_name: str | None = None,
    width: int = 768,
    height: int = 1024,
    seed: int = 42,
) -> Path:
    prompt = MIRA_PROMPTS.get(style, MIRA_PROMPTS["portrait"])
    output_name = output_name or f"mira_{style}.png"
    output_path = OUTPUT_DIR / output_name
    if output_path.exists():
        print(f"Already exists: {output_path}")
        return output_path

    print(f"Loading model...")
    model_id = "stabilityai/sdxl-turbo"

    pipe = AutoPipelineForText2Image.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
    )
    pipe = pipe.to("cuda")
    pipe.enable_model_cpu_offload()

    generator = torch.Generator("cuda").manual_seed(seed)

    print(f"Generating: {style}...")
    image = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE_PROMPT,
        num_inference_steps=4,
        guidance_scale=0.0,
        width=width,
        height=height,
        generator=generator,
    ).images[0]

    image.save(str(output_path))
    print(f"Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    styles = list(MIRA_PROMPTS.keys())
    style = sys.argv[1] if len(sys.argv) > 1 else "portrait"
    if style not in styles:
        print(f"Styles: {', '.join(styles)}")
        sys.exit(1)
    generate_mira(style)
