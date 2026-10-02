"""Speech-service factory for manim-voiceover.

Uses ElevenLabs when ``ELEVEN_API_KEY`` is set (env or ``.env``). Otherwise it
falls back to silent placeholder audio timed to the text, so scenes can be
previewed offline without spending API credits. Set ``REQUIRE_ELEVENLABS=1``
(the Makefile does this for ``make final``) to make a missing key an error.
"""

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from manim import logger
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService, initialize_speech_service, path_to_string
from pydub import AudioSegment

load_dotenv(find_dotenv(usecwd=True))

DEFAULT_MODEL = "eleven_multilingual_v2"
WORDS_PER_SECOND = 2.6  # rough narration pace for placeholder audio


class SilentService(SpeechService):
    """Writes silence with roughly the duration the narration would take."""

    def __init__(self, **kwargs: object) -> None:
        initialize_speech_service(self, kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        input_text = remove_bookmarks(text)
        input_data = {"input_text": input_text, "service": "silent", "wps": WORDS_PER_SECOND}

        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = path_to_string(path) if path else self.get_audio_basename(input_data) + ".wav"
        seconds = max(1.0, len(input_text.split()) / WORDS_PER_SECOND)
        AudioSegment.silent(duration=int(seconds * 1000)).export(cache_dir / audio_path, format="wav")
        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}


def speech_service(**kwargs: object) -> SpeechService:
    """Return the configured speech service. Extra kwargs go to the service."""
    if os.environ.get("ELEVEN_API_KEY"):
        from manim_voiceover.services.elevenlabs import ElevenLabsService

        # Whisper transcription is only needed for bookmarks; skip the heavy
        # `transcribe` extra unless a scene asks for it.
        kwargs.setdefault("transcription_model", None)
        return ElevenLabsService(
            voice_name=os.environ.get("ELEVEN_VOICE_NAME") or None,
            voice_id=os.environ.get("ELEVEN_VOICE_ID") or None,
            model=os.environ.get("ELEVEN_MODEL", DEFAULT_MODEL),
            **kwargs,
        )
    if os.environ.get("REQUIRE_ELEVENLABS") == "1":
        raise RuntimeError("ELEVEN_API_KEY is not set (see .env.example); refusing to render with silent audio.")
    logger.warning("ELEVEN_API_KEY not set: using silent placeholder narration.")
    return SilentService(**kwargs)
