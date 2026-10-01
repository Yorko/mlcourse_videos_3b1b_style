"""Key the outer white out of a hand-supplied ods_mascot.png (scene 1a).

prep_s01a_assets.py cuts the mascot from the banner, which would overwrite a
replacement mascot. This keys whatever ods_mascot.png is there into
ods_mascot_keyed.png and leaves the original untouched. Re-run it after
replacing the mascot:

    uv run python scripts/key_s01a_mascot.py
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prep_s01a_assets as prep  # noqa: E402

# The face outline is open between the ring and the laptop corner, so the
# flood fill would eat the white face. This is prep.SEALS, moved into the
# 258 x 300 mascot crop (left piece is 531 px wide) and rescaled per image.
SEAL_IN_CROP = ((57, 234), (76, 247))
CROP_SIZE = (258, 300)


def main() -> None:
    src = Image.open(prep.IMG_DIR / "ods_mascot.png").convert("RGB")
    sx, sy = src.width / CROP_SIZE[0], src.height / CROP_SIZE[1]
    (x0, y0), (x1, y1) = SEAL_IN_CROP
    prep.SEALS = [((round(x0 * sx), round(y0 * sy)), (round(x1 * sx), round(y1 * sy)))]
    prep.SEAL_WIDTH = max(prep.SEAL_WIDTH, round(6 * sx))
    prep.FRINGE_PX = max(prep.FRINGE_PX, round(2 * sx))

    out = src.convert("RGBA")
    out.putalpha(Image.fromarray(prep.key_outer_white(np.asarray(src))))
    out.save(prep.IMG_DIR / "ods_mascot_keyed.png")
    print(f"ods_mascot_keyed.png  {out.size}  seal={prep.SEALS[0]}")


if __name__ == "__main__":
    main()
