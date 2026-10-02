# 3b1b-style ML course: project rules

Videos are built with Manim Community and manim-voiceover, managed with uv. See `README.md` for setup.
The current video is decision trees. Its plan, beats and script are in `docs/`
(`decision_trees_video_plan.md`, `beat_sheet_decision_trees.md`, `narration_decision_trees.md`). Narration style is in `docs/STYLE.md`.

## Rules

- **Use the Manim Community v0.19+ API only** (`from manim import ...`). Never use manimgl or 3b1b's `manimlib`.
  Their APIs differ (`ShowCreation`, `self.frame`, `OldTex`, etc.), so don't copy code from 3b1b's own repo.
- **Import colors from `scripts/style.py`** (`from style import *`), and do the same for fonts, sizes and timings.
  Use the semantic names (`PRIMARY`, `SECONDARY`, `POSITIVE`, `NEGATIVE`, `TEXT`, `GRID`, ...).
  Don't use raw hex values or Manim color constants in scenes.
  If you need a new color or constant, add it to `scripts/style.py` and its `__all__`.
- **Read numbers from `data/*.json`. Never hard-code them.** This covers entropies, information gains, thresholds,
  point coordinates, tree splits, leaf rectangles, accuracies and MSEs.
  If a scene needs a number the JSON doesn't have, add it to `data/compute.ipynb`, run `make data`, and read it from there.
  Don't compute it inside the scene.
  The ball colors in `balls.json` were read off the article's images, so they are the ground truth and shouldn't be changed.
- **Every scene uses `VoiceoverScene`.** Call `self.set_speech_service(speech_service())` from `scripts/voice.py`, and wrap the
  animations in `with self.voiceover(text=...) as tracker:` so their timing follows `tracker.duration`.
  Narration text comes from `docs/narration_decision_trees.md`.
- **After writing or changing a scene, check it visually:**
  1. Render at low quality: `make preview FILE=scenes/<file>.py SCENE=<Scene>`.
  2. Extract frames at key timestamps (each beat, and just after every voiceover block starts and ends):
     ```bash
     ffmpeg -v error -ss <t> -i media/videos/<file>/480p15/<Scene>.mp4 -frames:v 1 /tmp/frames/<Scene>_<t>.png
     ```
     `ffprobe -v error -show_entries format=duration -of csv=p=0 <mp4>` gives the length.
  3. Open the frames with the Read tool. Look for overlapping mobjects, text that runs off-screen or past `EDGE_BUFF`,
     unreadable labels, and numbers that don't match the JSON.
  4. Fix and re-render until the frames are clean.

## Layout

```
scripts/style.py      palette, fonts, timing (single source of truth)
scripts/voice.py      speech_service(): ElevenLabs, or silent placeholder audio without a key
                      (the Makefile puts scripts/ on PYTHONPATH, so scenes keep `from style import *`)
scenes/               one file per video; test_scene.py is the smoke test / template
data/compute.ipynb    computes every on-screen number -> data/*.json  (make data)
docs/                 video plan, beat sheet, narration, style guide
```

## Commands

```bash
make preview FILE=scenes/foo.py SCENE=Foo   # 480p15, silent audio if there's no ELEVEN_API_KEY
make final   FILE=scenes/foo.py SCENE=Foo   # 2160p60, requires ELEVEN_API_KEY
make data                                   # re-run data/compute.ipynb (uv group "data")
```

Ignore the pydub `SyntaxWarning`s and the "SoX could not be found!" warning (see README).
