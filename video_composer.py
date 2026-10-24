import os, glob, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import config
from audio_visualizer import AudioSpectrumVisualizer

def prepare_base_image(img_path: str, logo_img: Image.Image, font_brand: ImageFont.ImageFont, font_path: str) -> Image.Image:
    """Loads a single background image, resizes to 1920x1080 with cinematic grading, and stamps permanent static branding."""
    raw = Image.open(img_path).convert("RGBA")
    if raw.size != (config.VIDEO_WIDTH, config.VIDEO_HEIGHT):
        raw = raw.resize((config.VIDEO_WIDTH, config.VIDEO_HEIGHT), Image.Resampling.LANCZOS)

    # Right-side shadow gradient for depth and text legibility
    overlay = Image.new("RGBA", (config.VIDEO_WIDTH, config.VIDEO_HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for x in range(750, config.VIDEO_WIDTH):
        alpha = int(min(170, (x - 750) / (config.VIDEO_WIDTH - 750) * 170))
        ov_draw.line([(x, 0), (x, config.VIDEO_HEIGHT)], fill=(6, 8, 12, alpha))
    raw = Image.alpha_composite(raw, overlay)

    draw = ImageDraw.Draw(raw)

    # 1. Circular Channel Logo Badge with Gold Rim (Top-Left)
    logo_size = 96
    logo_x, logo_y = 50, 40
    if logo_img:
        try:
            resized_logo = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (logo_size * 4, logo_size * 4), 0)
            m_draw = ImageDraw.Draw(mask)
            m_draw.ellipse((0, 0, logo_size * 4, logo_size * 4), fill=255)
            mask = mask.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            circular_logo = Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 0))
            circular_logo.paste(resized_logo, (0, 0), mask)
            raw.paste(circular_logo, (logo_x, logo_y), circular_logo)

            draw.ellipse(
                [(logo_x - 2, logo_y - 2), (logo_x + logo_size + 2, logo_y + logo_size + 2)],
                outline=(218, 165, 32, 240),
                width=3
            )
        except Exception:
            pass

    # 2. Top Branding Pill: [Amber Dot] THE DIONYSIAN ABYSS
    bbox = draw.textbbox((0, 0), config.CHANNEL_NAME, font=font_brand)
    text_w = bbox[2] - bbox[0]
    pill_start_x = 160
    text_start_x = pill_start_x + 42
    pill_end_x = text_start_x + text_w + 30

    draw.rounded_rectangle(
        [(pill_start_x, 52), (pill_end_x, 108)],
        radius=28,
        fill=(14, 16, 24, 230),
        outline=(218, 165, 32, 220),
        width=2
    )
    dot_cx = pill_start_x + 21
    draw.ellipse([(dot_cx - 7, 80 - 7), (dot_cx + 7, 80 + 7)], fill=(245, 175, 40))
    draw.text((text_start_x, 66), config.CHANNEL_NAME, fill=(255, 255, 255), font=font_brand)

    # 3. Footer Divider and Tagline
    draw.line([(0, 1025), (config.VIDEO_WIDTH, 1025)], fill=(40, 42, 54), width=2)
    f_footer = ImageFont.truetype(font_path, 22)
    draw.text((config.SUBTITLE_CENTER_X, 1052), config.TAGLINE, fill=(215, 205, 185), font=f_footer, anchor="mm")

    return raw

