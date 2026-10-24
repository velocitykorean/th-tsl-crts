import os, sys, argparse, asyncio, json, glob
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

import config
from story_generator import generate_full_podcast_story, generate_metadata, load_history_topics
from tts_engine import generate_podcast_audio
from thumbnail_generator import generate_thumbnail
from video_composer import render_podcast_video

def save_episode_history(record: dict):
    """Synchronously saves episode history to published_videos.json, history.json, and history.js."""
    base_dir = config.BASE_DIR
    p1 = os.path.join(base_dir, "published_videos.json")
    history = []
    if os.path.exists(p1):
        try:
            with open(p1, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(record)

    # 1. published_videos.json
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # 2. history.json
    p2 = os.path.join(base_dir, "history.json")
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # 3. history.js
    p3 = os.path.join(base_dir, "history.js")
    with open(p3, "w", encoding="utf-8") as f:
        f.write("// Daily Video History Log & Topic Registry\n")
        f.write("const PODCAST_HISTORY = " + json.dumps(history, indent=2, ensure_ascii=False) + ";\n")
        f.write("if (typeof module !== 'undefined' && module.exports) { module.exports = PODCAST_HISTORY; }\n")
        f.write("if (typeof window !== 'undefined') { window.PODCAST_HISTORY = PODCAST_HISTORY; }\n")

    print(f"[History] Recorded episode #{record['episode']} to history files.")

def run_auto_pipeline(target_minutes: float = 20.0, topic: str = None, dry_run: bool = False, preview_seconds: float = None, force_publish: bool = False):
    active_voice = getattr(config, "KOKORO_VOICE", config.VOICE_HOST1) if getattr(config, "TTS_ENGINE", "kokoro") == "kokoro" else config.VOICE_HOST1
    print("=" * 75)
    print(f"    [YOUTUBE BOT] {config.CHANNEL_NAME} ({config.CHANNEL_HANDLE})")
    print(f"    Target Duration: {target_minutes:.1f} minutes | Engine: {getattr(config, 'TTS_ENGINE', 'kokoro')} ({active_voice})")
    print("=" * 75)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    past_topics = load_history_topics()
    ep_num = len(past_topics) + 1

    # Step 1: Tesla Philosophical & Scientific Master Script
    print(f"\n[Step 1/4] Generating Tesla Master Script (Target: {target_minutes:.1f} mins)...")
    story = generate_full_podcast_story(target_minutes=target_minutes, topic=topic, ep_num=ep_num)

    dialogue = story["dialogue"]
    if preview_seconds:
        max_turns = max(2, int(preview_seconds / 20.0) + 1)
        dialogue = dialogue[:max_turns]
        print(f"[Preview Mode] Sliced dialogue to first {len(dialogue)} turns for rapid preview.")

    # Step 2: Speech Synthesis with WordBoundary Synchronization
    print(f"\n[Step 2/4] Synthesizing Deep Voiceover ({active_voice})...")
    master_audio, subtitle_chunks, total_dur = asyncio.run(generate_podcast_audio(dialogue))

    # Calculate chapter timestamps
    for ch in story["chapters"]:
        start_turn = ch["start_turn"]
        ch_time = 0.0
        for c in subtitle_chunks:
            if c.get("turn_idx") == start_turn:
                ch_time = c["start"]
                break
        ch["start_time"] = ch_time

    # Step 3: High-CTR YouTube Thumbnail
    print(f"\n[Step 3/4] Generating YouTube 1080p Thumbnail...")
    thumb_path = os.path.join(config.OUTPUT_DIR, f"thumb_ep{ep_num}_{timestamp}.jpg")
    
    # Automatically scan all available Tesla portraits in assets/images
    all_portraits = sorted(glob.glob(os.path.join(config.IMAGES_DIR, "*.jpg")))
    if not all_portraits:
        all_portraits = [config.DEFAULT_IMAGE_PATH]

    thumb_base_img = all_portraits[(ep_num - 1) % len(all_portraits)]
    print(f"[Image Selection] Episode #{ep_num} designated single image: {os.path.basename(thumb_base_img)} (Used statically for entire video & thumbnail)")

    generate_thumbnail(
        thumb_base_img,
        story["thumbnail_title_1"],
        story["thumbnail_title_2"],
        story["thumbnail_hook"],
        thumb_path,
        ep_number=ep_num
    )

    # Step 4: Render Full 1080p Video (Single Static Image, Single-Line Subtitles + Equalizer)
    print(f"\n[Step 4/4] Rendering 1080p Video via FFmpeg Pipe...")
    video_path = os.path.join(config.OUTPUT_DIR, f"tesla_ep{ep_num}_{timestamp}.mp4")
    render_podcast_video(
        master_audio,
        subtitle_chunks,
        video_path,
        fps=config.VIDEO_FPS,
        preview_seconds=preview_seconds,
        bg_image_path=thumb_base_img
    )

    # Generate metadata file (Title, Description, Timestamps, Tags)
    meta = generate_metadata(story["topic"], total_dur, story["chapters"], ep_num=ep_num, story=story)
    meta_path = os.path.join(config.OUTPUT_DIR, f"metadata_ep{ep_num}_{timestamp}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"[Metadata] Saved episode metadata: {meta_path}")

    # Append to all history registries
    record = {
        "episode": ep_num,
        "topic": story["topic"],
        "date": datetime.now().isoformat(),
        "duration_sec": round(total_dur, 2),
        "duration_min": round(total_dur / 60.0, 2),
        "video_file": os.path.basename(video_path),
        "thumbnail_file": os.path.basename(thumb_path),
        "metadata_file": os.path.basename(meta_path),
        "channel": config.CHANNEL_NAME,
        "handle": config.CHANNEL_HANDLE
    }
    if not dry_run and not preview_seconds:
        save_episode_history(record)

    # Step 5: Multi-Platform Publishing Controller
    # Schedule Rule: YouTube = Monday, Wednesday, Friday | Facebook = Every Day
    weekday = datetime.now().weekday()
    day_name = datetime.now().strftime("%A")
    is_yt_day = weekday in [0, 2, 4]  # Mon=0, Wed=2, Fri=4

    youtube_url = None
    facebook_url = None

    if not dry_run and not preview_seconds:
        from publish_youtube import upload_to_youtube
        from publish_facebook import upload_video_facebook

        # 1. YouTube Publishing (Mon, Wed, Fri)
        if is_yt_day or force_publish:
            print(f"\n[Publishing] Today is {day_name}. Executing YouTube upload (Mon/Wed/Fri schedule)...")
            youtube_url = upload_to_youtube(video_path, thumb_path, meta, privacy="public")
            if youtube_url:
                record["youtube_url"] = youtube_url
        else:
            print(f"\n[YouTube Schedule] Today is {day_name}. YouTube uploads run Mon/Wed/Fri. Skipping YouTube today (use --force-publish to override).")

        # 2. Facebook Publishing (Daily schedule)
        print(f"\n[Publishing] Executing Facebook upload (Daily schedule)...")
        facebook_url = upload_video_facebook(video_path, meta["title"], meta["description"])
        if facebook_url:
            record["facebook_url"] = facebook_url

        save_episode_history(record)

    print("\n" + "=" * 75)
    print(f"       PIPELINE COMPLETE! Ep. #{ep_num} ({total_dur/60:.1f} mins)")
    print(f"       Video File:     {video_path}")
    print(f"       Thumbnail:      {thumb_path}")
    print(f"       Metadata:       {meta_path}")
    if youtube_url:
        print(f"       YouTube:        {youtube_url}")
    if facebook_url:
        print(f"       Facebook:       {facebook_url}")
    print("=" * 75)
    return video_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{config.CHANNEL_NAME} Automation Pipeline")
    parser.add_argument("--duration", type=float, default=20.0, help="Target duration in minutes (default: 20.0)")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic override")
    parser.add_argument("--dry-run", action="store_true", help="Skip uploads")
    parser.add_argument("--preview", type=float, default=None, help="Render preview seconds only (e.g. 30.0)")
    parser.add_argument("--force-publish", action="store_true", help="Force publish regardless of schedule day")
    args = parser.parse_args()

    run_auto_pipeline(
        target_minutes=args.duration,
        topic=args.topic,
        dry_run=args.dry_run,
        preview_seconds=args.preview,
        force_publish=args.force_publish
    )
