import asyncio
import edge_tts
from pathlib import Path
from config import Config


async def generate_audio(text: str, voice: str | None = None) -> Path:
    voice = voice or Config.TTS_VOICE
    output_path = Config.AUDIO_DIR / "voice.mp3"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

    return output_path


def run_tts(text: str, voice: str | None = None) -> Path:
    return asyncio.run(generate_audio(text, voice))


if __name__ == "__main__":
    test_text = "Привет, с вами IT-блогер! Сегодня поговорим о нейросетях."
    path = run_tts(test_text)
    print(f"Audio saved: {path}")
