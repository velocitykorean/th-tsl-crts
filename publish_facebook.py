import os, sys, json, requests
import config

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

GRAPH_API_VERSION = "v20.0"

def get_facebook_credentials():
    page_id = (os.getenv('FB_PAGE_ID') or os.getenv('FACEBOOK_PAGE_ID') or '').strip()
    access_token = (os.getenv('FB_PAGE_ACCESS_TOKEN') or os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN') or '').strip()

    if not page_id or not access_token:
        return None, None
    return page_id, access_token

def upload_video_facebook(video_path: str, title: str, description: str) -> str:
    """Uploads video to Facebook page via Meta Graph API."""
    page_id, access_token = get_facebook_credentials()
    if not page_id or not access_token:
        print("[Facebook Publisher] FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN not yet configured. Skipping Facebook publish.")
        return None

    file_size = os.path.getsize(video_path)
    print(f"\n[Facebook Publisher] Initializing upload for: '{title[:60]}...' ({file_size / (1024 * 1024):.1f} MB)...")

    start_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
    start_payload = {
        "upload_phase": "start",
        "file_size": file_size,
        "access_token": access_token
    }
    resp = requests.post(start_url, data=start_payload, timeout=60)
    if resp.status_code != 200:
        print(f"[Facebook Publisher] Upload START failed ({resp.status_code}): {resp.text}")
        return None

    start_data = resp.json()
    upload_session_id = start_data["upload_session_id"]
    video_id = start_data.get("video_id")
    start_offset = int(start_data.get("start_offset", 0))
    end_offset = int(start_data.get("end_offset", 0))

    chunk_size = end_offset - start_offset if end_offset > start_offset else (4 * 1024 * 1024)
    with open(video_path, "rb") as f:
        while start_offset < file_size:
            f.seek(start_offset)
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break

            transfer_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
            t_data = {
                "upload_phase": "transfer",
                "upload_session_id": upload_session_id,
                "start_offset": start_offset,
                "access_token": access_token
            }
            t_files = {"video_file_chunk": chunk_data}
            t_resp = requests.post(transfer_url, data=t_data, files=t_files, timeout=120)
            if t_resp.status_code != 200:
                print(f"[Facebook Publisher] Chunk upload failed ({t_resp.status_code}): {t_resp.text}")
                return None

            t_json = t_resp.json()
            start_offset = int(t_json.get("start_offset", start_offset + len(chunk_data)))
            end_offset = int(t_json.get("end_offset", start_offset))
            pct = min(100, int((start_offset / file_size) * 100))
            print(f"  [Facebook Progress] {pct}% transferred...")

    finish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
    finish_payload = {
        "upload_phase": "finish",
        "upload_session_id": upload_session_id,
        "access_token": access_token,
        "title": title,
        "description": description
    }
    f_resp = requests.post(finish_url, data=finish_payload, timeout=60)
    if f_resp.status_code == 200:
        f_json = f_resp.json()
        final_video_id = f_json.get("id", video_id)
        fb_url = f"https://www.facebook.com/{final_video_id}"
        print(f"[Facebook Publisher] SUCCESS! Video published: {fb_url}")
        return fb_url
    else:
        print(f"[Facebook Publisher] FINISH phase failed: {f_resp.text}")
        return None
