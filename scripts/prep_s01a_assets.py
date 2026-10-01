"""One-off asset prep for the course intro (s01a): bake transparency into the PNGs.

Manim CE can't mask an ImageMobject, and both source images have white backgrounds
that look harsh on the dark frame. This script writes, next to the sources:

  yury_circle.png                          portrait cropped to an anti-aliased circle
  ods_left.png, ods_mascot.png, ods_right.png
                                           banner cut into three pieces, outer white keyed to alpha

Only white connected to the image border is removed, so the white sticker interiors
and the mascot's face survive.

    uv run python scripts/prep_s01a_assets.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


IMG_DIR = Path(__file__).resolve().parent.parent / "media" / "images" / "s01a_intro"

# Portrait: circle center/radius in source pixels (600 x 600). The center sits a little
# above the image center so the face is in the middle of the disc.
PORTRAIT_CENTER = (298, 285)
PORTRAIT_RADIUS = 255
SUPERSAMPLE = 4  # draw the mask larger, then downsample, for a smooth edge

# Banner keying
WHITE_THRESHOLD = 235  # min channel >= this counts as background white
FRINGE_PX = 2  # anti-aliased edge band (px) that gets a soft alpha instead of a hard cut
GAP_MIN_WIDTH = 8  # a run of blank columns at least this wide separates two pieces
# The mascot's outline is open between the end of the pink ring and the laptop's left
# corner, which would let the flood fill eat its white face. These segments (source px,
# barrier only, pixels are untouched) seal such gaps.
SEALS = [((588, 234), (607, 247))]
SEAL_WIDTH = 6


def make_portrait() -> None:
    src = Image.open(IMG_DIR / "yury.jpg").convert("RGB")
    cx, cy = PORTRAIT_CENTER
    r = PORTRAIT_RADIUS
    crop = src.crop((cx - r, cy - r, cx + r, cy + r))

    size = 2 * r
    big = Image.new("L", (size * SUPERSAMPLE, size * SUPERSAMPLE), 0)
    ImageDraw.Draw(big).ellipse((0, 0, size * SUPERSAMPLE - 1, size * SUPERSAMPLE - 1), fill=255)
    mask = big.resize((size, size), Image.LANCZOS)

    out = crop.convert("RGBA")
    out.putalpha(mask)
    out.save(IMG_DIR / "yury_circle.png")
    print(f"yury_circle.png  {out.size}")


def key_outer_white(rgb: np.ndarray) -> np.ndarray:
    """Alpha channel that is 0 on border-connected white and soft along its edge."""
    whiteness = rgb.min(axis=2)
    barrier = Image.new("L", (rgb.shape[1], rgb.shape[0]), 0)
    for a, b in SEALS:
        ImageDraw.Draw(barrier).line([a, b], fill=255, width=SEAL_WIDTH)
    near_white = (whiteness >= WHITE_THRESHOLD) & (np.asarray(barrier) == 0)

    labels, _ = ndimage.label(near_white)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    border = border[border != 0]
    background = np.isin(labels, border)

    # Pixels just outside the background are anti-aliased blends with white:
    # give them alpha proportional to how far they are from white.
    fringe = ndimage.binary_dilation(background, iterations=FRINGE_PX) & ~background
    soft = np.clip((255 - whiteness.astype(float)) / (255 - 160), 0, 1)

    alpha = np.ones(whiteness.shape)
    alpha[background] = 0
    alpha[fringe] = soft[fringe]
    return (alpha * 255).round().astype(np.uint8)


def find_cuts(rgb: np.ndarray) -> list[int]:
    """Midpoints of the interior blank-column gaps that separate the banner pieces."""
    blank = (rgb.min(axis=2) >= WHITE_THRESHOLD).all(axis=0)
    gaps, start = [], None
    for x, b in enumerate(blank):
        if b and start is None:
            start = x
        elif not b and start is not None:
            gaps.append((start, x - 1))
            start = None
    w = rgb.shape[1]
    interior = [(a, b) for a, b in gaps if a > 0 and b < w - 1 and b - a + 1 >= GAP_MIN_WIDTH]
    if len(interior) != 2:
        raise SystemExit(f"expected 2 interior gaps in the banner, found {interior}")
    return [(a + b) // 2 for a, b in interior]


def make_banner() -> None:
    src = Image.open(IMG_DIR / "ods_stickers.jpg").convert("RGB")
    rgb = np.asarray(src)
    out = src.convert("RGBA")
    out.putalpha(Image.fromarray(key_outer_white(rgb)))

    c1, c2 = find_cuts(rgb)
    w, h = out.size
    for name, (x0, x1) in {"left": (0, c1), "mascot": (c1, c2), "right": (c2, w)}.items():
        piece = out.crop((x0, 0, x1, h))
        piece.save(IMG_DIR / f"ods_{name}.png")
        print(f"ods_{name}.png  x={x0}-{x1}  {piece.size}")


if __name__ == "__main__":
    make_portrait()
    make_banner()
