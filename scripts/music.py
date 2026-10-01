"""Generate the background music bed for the whole video with Lyria RealTime.

Reads each scene's length from its rendered mp4, streams one continuous track
from Lyria RealTime (Gemini API), and crossfades the prompt at every scene
boundary. Writes media/music/bed.wav plus a cue sheet with scene start times,
ready to drop into iMovie's music well.

    make music                       # needs GEMINI_API_KEY in .env, renders first
    make music ARGS=--dry-run        # print the timeline, no API call
    make music ARGS="--quality 480p15 --gap 1.0"

Generation runs in real time: a 10-minute bed takes about 10 minutes.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from dotenv import find_dotenv, load_dotenv

ROOT = Path(__file__).resolve().parent.parent
VIDEOS = ROOT / "media" / "videos"
OUT_DIR = ROOT / "media" / "music"

MODEL = "models/lyria-realtime-exp"
SAMPLE_RATE = 48_000
CHANNELS = 2
BYTES_PER_SEC = SAMPLE_RATE * CHANNELS * 2  # 16-bit PCM

# Shared across the whole video so sections feel like one piece.
BASE_PROMPT = "calm felt piano, soft ambient pads, instrumental background music for an educational video, minimal"
BASE_WEIGHT = 1.0
SECTION_WEIGHT = 0.8


@dataclass
class Cue:
    scene_dir: str  # media/videos/<scene_dir>/
    scene: str  # mp4 name
    prompt: str  # added on top of BASE_PROMPT
    density: float
    brightness: float


# Video order. Prompts drift gradually; keep them sparse so they sit under the voice.
CUES = [
    Cue("s01_cold_open", "ColdOpen", "curious, sparse, light plucked strings", 0.25, 0.45),
    Cue("s01a_intro", "CourseIntro", "curious, sparse, light plucked strings", 0.25, 0.5),
    Cue("s02_twenty_questions", "TwentyQuestions", "playful, curious, gentle pizzicato", 0.3, 0.5),
    Cue("s03_entropy", "Entropy", "thoughtful, steady soft pulse, warm pads", 0.3, 0.4),
    Cue("s04_information_gain", "InformationGain", "thoughtful, steady soft pulse, warm pads", 0.3, 0.45),
    Cue("s05_growing_tree", "GrowingTree", "building, gentle arpeggios, hopeful", 0.4, 0.5),
    Cue("s06_numeric_gini", "NumericGini", "focused, gentle arpeggios", 0.35, 0.5),
    Cue("s07_trees_2d", "Trees2D", "building, gentle arpeggios, hopeful, slightly brighter", 0.4, 0.55),
    Cue("s08_overfitting", "Overfitting", "slightly tense, minor key, uneasy", 0.35, 0.35),
    Cue("s09_regression", "RegressionTrees", "resolving, warm, calm", 0.3, 0.45),
    Cue("s10_wrapup", "WrapUp", "resolved, warm, major key, reflective ending", 0.25, 0.45),
]


def scene_duration(cue: Cue, quality: str) -> float:
    mp4 = VIDEOS / cue.scene_dir / quality / f"{cue.scene}.mp4"
    if not mp4.exists():
        sys.exit(f"missing render: {mp4.relative_to(ROOT)} (render it first, or pass --quality)")
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout)


def build_timeline(quality: str, gap: float) -> list[tuple[float, Cue]]:
    """(start time, cue, duration) per scene, in seconds."""
    t, timeline = 0.0, []
    for cue in CUES:
        timeline.append((t, cue, scene_duration(cue, quality)))
        t += timeline[-1][2] + gap
    return timeline


def section_weights(t: float, timeline, xfade: float) -> dict[str, float]:
    """Section prompt weights at time t, crossfading over `xfade` s centred on each boundary."""
    weights: dict[str, float] = {}
    for i, (start, cue, _) in enumerate(timeline):
        fade_in = 1.0 if i == 0 else np.clip((t - (start - xfade / 2)) / xfade, 0.0, 1.0)
        nxt = timeline[i + 1][0] if i + 1 < len(timeline) else None
        fade_out = 1.0 if nxt is None else np.clip(((nxt + xfade / 2) - t) / xfade, 0.0, 1.0)
        weights[cue.prompt] = weights.get(cue.prompt, 0.0) + float(min(fade_in, fade_out)) * SECTION_WEIGHT
    # 0.1 steps mean fewer updates; Lyria rejects zero weights, so drop those prompts.
    weights = {text: round(w, 1) for text, w in weights.items()}
    return {text: w for text, w in weights.items() if w > 0}


def current_cue(t: float, timeline) -> Cue:
    return [cue for start, cue, _ in timeline if start <= t][-1]


def print_timeline(timeline, total: float) -> None:
    for start, cue, dur in timeline:
        print(f"{start:7.1f}s  {dur:6.1f}s  {cue.scene:<16} {cue.prompt}")
    print(f"{total:7.1f}s  total ({total / 60:.1f} min)")


def write_cue_sheet(path: Path, timeline) -> None:
    lines = [f"{int(s // 60)}:{s % 60:04.1f}  {cue.scene}" for s, cue, _ in timeline]
    path.write_text("\n".join(lines) + "\n")


def write_wav(path: Path, pcm: bytes, total: float, fade_in: float, fade_out: float) -> None:
    audio = np.frombuffer(pcm, dtype="<i2")[: int(total * SAMPLE_RATE) * CHANNELS].reshape(-1, CHANNELS)
    audio = audio.astype(np.float32)
    n_in, n_out = min(len(audio), int(fade_in * SAMPLE_RATE)), min(len(audio), int(fade_out * SAMPLE_RATE))
    audio[:n_in] *= np.linspace(0, 1, n_in)[:, None]
    if n_out:
        audio[-n_out:] *= np.linspace(1, 0, n_out)[:, None]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(CHANNELS)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(audio.astype("<i2").tobytes())


async def generate(args, timeline, total: float, pcm: bytearray) -> None:
    """Stream into `pcm` until it holds `total` seconds; keeps what arrived if the connection drops."""
    from google import genai
    from google.genai import types

    client = genai.Client(http_options={"api_version": "v1beta"})
    done = asyncio.Event()

    def config(cue: Cue):
        # Lyria resets any field left out, so always send the full config.
        return types.LiveMusicGenerationConfig(
            bpm=args.bpm,
            scale=getattr(types.Scale, args.scale),
            seed=args.seed,
            guidance=args.guidance,
            temperature=args.temperature,
            density=cue.density,
            brightness=cue.brightness,
        )

    def prompts(weights: dict[str, float]):
        return [types.WeightedPrompt(text=BASE_PROMPT, weight=BASE_WEIGHT)] + [
            types.WeightedPrompt(text=text, weight=w) for text, w in weights.items()
        ]

    async def receive(session):
        while not done.is_set():
            async for message in session.receive():
                if message.filtered_prompt:
                    print(f"\nprompt filtered: {message.filtered_prompt}", file=sys.stderr)
                if message.server_content and message.server_content.audio_chunks:
                    for chunk in message.server_content.audio_chunks:
                        pcm.extend(chunk.data)
                if len(pcm) >= total * BYTES_PER_SEC:
                    done.set()
                    return

    async with client.aio.live.music.connect(model=MODEL) as session:
        cue = timeline[0][1]
        weights = section_weights(0.0, timeline, args.xfade)
        await session.set_weighted_prompts(prompts=prompts(weights))
        await session.set_music_generation_config(config=config(cue))
        await session.play()
        receiver = asyncio.create_task(receive(session))
        try:
            while not done.is_set():
                if receiver.done():
                    receiver.result()  # re-raise a dropped connection
                    break
                # Prompt changes reach the audio with some delay, so steer slightly ahead.
                t = len(pcm) / BYTES_PER_SEC + args.lead
                new_weights, new_cue = section_weights(t, timeline, args.xfade), current_cue(t, timeline)
                if new_weights != weights:
                    weights = new_weights
                    await session.set_weighted_prompts(prompts=prompts(weights))
                if new_cue is not cue:
                    cue = new_cue
                    await session.set_music_generation_config(config=config(cue))
                print(f"\r{len(pcm) / BYTES_PER_SEC:6.1f} / {total:.1f}s  {cue.scene:<16}", end="", flush=True)
                await asyncio.sleep(0.25)
        finally:
            done.set()
            receiver.cancel()
            print()
            await session.stop()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--quality", default="2160p60", help="render folder to time against (default 2160p60)")
    p.add_argument("--gap", type=float, default=0.0, help="seconds of pause you add between scenes in the edit")
    p.add_argument("--tail", type=float, default=6.0, help="extra seconds after the last scene, faded out")
    p.add_argument("--xfade", type=float, default=8.0, help="prompt crossfade length at each boundary (s)")
    p.add_argument("--lead", type=float, default=2.0, help="steer prompts this many seconds ahead of the audio")
    p.add_argument("--bpm", type=int, default=80)
    p.add_argument("--scale", default="SCALE_UNSPECIFIED", help="types.Scale name, e.g. C_MAJOR_A_MINOR")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--guidance", type=float, default=3.0, help="lower = smoother transitions (0-6)")
    p.add_argument("--temperature", type=float, default=1.1)
    p.add_argument("--out", type=Path, default=OUT_DIR / "bed.wav")
    p.add_argument("--dry-run", action="store_true", help="print the timeline and exit")
    args = p.parse_args()

    timeline = build_timeline(args.quality, args.gap)
    total = timeline[-1][0] + timeline[-1][2] + args.tail
    print_timeline(timeline, total)
    if args.dry_run:
        return

    load_dotenv(find_dotenv(usecwd=True))
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("GEMINI_API_KEY is not set (see .env.example)")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pcm = bytearray()
    try:
        asyncio.run(generate(args, timeline, total, pcm))
    finally:
        if pcm:
            write_wav(args.out, bytes(pcm), total, fade_in=2.0, fade_out=args.tail)
            write_cue_sheet(args.out.with_suffix(".cues.txt"), timeline)
            got = len(pcm) / BYTES_PER_SEC
            print(f"wrote {args.out.relative_to(ROOT)} ({min(got, total):.1f}s of {total:.1f}s)")


if __name__ == "__main__":
    main()
