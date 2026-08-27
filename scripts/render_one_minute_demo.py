#!/usr/bin/env python3
"""Render a single short demo video from generated clips, slides, and screenshots.

This script keeps the edit simple:
- render a few PPTX/PDF slides into PNGs
- combine them with existing AI video clips and screenshots
- concatenate everything into one MP4

It expects:
- docs/final/videos/*.mp4
- docs/final/screenshots/*.png

Output:
- docs/final/Space_Biology_Evidence_Engine_One_Minute_Demo.mp4
"""

from __future__ import annotations

import json
import subprocess
from glob import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "docs" / "final"
VIDEOS = FINAL / "videos"
SHOTS = FINAL / "screenshots"
RENDERED = FINAL / "rendered_slides"
WORK = FINAL / "video_work"
OUT = FINAL / "Space_Biology_Evidence_Engine_One_Minute_Demo.mp4"
PDF = FINAL / "Space_Biology_Evidence_Engine_Pitch_Deck.pdf"
FFMPEG = "ffmpeg"
PDFTOPPM = "pdftoppm"


SCENES = [
    {
        "id": "01",
        "video": VIDEOS / "Clip 0 - logo into life-science research environment in orbit .mp4",
        "source_type": "clip",
        "duration": 7.0,
    },
    {
        "id": "02",
        "image": RENDERED / "slide-2.png",
        "source_type": "slide",
        "duration": 7.0,
    },
    {
        "id": "03",
        "video": VIDEOS / "Clip 3 - opening science atmosphere.mp4",
        "source_type": "clip",
        "duration": 7.0,
    },
    {
        "id": "04",
        "image": RENDERED / "slide-3.png",
        "source_type": "slide",
        "duration": 7.0,
    },
    {
        "id": "05",
        "image": SHOTS / "01-home.png",
        "source_type": "screenshot",
        "duration": 7.0,
    },
    {
        "id": "06",
        "image": SHOTS / "03-search.png",
        "source_type": "screenshot",
        "duration": 7.0,
    },
    {
        "id": "07",
        "image": SHOTS / "02-ask.png",
        "source_type": "screenshot",
        "duration": 7.0,
    },
    {
        "id": "08",
        "video": VIDEOS / "Clip 4 - evidence transition.mp4",
        "source_type": "clip",
        "duration": 4.0,
    },
    {
        "id": "09",
        "endcard": True,
        "source_type": "endcard",
        "duration": 4.0,
    },
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def prepare_slide_pages() -> None:
    RENDERED.mkdir(parents=True, exist_ok=True)
    page_map = {
        2: RENDERED / "slide-2.png",
        3: RENDERED / "slide-3.png",
        12: RENDERED / "slide-12.png",
    }
    for page, out_path in page_map.items():
        if out_path.exists():
            continue
        prefix = str(RENDERED / f"slide-{page}")
        run([PDFTOPPM, "-f", str(page), "-l", str(page), "-png", str(PDF), prefix])
        matches = sorted(RENDERED.glob(f"slide-{page}-*.png"))
        if matches:
            matches[0].rename(out_path)


def scene_segment(scene: dict[str, Path], index: int) -> Path:
    seg = WORK / f"scene-{index:02d}.mp4"
    duration = scene["duration"]
    if scene.get("endcard"):
        bg = RENDERED / "slide-12.png"
        run(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-i",
                str(bg),
                "-t",
                f"{duration:.3f}",
                "-vf",
                "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x041839,fade=t=in:st=0:d=0.8,fade=t=out:st=3.0:d=0.8,format=yuv420p",
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                str(seg),
            ]
        )
    elif "video" in scene:
        src = scene["video"]
        run(
            [
                FFMPEG,
                "-y",
                "-i",
                str(src),
                "-t",
                f"{duration:.3f}",
                "-vf",
                "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x041839,format=yuv420p",
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                str(seg),
            ]
        )
    else:
        img = scene["image"]
        run(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-i",
                str(img),
                "-t",
                f"{duration:.3f}",
                "-vf",
                "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x041839,format=yuv420p",
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                str(seg),
            ]
        )
    return seg


def build_concat_list(segments: list[Path]) -> Path:
    concat = WORK / "concat.txt"
    with concat.open("w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"file '{seg.as_posix()}'\n")
    return concat


def main() -> int:
    prepare_slide_pages()
    WORK.mkdir(parents=True, exist_ok=True)
    segments = [scene_segment(scene, i) for i, scene in enumerate(SCENES, start=1)]
    concat = build_concat_list(segments)
    run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(OUT),
        ]
    )
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
