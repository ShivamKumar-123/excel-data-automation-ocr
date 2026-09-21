"""Generates assets/hero_illustration.png: overlapping XLSX/CSV/PDF file
cards flowing into a checklist card with a mini bar chart, matching the
DataFlow Pro dashboard mockup's hero graphic."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(BASE_DIR, "assets", "hero_illustration.png")

W, H = 900, 520
SCALE = 2  # render at 2x then downsample for smoother edges
CW, CH = W * SCALE, H * SCALE


def load_font(bold=False, italic=False, size=20):
    candidates = []
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = os.path.join(windir, "Fonts")
    if bold and italic:
        candidates += ["arialbi.ttf"]
    elif bold:
        candidates += ["arialbd.ttf", "segoeuib.ttf"]
    elif italic:
        candidates += ["ariali.ttf", "segoeuii.ttf"]
    else:
        candidates += ["arial.ttf", "segoeui.ttf"]

    for name in candidates:
        path = os.path.join(fonts_dir, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rounded_card(size, radius, fill):
    card = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return card


def paste_rotated(base, card, center, angle, shadow=True):
    if shadow:
        sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(
            [0, 0, card.size[0] - 1, card.size[1] - 1],
            radius=int(card.size[0] * 0.12), fill=(15, 23, 42, 60)
        )
        sh = sh.rotate(angle, expand=True, resample=Image.BICUBIC)
        sx = center[0] - sh.size[0] // 2 + int(6 * SCALE)
        sy = center[1] - sh.size[1] // 2 + int(10 * SCALE)
        base.alpha_composite(sh, (sx, sy))

    rotated = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    x = center[0] - rotated.size[0] // 2
    y = center[1] - rotated.size[1] // 2
    base.alpha_composite(rotated, (x, y))


def main():
    canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))

    # ---- File cards (XLSX, CSV, PDF) ----
    card_w, card_h = int(150 * SCALE), int(190 * SCALE)
    font_label_bold = load_font(bold=True, size=int(22 * SCALE))

    file_specs = [
        {"label": "PDF", "color": (100, 116, 139, 255), "angle": 8, "offset": (int(60 * SCALE), int(60 * SCALE))},
        {"label": "CSV", "color": (6, 182, 212, 255), "angle": -6, "offset": (int(95 * SCALE), int(20 * SCALE))},
        {"label": "XLSX", "color": (16, 185, 129, 255), "angle": 3, "offset": (int(130 * SCALE), int(-15 * SCALE))},
    ]

    base_center = (int(190 * SCALE), int(240 * SCALE))
    for spec in file_specs:
        card = rounded_card((card_w, card_h), int(18 * SCALE), spec["color"])
        d = ImageDraw.Draw(card)
        # fold corner
        fold = int(34 * SCALE)
        d.polygon(
            [(card_w - fold, 0), (card_w, fold), (card_w - fold, fold)],
            fill=(255, 255, 255, 70),
        )
        bbox = d.textbbox((0, 0), spec["label"], font=font_label_bold)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((card_w - tw) / 2, card_h - th - int(24 * SCALE)), spec["label"],
               font=font_label_bold, fill=(255, 255, 255, 255))
        center = (base_center[0] + spec["offset"][0], base_center[1] + spec["offset"][1])
        paste_rotated(canvas, card, center, spec["angle"])

    # ---- Arrow ----
    arrow_font = load_font(bold=True, size=int(46 * SCALE))
    d = ImageDraw.Draw(canvas)
    arrow_x = int(400 * SCALE)
    arrow_y = int(230 * SCALE)
    d.line([(arrow_x, arrow_y), (arrow_x + int(90 * SCALE), arrow_y)], fill=(37, 99, 235, 255), width=int(5 * SCALE))
    d.polygon([
        (arrow_x + int(90 * SCALE), arrow_y - int(16 * SCALE)),
        (arrow_x + int(120 * SCALE), arrow_y),
        (arrow_x + int(90 * SCALE), arrow_y + int(16 * SCALE)),
    ], fill=(37, 99, 235, 255))

    # ---- Checklist card ----
    check_w, check_h = int(340 * SCALE), int(300 * SCALE)
    check_card = rounded_card((check_w, check_h), int(22 * SCALE), (255, 255, 255, 255))
    cd = ImageDraw.Draw(check_card)
    cd.rounded_rectangle([0, 0, check_w - 1, check_h - 1], radius=int(22 * SCALE), outline=(226, 232, 240, 255), width=int(2 * SCALE))

    items = ["Clean Data", "Validated", "Duplicates Removed", "Ready to Export"]
    font_item = load_font(bold=True, size=int(19 * SCALE))
    row_h = int(58 * SCALE)
    pad = int(28 * SCALE)
    for i, text in enumerate(items):
        cy = pad + i * row_h + int(20 * SCALE)
        r = int(16 * SCALE)
        cd.ellipse([pad, cy - r, pad + 2 * r, cy + r], fill=(16, 185, 129, 255))
        # checkmark
        cd.line([
            (pad + r * 0.5, cy),
            (pad + r * 0.9, cy + r * 0.4),
            (pad + r * 1.5, cy - r * 0.5),
        ], fill=(255, 255, 255, 255), width=int(3 * SCALE), joint="curve")
        cd.text((pad + 2 * r + int(14 * SCALE), cy - int(12 * SCALE)), text,
                 font=font_item, fill=(15, 23, 42, 255))

    # mini bar chart bottom-right of checklist card
    bar_colors = (37, 99, 235, 255)
    bar_w = int(14 * SCALE)
    bar_gap = int(10 * SCALE)
    bar_base_y = check_h - int(28 * SCALE)
    heights = [int(30 * SCALE), int(46 * SCALE), int(62 * SCALE)]
    start_x = check_w - int(110 * SCALE)
    for i, h in enumerate(heights):
        x0 = start_x + i * (bar_w + bar_gap)
        cd.rounded_rectangle([x0, bar_base_y - h, x0 + bar_w, bar_base_y], radius=int(5 * SCALE), fill=bar_colors)

    canvas.alpha_composite(check_card, (int(500 * SCALE), int(70 * SCALE)))

    # shadow under checklist card (draw before? simplify: skip separate shadow layer for card, acceptable)

    # ---- Caption ----
    caption_font = load_font(italic=True, size=int(22 * SCALE))
    d = ImageDraw.Draw(canvas)
    d.multiline_text(
        (int(560 * SCALE), int(400 * SCALE)),
        "Cleaner Data,\nBetter Decisions",
        font=caption_font, fill=(37, 99, 235, 255), spacing=int(10 * SCALE)
    )

    canvas = canvas.resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    canvas.save(OUT_PATH)
    print(f"Saved {OUT_PATH} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
