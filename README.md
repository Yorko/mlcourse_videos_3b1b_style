# 3b1b-style ML course videos

I am the developer of [mlcourse.ai](mlcourse.ai]), and I've always wanted to test 3b1b-style video creation with [Manim](https://www.manim.community/), kudos to Grant Sanderson ([YouTube](https://www.youtube.com/@3blue1brown)). Here I'm sharing the process I followed with help of Claude Opus 5.5, Gemini 4 Argon, Lyria and a bit of Nano Banana. 

[![Final result](https://img.youtube.com/vi/HAvToyUmyGU/maxresdefault.jpg)](https://www.youtube.com/watch?v= HAvToyUmyGU)

First, I asked Claude to create a plan:

> I want to create an impeccable video on classification and decision trees based on my article https://mlcourse.ai/book/topic03/topic03_decision_trees_kNN.html. I want it to be in the style of 3blue1brown, using his library https://github.com/3b1b/manim  create a plan for me, what do I need to do step by step, I want to use AI assistants as much as possible

Here is the plan: [docs/decision_trees_video_plan.md](docs/decision_trees_video_plan.md). 

Then I basically followed the plan, jumping between Claude and Gemini subagents. It can still be (almost) fully automated but I preferred to follow the plan manually. In a nutshell, the steps are:

 - creating a narrative ([docs/narration_decision_trees.md](docs/narration_decision_trees.md)) and reviewing it with 3 subagents (beginner, ML expert, YouTube editor);
 - creating a style ([docs/STYLE.md](docs/STYLE.md));
 - then a creating storyboard in Manim format ([docs/STORYBOARD.md](docs/STORYBOARD.md));
 - doing a voice clone with ElevenLabs (API key needed);
 - rendering scenes following the storyboard (11 scenes for a 10-minute video in my case);
 - adding a background siundtrack with Lyria Live API (Gemini API key needed);
 - revieweing the scenes and final editing.

Some observations:
 - I started off with an mlcourse.ai [article](https://mlcourse.ai/book/topic03/topic03_decision_trees_kNN.html), it's a good start; otherwise, you need to invest time in some seed images and/or animations;
 - LLM assistance is superb, the bottleneck is actually watching and verifying the video episodes. Subtle issues can still occur;
 - Claude Opus 5.5 is most helpful, Gemini 4 Argon subjectively is on par but atm (Oct 2026) only max thinking level is available, and so it's a bit slow;
 - To make it impeccable, you still need some post-processing with video-editing tools, also it's a good practice to narrate videos by yourself, without AI dubbing (3b1b btw narrates everything himself).  

## Setup

For Mac

```bash
brew install py3cairo sox ffmpeg
uv venv
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

### Background music

`make music` streams one continuous instrumental bed from Lyria RealTime (Gemini API), timed to the rendered
scenes, and writes `media/music/bed.wav` plus `bed.cues.txt` (scene start times). It needs `GEMINI_API_KEY` in `.env`
and the `make final` renders, and it runs in real time (about 10 minutes). Per-scene prompts are in `CUES` in
`scripts/music.py`. Useful flags: `ARGS=--dry-run` prints the timeline, `--gap 1.0` matches pauses you add
between scenes in the edit, and `--quality 480p15` times against previews.

