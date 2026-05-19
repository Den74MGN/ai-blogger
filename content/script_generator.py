import json
from openai import OpenAI
from pathlib import Path
from config import Config

SYSTEM_PROMPT = """Ты — IT-блогер-девушка, которая ведёт популярный YouTube-канал про технологии.
Твой тон: дружелюбный, живой, с лёгким юмором. Ты объясняешь сложные IT-штуки простым языком.

Темы твоего канала:
- Новинки в мире AI и нейросетей
- Полезные IT-инструменты и сервисы
- Обзоры технологий
- Лайфхаки для разработчиков
- Будущее технологий

Правила:
- Пиши текст для видео на русском языке
- Длина: 400-600 символов (1.5-2 минуты озвучки)
- Начинай с приветствия зрителей
- Заканчивай призывом подписаться
- Не используй markdown
- Сделай текст естественным, как живую речь"""

IT_TOPICS = [
    "почему ChatGPT стал умнее в 2026 и что изменилось",
    "топ-5 бесплатных AI инструментов для разработчика",
    "как нейросети меняют IT-образование",
    "что такое агентный AI и зачем он нужен",
    "обзор новой IDE от Microsoft с AI-начинкой",
    "как использовать Claude для написания кода",
    "топ библиотек Python которые стоит знать в 2026",
    "как AI помогает в тестировании кода",
    "что такое MCP протокол и почему о нём говорят",
    "5 AI сервисов которые заменят целую команду",
    "как нейросети пишут код лучше джуниоров",
    "обзор новых моделей от DeepSeek и Qwen",
]

POLICY_TEXT = """Не используй упоминания политики, войны, религии, пропаганды.
Не давай финансовых или инвестиционных советов.
Не упоминай конкретные политические события или фигуры."""


def generate_script(topic: str | None = None) -> str:
    client = OpenAI(
        api_key=Config.LLM_API_KEY,
        base_url=Config.LLM_BASE_URL,
    )

    if topic is None:
        import random
        topic = random.choice(IT_TOPICS)

    user_prompt = f"""Напиши текст для видео на тему: {topic}

{SYSTEM_PROMPT}

{POLICY_TEXT}"""

    response = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        temperature=0.8,
        max_tokens=800,
    )

    text = response.choices[0].message.content.strip()

    import re
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    return text


def save_script(text: str, topic: str) -> Path:
    import re
    sanitized = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "_")
    filename = f"script_{sanitized[:40]}.txt"
    path = Config.SCRIPTS_DIR / filename
    path.write_text(text, encoding="utf-8")
    return path


if __name__ == "__main__":
    text = generate_script()
    print(text)
    print(f"\n---\nДлина: {len(text)} символов")
