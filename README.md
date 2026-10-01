# 3b1b-style ML course

Manim Community + manim-voiceover (ElevenLabs), managed with uv.

The planI'm following: [docs/decision_trees_video_plan.md](docs/decision_trees_video_plan.md)

```
style.py        palette, fonts, timing — `from style import *` in every scene
voice.py        speech_service(): ElevenLabs if ELEVEN_API_KEY is set, else silent placeholder audio
scenes/         one file per video; test_scene.py is the smoke test
Makefile        preview / final targets
```

## Setup

This Mac runs Santa in Lockdown mode, which blocks locally compiled binaries, so
`pycairo` can't be built from source. It comes from Homebrew instead and the venv
sees it via `--system-site-packages` (`pyproject.toml` tells uv to skip it).

```bash
brew install py3cairo sox ffmpeg
uv venv --python /opt/homebrew/bin/python3.14 --system-site-packages
uv sync
cp .env.example .env   # add ELEVEN_API_KEY (optional for previews)
```

## Check that it works

1. **Imports**: should print the Homebrew cairo path and the Manim version:

   ```bash
   uv run python -c "import cairo, manim, manim_voiceover; print(cairo.__file__, manim.__version__)"
   ```
2. **Preview render** (silent audio if there's no key):

   ```bash
   make preview
   ```
   Expect `media/videos/test_scene/480p15/TestScene.mp4` plus a `.srt`.
3. **Output has video + audio**:
   
   ```bash
   ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate \
     -of compact media/videos/test_scene/480p15/TestScene.mp4
   ```
4. **ElevenLabs** (needs `ELEVEN_API_KEY` in `.env`): run `make preview` again. The log
   should no longer say "using silent placeholder narration", and the video should have
   a voice. Generated audio is cached in `media/voiceovers/`.
5. **Final render**:
   
   ```bash
   make final   # 2160p60 in media/videos/test_scene/2160p60/
   ```
   This fails on purpose if `ELEVEN_API_KEY` isn't set, so a final video can't go out silent.

## Usage

```bash
make preview FILE=scenes/foo.py SCENE=Foo   # -ql
make final   FILE=scenes/foo.py SCENE=Foo   # -qk --fps 60
make preview ARGS=-p                        # extra manim flags (-p opens the result)
make clean                                  # delete media/
```

Omit `SCENE` to render every scene in the file. Optional `.env` settings:
`ELEVEN_VOICE_NAME` / `ELEVEN_VOICE_ID` and `ELEVEN_MODEL` (default `eleven_multilingual_v2`).

## Known issues

- pydub prints harmless `SyntaxWarning`s on Python 3.14.
- "SoX could not be found!" appears because Santa blocks Homebrew's ad-hoc-signed `sox`.
  It's harmless unless you pass `global_speed` (other than 1.0) to `speech_service()`, the only
  place manim-voiceover uses SoX. If you need it, ask IT to allowlist `/opt/homebrew/Cellar/sox/*/bin/sox`.
