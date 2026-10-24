import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import config

def draw_heavy_3d_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, center_x: int, y: int, fill_color: tuple, stroke_color: tuple = (10, 12, 18), stroke_width: int = 8):
    b = draw.textbbox((0, 0), text, font=font)
    tw = b[2] - b[0]
    tx = center_x - (tw // 2)

    shadow_offset = stroke_width + 4
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((tx + dx + 4, y + dy + shadow_offset), text, fill=(0, 0, 0, 220), font=font)

    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((tx + dx, y + dy), text, fill=stroke_color, font=font)

    draw.text((tx, y), text, fill=fill_color, font=font)

def generate_thumbnail(image_path: str, title_1: str, title_2: str, hook: str, output_path: str, ep_number: int = 1) -> str:
    base = Image.open(image_path).convert("RGBA")
    if base.size != (config.VIDEO_WIDTH, config.VIDEO_HEIGHT):
        base = base.resize((config.VIDEO_WIDTH, config.VIDEO_HEIGHT), Image.Resampling.LANCZOS)

    # Apply rich contrast gradient to the right side for bold thumbnail typography
    overlay = Image.new("RGBA", (config.VIDEO_WIDTH, config.VIDEO_HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for x in range(750, config.VIDEO_WIDTH):
        alpha = int(min(180, (x - 750) / (config.VIDEO_WIDTH - 750) * 180))
        ov_draw.line([(x, 0), (x, config.VIDEO_HEIGHT)], fill=(6, 8, 14, alpha))
    base = Image.alpha_composite(base, overlay)

    draw = ImageDraw.Draw(base)
    font_path = config.FONT_PATH if os.path.exists(config.FONT_PATH) else config.FALLBACK_FONT_PATH
    badge_font = ImageFont.truetype(font_path, 28)

    # Episode Badge Pill
    badge_text = f"• {config.CHANNEL_NAME} • EPISODE {ep_number:02d} •"
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bbox[2] - bbox[0]
    bh = bbox[3] - bbox[1]
    bx = config.SUBTITLE_CENTER_X - (bw // 2)
    by = 190

    draw.rounded_rectangle(
        [bx - 26, by - 10, bx + bw + 26, by + bh + 12],
        radius=16,
        fill=(218, 165, 32, 245),
        outline=(255, 235, 175, 230),
        width=2
    )
    draw.text((bx, by), badge_text, fill=(12, 14, 20), font=badge_font)

    # Title Lines (Extruded 3D Gold & White)
    font_t1 = ImageFont.truetype(font_path, 76)
    draw_heavy_3d_text(draw, title_1.upper(), font_t1, config.SUBTITLE_CENTER_X, 290, (255, 255, 255), stroke_width=8)

    font_t2 = ImageFont.truetype(font_path, 76)
    draw_heavy_3d_text(draw, title_2.upper(), font_t2, config.SUBTITLE_CENTER_X, 400, (255, 215, 0), stroke_width=8)

    # Subtitle Hook Pill
    if hook:
        hook_font = ImageFont.truetype(font_path, 34)
        h_bbox = draw.textbbox((0, 0), hook, font=hook_font)
        hw = h_bbox[2] - h_bbox[0]
        hh = h_bbox[3] - h_bbox[1]
        hx = config.SUBTITLE_CENTER_X - (hw // 2)
        hy = 530

        draw.rounded_rectangle(
            [hx - 22, hy - 10, hx + hw + 22, hy + hh + 12],
            radius=14,
            fill=(14, 16, 26, 235),
            outline=(218, 165, 32, 200),
            width=2
        )
        draw.text((hx, hy), hook, fill=(245, 240, 225), font=hook_font)

    base.convert("RGB").save(output_path, quality=95)
    print(f"[Thumbnail] Created thumbnail: {output_path}")
    return output_path
