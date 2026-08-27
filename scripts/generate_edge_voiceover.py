#!/usr/bin/env python3
"""Generate a single narration track for the one-minute demo using edge-tts."""

from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "final" / "voice_clips" / "one_minute_voiceover.mp3"

VOICE = "en-US-GuyNeural"
RATE = "-18%"
PITCH = "-2Hz"
TEXT = """
Space biology evidence is scattered across studies, models, and terminology.

This application keeps the boundary tight: a controlled corpus of approved publications.

From the home screen, researchers can move into Ask, Search, Corpus, Compare, or Add Paper.

Every paper stays visible with its title, organism, exposure, and source provenance.

Search returns real passages from the corpus, not generic model memory.

Ask is grounded in retrieved evidence, with citations and supporting passages the user can inspect.

And when the evidence is weak, the system says so instead of guessing.

That makes the research faster, clearer, and more trustworthy for scientific review.

Thank you for watching, and thank you for your time.
""".strip()


async def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(TEXT, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(OUT))
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
