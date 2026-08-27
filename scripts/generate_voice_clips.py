#!/usr/bin/env python3
"""Generate narration clips for the demo video.

This script uses the OpenAI text-to-speech API to create one audio file per
scene. It is designed for short, separate narration clips that can be dropped
into CapCut, DaVinci Resolve, or another editor.

Requirements:
  pip install openai
  export OPENAI_API_KEY="..."

Input format:
  JSON file with a list of objects:

  [
    {"id": "01", "text": "Space biology evidence is scattered across studies."},
    {"id": "02", "text": "This application keeps the boundary tight..."}
  ]

Example usage:
  python scripts/generate_voice_clips.py \
    --input docs/final/voiceover_scenes.json \
    --output-dir docs/final/voice_clips \
    --voice marin

The default voice and instructions are tuned for a calm, soft, male-leaning
documentary tone.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from openai import OpenAI


DEFAULT_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "marin"
DEFAULT_INSTRUCTIONS = (
    "Speak in a calm, soft, warm male-leaning documentary voice. "
    "Keep the delivery measured, clear, and understated. "
    "Avoid sounding excited, theatrical, or salesy."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to a JSON file containing narration scenes.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where MP3 files will be written.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"TTS model to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"Built-in voice to use (default: {DEFAULT_VOICE}).",
    )
    parser.add_argument(
        "--instructions",
        default=DEFAULT_INSTRUCTIONS,
        help="Voice style instructions passed to the TTS API.",
    )
    parser.add_argument(
        "--format",
        default="mp3",
        choices=["mp3", "opus", "aac", "flac", "wav", "pcm"],
        help="Output audio format (default: mp3).",
    )
    return parser.parse_args()


def load_scenes(path: Path) -> list[dict[str, str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Input JSON must be a list of scene objects.")

    scenes: list[dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Scene {index} must be an object.")
        scene_id = str(item.get("id", index))
        text = str(item.get("text", "")).strip()
        if not text:
            raise ValueError(f"Scene {scene_id} is missing text.")
        scenes.append({"id": scene_id, "text": text})
    return scenes


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    scenes = load_scenes(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for scene in scenes:
        scene_id = scene["id"]
        text = scene["text"]
        out_path = args.output_dir / f"{scene_id}.mp3"
        print(f"Generating {out_path.name}...")
        response = client.audio.speech.create(
            model=args.model,
            voice=args.voice,
            input=text,
            instructions=args.instructions,
            response_format=args.format,
        )
        response.stream_to_file(out_path)

    print(f"Done. Wrote {len(scenes)} clips to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
