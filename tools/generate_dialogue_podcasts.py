"""Erzeuge längere Gesprächsfolgen mit zwei deutschen Neural-Stimmen.

Manuskript: podcasts/manuskripte/gespraech-*.txt
Absätze beginnen mit `Mara:` oder `Jonas:`. `PAUSE: 3` fügt drei Sekunden Denkzeit ein.

Installation: python -m pip install edge-tts imageio-ffmpeg
Aufruf: python tools/generate_dialogue_podcasts.py gespraech-plab-1-logistikstruktur
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import re
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "podcasts" / "manuskripte"
OUTPUT = ROOT / "assets" / "audio"
BUILD = ROOT / ".podcast-build" / "gespraeche"
VOICES = {
    "Mara": ("de-DE-SeraphinaMultilingualNeural", "-5%"),
    "Jonas": ("de-DE-FlorianMultilingualNeural", "-4%"),
}


def parse(script: Path) -> list[tuple[str, str | int]]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", script.read_text(encoding="utf-8-sig")) if part.strip()]
    if not paragraphs or not paragraphs[0].startswith("Gesprächsfolge:"):
        raise ValueError(f"Titel fehlt: {script.name}")
    turns: list[tuple[str, str | int]] = []
    for paragraph in paragraphs[1:]:
        match = re.fullmatch(r"(Mara|Jonas):\s*(.+)", paragraph, re.S)
        if match:
            turns.append((match.group(1), re.sub(r"\s+", " ", match.group(2)).strip()))
            continue
        pause = re.fullmatch(r"PAUSE:\s*([1-8])", paragraph)
        if pause:
            turns.append(("Pause", int(pause.group(1))))
            continue
        raise ValueError(f"Unbekannter Gesprächsabsatz in {script.name}: {paragraph[:60]}")
    if len([turn for turn in turns if turn[0] != "Pause"]) < 10:
        raise ValueError(f"Zu wenige Sprecherwechsel: {script.name}")
    return turns


async def synthesize(text: str, voice: str, rate: str, target: Path, semaphore: asyncio.Semaphore) -> None:
    if target.exists() and target.stat().st_size > 1000:
        return
    async with semaphore:
        for attempt in range(1, 5):
            try:
                await edge_tts.Communicate(text, voice, rate=rate).save(str(target))
                if target.stat().st_size <= 1000:
                    raise RuntimeError("Sprachabschnitt ist leer")
                return
            except Exception:
                target.unlink(missing_ok=True)
                if attempt == 4:
                    raise
                await asyncio.sleep(attempt * 2)


def silence(ffmpeg: str, seconds: float) -> Path:
    target = BUILD / f"pause-{str(seconds).replace('.', '_')}.mp3"
    if not target.exists():
        subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(seconds), "-c:a", "libmp3lame", "-b:a", "48k", str(target)],
            check=True,
        )
    return target


def build(script: Path, force: bool) -> None:
    target = OUTPUT / (script.stem + ".mp3")
    if target.exists() and not force:
        print(f"Schon vorhanden: {target.name}")
        return
    turns = parse(script)
    BUILD.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    semaphore = asyncio.Semaphore(3)
    clips: list[Path] = []
    tasks = []
    for index, (speaker, content) in enumerate(turns, 1):
        if speaker == "Pause":
            clips.append(silence(ffmpeg, float(content)))
            continue
        voice, rate = VOICES[speaker]
        digest = hashlib.sha256(f"{voice}|{rate}|{content}".encode("utf-8")).hexdigest()[:12]
        path = BUILD / f"{script.stem}-{index:03d}-{digest}.mp3"
        clips.append(path)
        tasks.append(synthesize(str(content), voice, rate, path, semaphore))
    print(f"{script.stem}: {len(tasks)} Sprecherbeiträge und {len(turns) - len(tasks)} Denkpausen", flush=True)
    async def render_all() -> None:
        await asyncio.gather(*tasks)

    asyncio.run(render_all())

    list_path = BUILD / f"{script.stem}-folge.txt"
    list_path.write_text("".join("file '" + path.resolve().as_posix() + "'\n" for path in clips), encoding="utf-8")
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c:a", "libmp3lame", "-b:a", "64k", "-ar", "24000", str(target)], check=True)
    if target.stat().st_size < 500_000:
        raise RuntimeError(f"Gesprächsfolge unerwartet kurz: {target.name}")
    probe = subprocess.run([ffmpeg, "-hide_banner", "-i", str(target)], capture_output=True, text=True)
    duration = re.search(r"Duration: (\d\d):(\d\d):(\d\d)", probe.stderr)
    readable = f"{int(duration[1]) * 60 + int(duration[2])}:{duration[3]}" if duration else "unbekannt"
    print(f"Fertig: {target.name} | {readable} Min. | {target.stat().st_size} Bytes", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*", help="Dateinamen ohne .txt; leer = alle Gesprächsfolgen")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    scripts = [SCRIPTS / (name + ".txt") for name in args.names] if args.names else sorted(SCRIPTS.glob("gespraech-*.txt"))
    for script in scripts:
        if not script.is_file() or not script.stem.startswith("gespraech-"):
            raise FileNotFoundError(script)
        build(script, args.force)


if __name__ == "__main__":
    main()
