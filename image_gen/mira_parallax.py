#!/usr/bin/env python3
"""3D-параллакс видео Миры — максимально простая версия."""

import subprocess
from pathlib import Path
from config import Config, BASE_DIR

OUTPUT_DIR = BASE_DIR / "image_gen" / "output"


def get_duration(path: Path) -> float:
    r = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path)
    ], capture_output=True, text=True, timeout=30)
    return float(r.stdout.strip())


def make_mira_video(
    image_path: Path | None = None,
    audio_path: Path | None = None,
    output_path: Path | None = None,
    duration: float | None = None,
) -> Path:
    image_path = image_path or OUTPUT_DIR / "mira_portrait.png"
    audio_path = audio_path or Config.AUDIO_DIR / "voice.mp3"
    output_path = output_path or Config.FINAL_DIR / "mira_video.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    if duration is None and audio_path.exists():
        duration = get_duration(audio_path)
    duration = duration or 10.0

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(audio_path),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e",
        "-t", str(duration),
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error:\n{result.stderr}")

    return output_path


if __name__ == "__main__":
    result = make_mira_video(output_path=Path("D:/OpenCode/ai-blogger/content/final/mira_video.mp4"))
    print(f"Video: {result}")
