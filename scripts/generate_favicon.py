"""Generates assets/favicon.png: a gradient rounded-square icon (violet -> cyan,
matching the app's theme) with three ascending bars evoking 'data flow'."""
import os
from PIL import Image, ImageDraw, ImageOps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(BASE_DIR, "assets", "favicon.png")

SIZE = 256
COLOR_START = "#7c3aed"  # violet
COLOR_END = "#06b6d4"    # cyan

def build_gradient(size):
    grad = Image.linear_gradient("L").resize((size * 2, size * 2))
    grad = grad.rotate(45, resample=Image.BICUBIC)
    left = (grad.width - size) // 2
    top = (grad.height - size) // 2
    grad = grad.crop((left, top, left + size, top + size))
    return ImageOps.colorize(grad, black=COLOR_START, white=COLOR_END).convert("RGBA")


def rounded_mask(size, radius):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def draw_bars(img, size):
    draw = ImageDraw.Draw(img, "RGBA")
    bar_w = size * 0.13
    gap = size * 0.08
    heights = [0.30, 0.46, 0.62]
    total_w = bar_w * 3 + gap * 2
    start_x = (size - total_w) / 2
    base_y = size * 0.72

    for i, h_frac in enumerate(heights):
        x0 = start_x + i * (bar_w + gap)
        x1 = x0 + bar_w
        h = size * h_frac
        y0 = base_y - h
        y1 = base_y
        radius = bar_w / 2.2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(255, 255, 255, 235))


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    bg = build_gradient(SIZE)
    mask = rounded_mask(SIZE, radius=int(SIZE * 0.22))

    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(bg, (0, 0), mask)

    draw_bars(canvas, SIZE)

    canvas.save(OUT_PATH)
    print(f"Saved {OUT_PATH} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
