#!/usr/bin/env python3
"""Compose the gta6-meme-x-01 meme (1200x675) with PIL.

Inputs (all in assets/ next to this script):
  scene.webp        - fresh flat-cartoon graveyard scene (2048x1152)
  splash-dark.png   - make.fun dark press splash, downloaded fresh from
                      https://make.fun/press/ (1125x2436)
  Anton-Regular.ttf - Anton font, fetched from google/fonts on GitHub
Output:
  ../meme.jpg       - the final meme (quality 90)
  ghost.png         - the extracted make.fun ghost (intermediate, kept for
                      inspection)

Ghost extraction: the splash holds the ghost on a magenta disc. We mask out
the magenta, then flood-fill the connected component from a seed inside the
white body, staying inside the disc's circle so the fill can never leak into
the dark page background through the disc's black rim. That drops the
magenta disc, the star-badge coin and the rim, and keeps only the ghost
body, its black outline and its sparkle eyes.
"""

import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
W, H = 1200, 675

MAGENTA = (196, 28, 131)          # make.fun splash magenta
DISC_CX, DISC_CY, DISC_R = 564, 1218, 172   # disc centre/radius in splash px


def is_magenta(px):
    r, g, b = px
    return r > 150 and g < 80 and 80 < b < 200


def extract_ghost():
    splash = Image.open(ASSETS / "splash-dark.png").convert("RGB")
    # Tight crop around the disc, plus a margin for the flood fill.
    x0, y0 = DISC_CX - DISC_R - 4, DISC_CY - DISC_R - 4
    x1, y1 = DISC_CX + DISC_R + 4, DISC_CY + DISC_R + 4
    crop = splash.crop((x0, y0, x1, y1))
    cw, ch = crop.size
    px = crop.load()

    # Seed: first white pixel near the middle of the body.
    seed = None
    for yy in range(ch // 2 - 40, ch // 2 + 60):
        for xx in range(cw // 2 - 60, cw // 2 + 60):
            r, g, b = px[xx, yy]
            if r > 240 and g > 240 and b > 240:
                seed = (xx, yy)
                break
        if seed:
            break
    assert seed, "no white seed pixel found inside the ghost body"

    # Flood fill over non-magenta pixels, confined to the disc circle.
    seen = bytearray(cw * ch)
    q = deque([seed])
    seen[seed[1] * cw + seed[0]] = 1
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not (0 <= nx < cw and 0 <= ny < ch):
                continue
            if seen[ny * cw + nx]:
                continue
            dx, dy = nx + x0 - DISC_CX, ny + y0 - DISC_CY
            if dx * dx + dy * dy > DISC_R * DISC_R:
                continue
            if is_magenta(px[nx, ny]):
                continue
            seen[ny * cw + nx] = 1
            q.append((nx, ny))

    # Build the RGBA ghost from the filled component.
    ghost = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    gp = ghost.load()
    for yy in range(ch):
        for xx in range(cw):
            if seen[yy * cw + xx]:
                gp[xx, yy] = (*px[xx, yy], 255)
    bbox = ghost.getbbox()
    ghost = ghost.crop(bbox)
    ghost.save(ASSETS / "ghost.png")
    return ghost


def text_with_outline(draw, xy, text, font, fill, outline, width):
    x, y = xy
    draw.text((x, y), text, font=font, fill=fill, anchor="ma",
              stroke_width=width, stroke_fill=outline)


def draw_money_bag(draw, cx, cy, s):
    """A green money bag with a '$', centred at (cx, cy), size s."""
    green, dark = (34, 139, 34), (16, 90, 16)
    # Sack body.
    draw.ellipse([cx - 0.55 * s, cy - 0.35 * s, cx + 0.55 * s, cy + 0.55 * s],
                 fill=green, outline=dark, width=max(2, int(s * 0.06)))
    # Tied neck.
    draw.polygon([(cx - 0.28 * s, cy - 0.32 * s), (cx + 0.28 * s, cy - 0.32 * s),
                  (cx + 0.12 * s, cy - 0.62 * s), (cx - 0.12 * s, cy - 0.62 * s)],
                 fill=green, outline=dark)
    draw.line([cx - 0.30 * s, cy - 0.34 * s, cx + 0.30 * s, cy - 0.34 * s],
              fill=dark, width=max(2, int(s * 0.06)))
    # Dollar sign.
    font = ImageFont.truetype(str(ASSETS / "DejaVuSans-Bold.ttf"), int(s * 0.55))
    draw.text((cx, cy + 0.08 * s), "$", font=font, fill="white", anchor="mm",
              stroke_width=max(1, int(s * 0.04)), stroke_fill=dark)


def draw_coin(draw, cx, cy, r):
    gold, dark = (255, 200, 40), (176, 120, 0)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gold, outline=dark,
                 width=max(2, int(r * 0.14)))
    font = ImageFont.truetype(str(ASSETS / "DejaVuSans-Bold.ttf"), int(r * 1.1))
    draw.text((cx, cy), "$", font=font, fill=dark, anchor="mm")


def main():
    scene = Image.open(ASSETS / "scene.webp").convert("RGB").resize((W, H), Image.LANCZOS)
    meme = scene.copy()
    draw = ImageDraw.Draw(meme, "RGBA")

    anton = ImageFont.truetype(str(ASSETS / "Anton-Regular.ttf"), 64)
    anton_small = ImageFont.truetype(str(ASSETS / "Anton-Regular.ttf"), 34)

    # --- Top + bottom captions (Anton, white with black outline). ---
    text_with_outline(draw, (W // 2, 16), "WE GOT PAID BEFORE GTA 6",
                      anton, "white", "black", 7)
    text_with_outline(draw, (W // 2, H - 56),
                      "my AI agent earned on make.fun while we waited 13 years",
                      anton_small, "white", "black", 5)

    # --- Tombstone inscription (DejaVu Sans Bold, dark grey, centred x=380). ---
    dejavu = str(ASSETS / "DejaVuSans-Bold.ttf")
    lines = ["WE GOT ___", "BEFORE GTA 6", "2013 \u2013 2026"]
    size = 26
    while size > 10:
        font = ImageFont.truetype(dejavu, size)
        if max(draw.textlength(t, font=font) for t in lines) <= 130:
            break
        size -= 1
    font = ImageFont.truetype(dejavu, size)
    y = 268
    for line in lines:
        draw.text((380, y), line, font=font, fill="#3c3c46", anchor="ma")
        y += int(size * 1.35)

    # --- Ghost on the right, standing on the grass, holding a money bag. ---
    ghost = extract_ghost()
    gh = 300
    gw = int(ghost.width * gh / ghost.height)
    ghost = ghost.resize((gw, gh), Image.LANCZOS)
    gx, gy = 790, 600 - gh  # feet on the grass, fully inside the frame
    meme.paste(ghost, (gx, gy), ghost)

    # Money bag in front of the ghost's hand, coins at its feet.
    draw = ImageDraw.Draw(meme, "RGBA")
    draw_money_bag(draw, gx + int(gw * 0.78), gy + int(gh * 0.62), 95)
    for cx, cy, r in ((gx + 8, 592, 16), (gx + 46, 600, 18), (gx + 86, 592, 15),
                      (gx + 120, 600, 17)):
        draw_coin(draw, cx, cy, r)

    meme.save(HERE / "meme.jpg", quality=90)
    print(f"wrote {HERE / 'meme.jpg'} ({W}x{H}, ghost {gw}x{gh} at {gx},{gy})")


if __name__ == "__main__":
    main()
