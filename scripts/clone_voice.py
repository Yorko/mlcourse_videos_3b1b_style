"""Clone a voice with ElevenLabs Instant Voice Cloning API and print/save the voice_id."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import mimetypes
import os
from pathlib import Path
import re
import sys

from dotenv import load_dotenv
import requests


API_URL = "https://api.elevenlabs.io/v1/voices/add"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an ElevenLabs Instant Voice Clone from 1-2 minutes of clean audio."
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Path(s) to clean audio sample file(s) (.mp3, .wav, .m4a).",
    )
    parser.add_argument(
        "--name",
        default="My Manim Narrator",
        help="Display name for the cloned voice in ElevenLabs (default: 'My Manim Narrator').",
    )
    parser.add_argument(
        "--description",
        default="Clear educational narrator voice for Manim animations",
        help="Optional description for the cloned voice.",
    )
    parser.add_argument(
        "--remove-background-noise",
        action="store_true",
        help="Ask ElevenLabs to strip background noise from the samples before cloning.",
    )
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Automatically update ELEVEN_VOICE_ID in .env with the newly created voice_id.",
    )
    return parser.parse_args()


def update_dotenv_voice_id(env_path: Path, voice_id: str) -> None:
    """Update or append ELEVEN_VOICE_ID in the .env file."""
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if re.search(r"^ELEVEN_VOICE_ID=.*$", content, flags=re.MULTILINE):
            content = re.sub(
                r"^ELEVEN_VOICE_ID=.*$",
                f"ELEVEN_VOICE_ID={voice_id}",
                content,
                flags=re.MULTILINE,
            )
        else:
            content = content.rstrip("\n") + f"\nELEVEN_VOICE_ID={voice_id}\n"
    else:
        content = f"ELEVEN_VOICE_ID={voice_id}\n"

    env_path.write_text(content, encoding="utf-8")


def clone_voice(
    files: list[Path],
    name: str,
    description: str,
    remove_background_noise: bool = False,
) -> str:
    """Upload audio samples to ElevenLabs /v1/voices/add and return the new voice_id."""
    load_dotenv()
    api_key = os.environ.get("ELEVEN_API_KEY", "").strip()
    if not api_key or api_key == "your_elevenlabs_api_key_here":
        raise RuntimeError(
            "ELEVEN_API_KEY is not set. Add your key to .env before running this script."
        )

    missing = [str(p) for p in files if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Audio sample file(s) not found: {', '.join(missing)}")

    with ExitStack() as stack:
        multipart_files = []
        for path in files:
            mime_type, _ = mimetypes.guess_type(path.name)
            file_obj = stack.enter_context(path.open("rb"))
            multipart_files.append(
                ("files", (path.name, file_obj, mime_type or "audio/mpeg"))
            )

        response = requests.post(
            API_URL,
            headers={"xi-api-key": api_key},
            data={
                "name": name,
                "description": description,
                "remove_background_noise": str(remove_background_noise).lower(),
            },
            files=multipart_files,
            timeout=120,
        )

    if not response.ok:
        raise RuntimeError(
            f"ElevenLabs API error ({response.status_code}): {response.text}"
        )

    payload = response.json()
    voice_id = payload.get("voice_id")
    if not voice_id:
        raise RuntimeError(f"Unexpected API response (missing voice_id): {payload}")

    return str(voice_id)


def main() -> int:
    args = parse_args()
    try:
        voice_id = clone_voice(
            files=args.files,
            name=args.name,
            description=args.description,
            remove_background_noise=args.remove_background_noise,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Cloned Voice Name: {args.name}")
    print(f"Cloned Voice ID:   {voice_id}")

    if args.update_env:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        update_dotenv_voice_id(env_path, voice_id)
        print(f"Updated ELEVEN_VOICE_ID={voice_id} in {env_path}")
    else:
        print(f"\nAdd this to your .env file:\nELEVEN_VOICE_ID={voice_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

