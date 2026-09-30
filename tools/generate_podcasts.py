"""Erzeuge kurze MP3-Folgen aus den selbst verfassten Podcast-Manuskripten.

Installation: python -m pip install edge-tts imageio-ffmpeg
Aufruf: python tools/generate_podcasts.py plab-2-a-informationssysteme
Ohne Namen werden alle Manuskripte verarbeitet. Bereits fertige MP3s bleiben erhalten.
"""

import argparse
import asyncio
import hashlib
import re
import subprocess
import time
from pathlib import Path

import edge_tts
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "podcasts" / "manuskripte"
OUTPUT = ROOT / "assets" / "audio"
BUILD = ROOT / ".podcast-build"
VOICE = "de-DE-KatjaNeural"


def split_text(source: str, limit: int = 900) -> list[str]:
    units = []
    for paragraph in re.split(r"\n\s*\n", source.strip()):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= limit:
            units.append(paragraph)
            continue
        current = ""
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            if current and len(current) + len(sentence) + 1 > limit:
                units.append(current)
                current = ""
            current = (current + " " + sentence).strip()
        if current:
            units.append(current)
    chunks = []
    current = ""
    for unit in units:
        if current and len(current) + len(unit) + 2 > limit:
            chunks.append(current)
            current = ""
        current = (current + "\n\n" + unit).strip()
    if current:
        chunks.append(current)
    return chunks


async def speak(text: str, path: Path) -> None:
    await edge_tts.Communicate(text, VOICE, rate="-5%").save(str(path))


def build_episode(script: Path, force: bool = False) -> None:
    target = OUTPUT / (script.stem + ".mp3")
    if target.exists() and not force:
        print(f"Schon vorhanden: {target.name}", flush=True)
        return
    text = script.read_text(encoding="utf-8-sig")
    if len(text.split()) < 180:
        raise ValueError(f"Manuskript zu kurz: {script.name}")
    chunks = split_text(text)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    files = []
    print(f"{script.stem}: {len(chunks)} Sprachabschnitte", flush=True)
    for i, chunk in enumerate(chunks, 1):
        digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()[:12]
        path = BUILD / f"{script.stem}-{i:02d}-{digest}.mp3"
        if not path.exists() or path.stat().st_size < 1000:
            for attempt in range(1, 5):
                try:
                    asyncio.run(speak(chunk, path))
                    break
                except Exception:
                    path.unlink(missing_ok=True)
                    if attempt == 4:
                        raise
                    time.sleep(attempt * 2)
        files.append(path)
        print(f"  {i}/{len(chunks)}", flush=True)

    list_file = BUILD / (script.stem + ".txt")
    list_file.write_text(
        "".join("file '" + p.resolve().as_posix() + "'\n" for p in files),
        encoding="utf-8",
    )
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(target)],
        check=True,
    )
    if target.stat().st_size < 50_000:
        raise RuntimeError(f"Audio unerwartet kurz: {target.name}")
    probe = subprocess.run([ffmpeg, "-hide_banner", "-i", str(target)], capture_output=True, text=True)
    duration = re.search(r"Duration: (\d\d):(\d\d):(\d\d)", probe.stderr)
    readable = f"{int(duration[1]) * 60 + int(duration[2])}:{duration[3]}" if duration else "unbekannt"
    print(f"Fertig: {target.name} | {readable} Min. | {target.stat().st_size} Bytes", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*", help="Manuskriptname ohne .txt; leer = alle")
    parser.add_argument("--force", action="store_true", help="fertige MP3 neu erzeugen")
    args = parser.parse_args()
    scripts = [SCRIPTS / (name + ".txt") for name in args.names] if args.names else sorted(script for script in SCRIPTS.glob("*.txt") if not script.stem.startswith("gespraech-"))
    for script in scripts:
        if not script.exists():
            raise FileNotFoundError(script)
        if script.stem.startswith("gespraech-"):
            raise ValueError(f"Gesprächsfolgen mit tools/generate_dialogue_podcasts.py erzeugen: {script.name}")
        build_episode(script, args.force)


if __name__ == "__main__":
    main()
