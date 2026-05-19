import subprocess
from pathlib import Path
from config import Config, BASE_DIR
import random


def get_media_duration(path: Path) -> float:
    r = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path)
    ], capture_output=True, text=True, timeout=30)
    return float(r.stdout.strip())


def compose_final_video(
    avatar_video: Path | None = None,
    audio_path: Path | None = None,
    background: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    avatar_video = avatar_video or Config.AVATAR_OUTPUT / "avatar_animated.mp4"
    audio_path = audio_path or Config.AUDIO_DIR / "voice.mp3"
    output_path = output_path or Config.FINAL_DIR / "final_video.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_dur = get_media_duration(audio_path)
    avatar_dur = get_media_duration(avatar_video)

    bg_files = list(Config.BACKGROUND_DIR.glob("*.*"))
    if not bg_files:
        bg_files = list(Config.BASE_DIR.glob("avatar/source/*.png"))
    bg = random.choice(bg_files) if bg_files else None

    if bg and bg.exists():
        bg_scale = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
        av_overlay = "scale=640:640"
        loop_count = max(1, int(audio_dur / avatar_dur) + 1)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(bg),
            "-stream_loop", str(loop_count), "-i", str(avatar_video),
            "-i", str(audio_path),
            "-filter_complex",
            f"[0:v]{bg_scale}[bg];"
            f"[1:v]{av_overlay}[av];"
            f"[bg][av]overlay=(W-w)/2:(H-h)/2:format=auto,format=yuv420p[vout]",
            "-map", "[vout]",
            "-map", "2:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(output_path),
        ]
    else:
        loop_count = max(1, int(audio_dur / avatar_dur) + 1)
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", str(loop_count), "-i", str(avatar_video),
            "-i", str(audio_path),
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(output_path),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error:\n{result.stderr}")

    return output_path


if __name__ == "__main__":
    result = compose_final_video()
    print(f"Video saved: {result}")
