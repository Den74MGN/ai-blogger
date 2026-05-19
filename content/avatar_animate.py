import subprocess
import sys
from pathlib import Path
from config import Config, BASE_DIR


def animate_with_liveportrait(
    source_image: Path | None = None,
    driving_video: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """
    Анимирует фото аватара с помощью LivePortrait.
    source_image: фото лица
    driving_video: видео-драйвер (движения)
    output_path: куда сохранить
    """
    source_image = source_image or Config.AVATAR_SOURCE_IMAGE
    driving_video = driving_video or Config.DRIVING_VIDEO
    output_path = output_path or Config.AVATAR_OUTPUT / "avatar_animated.mp4"

    lp_dir = BASE_DIR / "LivePortrait"

    if not lp_dir.exists():
        raise RuntimeError(
            "LivePortrait не установлен. "
            "Запусти скрипт setup_liveportrait.bat или установи вручную:\n"
            f"  cd {lp_dir}\n"
            "  git clone https://github.com/KlingAIResearch/LivePortrait .\n"
            "  pip install -r requirements.txt\n"
            "  huggingface-cli download KlingTeam/LivePortrait --local-dir pretrained_weights --exclude '*.git*' README.md"
        )

    cmd = [
        sys.executable, str(lp_dir / "inference.py"),
        "-s", str(source_image),
        "-d", str(driving_video),
        "--flag_crop_driving_video",
    ]

    result = subprocess.run(cmd, cwd=str(lp_dir), capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"LivePortrait error:\n{result.stderr}")

    generated = lp_dir / "animations" / f"{source_image.stem}--{driving_video.stem}.mp4"
    import glob
    candidates = [
        generated,
        lp_dir / "animations" / f"{source_image.stem}--{driving_video.stem}_concat.mp4",
    ]
    found = [f for f in candidates if f.exists()]
    if found:
        import shutil
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(found[0]), str(output_path))
        return output_path

    raise FileNotFoundError(f"LivePortrait output not found in {lp_dir / 'animations'}")
