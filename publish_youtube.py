import os, sys, json, time
import config

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

def get_youtube_credentials():
    """Retrieves and refreshes YouTube OAuth2 credentials from token file or environment variable."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    raw_token = os.environ.get("YOUTUBE_TOKEN_JSON", "")
    token_data = None

    if raw_token.strip():
        try:
            token_data = json.loads(raw_token)
        except Exception:
            pass

    if not token_data:
        # Check local repo token.json
        local_p = os.path.join(config.BASE_DIR, "token.json")
        if os.path.exists(local_p):
            with open(local_p, "r", encoding="utf-8") as f:
                token_data = json.load(f)

    if not token_data:
        # Fallback to local default path
        fallback_p = r"C:\Users\kreg9\Downloads\kreggscode\open code\bots\youtube refresh tokens bot\token_The Freudian Depths.json"
        if os.path.exists(fallback_p):
            with open(fallback_p, "r", encoding="utf-8") as f:
                token_data = json.load(f)

    if not token_data or not token_data.get("refresh_token"):
        print("[YouTube Uploader] No valid YouTube refresh token found.")
        return None

    creds = Credentials(
        None,
        refresh_token=token_data["refresh_token"],
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

    try:
        creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"[YouTube Uploader] Error refreshing OAuth token: {e}")
        return None

def upload_to_youtube(video_path: str, thumbnail_path: str, metadata: dict, privacy: str = "public") -> str:
    """Uploads video to YouTube with title, description, tags, and custom 1080p thumbnail."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_youtube_credentials()
    if not creds:
        print("[YouTube Uploader] Skipping upload: credentials not configured.")
        return None

    youtube = build("youtube", "v3", credentials=creds)

    title = metadata.get("title", f"{config.CHANNEL_NAME} Episode")
    description = metadata.get("description", "")
    tags = metadata.get("tags", ["Sigmund Freud", "Psychoanalysis", "Psychology", "Unconscious Mind", "Freudian Depths"])

    body = {
        "snippet": {
            "title": title[:100],  # YouTube title limit
            "description": description[:5000],
            "tags": tags,
            "categoryId": "27"  # Education
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    print(f"\n[YouTube Uploader] Initializing upload for: '{title[:60]}...'")
    media = MediaFileUpload(video_path, chunksize=10 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    file_size = os.path.getsize(video_path)
    print(f"[YouTube Uploader] Uploading {file_size / (1024 * 1024):.1f} MB to YouTube ({privacy})...")

    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  [YouTube Progress] {pct}% uploaded...")

    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"[YouTube Uploader] SUCCESS! Video live at: {video_url}")

    # Upload custom thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"[YouTube Uploader] Setting custom 1080p thumbnail: {os.path.basename(thumbnail_path)}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("[YouTube Uploader] Custom thumbnail set successfully.")
        except Exception as e:
            print(f"[YouTube Uploader] Warning setting thumbnail: {e}")

    return video_url