def split_sentence_into_single_lines(words: list, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw, space_w: int, max_words: int = 7) -> list:
    """Splits words into single-line phrase chunks (strictly one line per chunk, centered)."""
    chunks = []
    curr_chunk = []
    curr_w = 0

    for w in words:
        w_text = w["word"]
        w_len = draw.textbbox((0, 0), w_text, font=font)[2]
        add_w = w_len if not curr_chunk else (space_w + w_len)

        # Break conditions: width exceeded OR word count reached OR punctuation pause
        has_break_punct = w_text.endswith((',', ';', ':', '—', '--', '-', '.', '?', '!'))
        exceeds_w = (curr_w + add_w > max_width)
        exceeds_count = (len(curr_chunk) >= max_words)

        if curr_chunk and (exceeds_w or exceeds_count or (len(curr_chunk) >= 4 and has_break_punct)):
            total_line_w = sum(x["width"] for x in curr_chunk) + (len(curr_chunk) - 1) * space_w
            start_x = config.SUBTITLE_CENTER_X - (total_line_w // 2)
            word_pos = []
            x_cursor = start_x
            for cw in curr_chunk:
                word_pos.append({
                    "word": cw["word"],
                    "start": cw["start"],
                    "end": cw["end"],
                    "width": cw["width"],
                    "x": x_cursor,
                    "y": config.SUBTITLE_Y
                })
                x_cursor += cw["width"] + space_w

            chunks.append({
                "start": curr_chunk[0]["start"],
                "end": curr_chunk[-1]["end"],
                "words": word_pos
            })
            curr_chunk = [{**w, "width": w_len}]
            curr_w = w_len
        else:
            curr_chunk.append({**w, "width": w_len})
            curr_w += add_w

    if curr_chunk:
        total_line_w = sum(x["width"] for x in curr_chunk) + (len(curr_chunk) - 1) * space_w
        start_x = config.SUBTITLE_CENTER_X - (total_line_w // 2)
        word_pos = []
        x_cursor = start_x
        for cw in curr_chunk:
            word_pos.append({
                "word": cw["word"],
                "start": cw["start"],
                "end": cw["end"],
                "width": cw["width"],
                "x": x_cursor,
                "y": config.SUBTITLE_Y
            })
            x_cursor += cw["width"] + space_w

        chunks.append({
            "start": curr_chunk[0]["start"],
            "end": curr_chunk[-1]["end"],
            "words": word_pos
        })

    return chunks

def render_podcast_video(audio_path: str, subtitle_chunks: list, output_video_path: str, fps: int = 30, preview_seconds: float = None, bg_image_path: str = None) -> str:
    print(f"[VideoComposer] Initializing video render: {output_video_path}...")
    visualizer = AudioSpectrumVisualizer(audio_path, fps=fps)
    total_frames = visualizer.total_frames
    if preview_seconds:
        total_frames = min(total_frames, int(preview_seconds * fps))
        print(f"[VideoComposer] Preview active: rendering {total_frames} frames ({preview_seconds:.1f}s)...")

    # Select single background image for the entire video (no image rotation)
    if not bg_image_path or not os.path.exists(bg_image_path):
        bg_image_path = config.DEFAULT_IMAGE_PATH

    print(f"[VideoComposer] Using single static background image: {os.path.basename(bg_image_path)}")

    font_path = config.FONT_PATH if os.path.exists(config.FONT_PATH) else config.FALLBACK_FONT_PATH
    font_quote = ImageFont.truetype(font_path, getattr(config, "SUBTITLE_FONT_SIZE", 48))
    font_brand = ImageFont.truetype(font_path, 28)

    # Load logo if available
    logo_img = None
    if os.path.exists(config.LOGO_PATH):
        try:
            logo_img = Image.open(config.LOGO_PATH).convert("RGBA")
        except Exception:
            logo_img = None

    # Pre-render single static base frame
    prepared_base = prepare_base_image(bg_image_path, logo_img, font_brand, font_path)

    # Process subtitle words into clean, single-line phrase chunks
    dummy_draw = ImageDraw.Draw(prepared_base)
    space_w = dummy_draw.textbbox((0, 0), " ", font=font_quote)[2]
    max_sub_w = getattr(config, "MAX_SUBTITLE_WIDTH", 880)

    single_line_chunks = []
    for c in subtitle_chunks:
        words = c.get("words", [])
        if not words:
            continue
        line_chunks = split_sentence_into_single_lines(words, font_quote, max_sub_w, dummy_draw, space_w, max_words=7)
        single_line_chunks.extend(line_chunks)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{config.VIDEO_WIDTH}x{config.VIDEO_HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video_path
    ]

    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    total_audio_sec = total_frames / float(fps)
    active_chunk_idx = 0
    num_chunks = len(single_line_chunks)

    # Frame rendering loop: Single static image, single-line subtitles with gold active highlighting + equalizer directly below
    for f_idx in range(total_frames):
        t_sec = f_idx / float(fps)

        # Single static base image
        frame_img = prepared_base.copy()
        draw = ImageDraw.Draw(frame_img)

        # 1. Draw floating music equalizer directly below subtitle
        visualizer.draw_frame(draw, f_idx)

        # 2. Draw gold progress line
        ratio = min(1.0, t_sec / max(1.0, total_audio_sec))
        draw.line([(0, 1025), (int(config.VIDEO_WIDTH * ratio), 1025)], fill=(218, 165, 32), width=4)

        # 3. Locate active single-line subtitle chunk
        while active_chunk_idx < num_chunks - 1 and t_sec >= single_line_chunks[active_chunk_idx + 1]["start"]:
            active_chunk_idx += 1

        curr_c = single_line_chunks[active_chunk_idx] if active_chunk_idx < num_chunks else None
        chunk = None
        if curr_c and (curr_c["start"] <= t_sec <= (curr_c["end"] + 0.15)):
            chunk = curr_c

        # 4. Draw single-line subtitle with real-time active word highlighting in radiant gold
        if chunk:
            for wm in chunk["words"]:
                is_active = (wm["start"] <= t_sec <= wm["end"])
                color = (255, 215, 0) if is_active else (245, 245, 245)

                # Clean drop shadow for high contrast and elegance
                draw.text((wm["x"] + 3, wm["y"] + 3), wm["word"], fill=(0, 0, 0, 240), font=font_quote)
                draw.text((wm["x"] - 1, wm["y"] - 1), wm["word"], fill=(10, 12, 18, 200), font=font_quote)
                draw.text((wm["x"], wm["y"]), wm["word"], fill=color, font=font_quote)

        raw_bgr = np.array(frame_img.convert("RGB"))[:, :, ::-1].tobytes()
        pipe.stdin.write(raw_bgr)

        if (f_idx + 1) % (fps * 30) == 0:
            print(f"  [Video Render] Progress: {f_idx + 1}/{total_frames} frames ({(f_idx+1)/fps:.1f}s / {total_audio_sec:.1f}s)")

    pipe.stdin.close()
    pipe.wait()
    print(f"[VideoComposer] Video rendered successfully: {output_video_path}")
    return output_video_path
