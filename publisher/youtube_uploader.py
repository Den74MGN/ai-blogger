from pathlib import Path
from config import Config


def upload_to_youtube(
    video_path: Path,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
) -> str | None:
    """
    Загрузка видео на YouTube через YouTube Data API v3.
    Требуется OAuth 2.0 credentials.
    """
    if not Config.YOUTUBE_API_KEY:
        print("[YouTube] API ключ не настроен. Пропускаю.")
        return None

    try:
        import google.auth
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        creds = None
        if Config.YOUTUBE_REFRESH_TOKEN:
            creds = Credentials(
                token=None,
                refresh_token=Config.YOUTUBE_REFRESH_TOKEN,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=Config.YOUTUBE_CLIENT_ID,
                client_secret=Config.YOUTUBE_CLIENT_SECRET,
            )
            creds.refresh(Request())

        if not creds or not creds.valid:
            print("[YouTube] Нет валидных OAuth credentials. Пропускаю.")
            return None

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags or [],
                "categoryId": "28",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )
        response = request.execute()
        video_id = response.get("id")
        print(f"[YouTube] Uploaded: https://youtu.be/{video_id}")
        return video_id

    except ImportError:
        print("[YouTube] google-api-python-client не установлен.")
        return None
    except Exception as e:
        print(f"[YouTube] Error: {e}")
        return None
