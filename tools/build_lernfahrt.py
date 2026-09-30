"""Bündelt die neuen Gesprächsfolgen zu einer Autofahrt mit Kapitelmarken.

Benötigt imageio-ffmpeg. Zuerst alle Einzel-MP3s erzeugen, dann ausführen:
  python tools/build_lernfahrt.py
"""

from __future__ import annotations

import re
import subprocess
import json
from pathlib import Path

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "assets" / "audio"
BUILD = ROOT / ".podcast-build" / "elevenlabs"
OUTPUT = AUDIO / "lernfahrt-01-logistikgrundlagen.mp3"
INDEX = AUDIO / "lernfahrt-01-kapitel.json"
CHAPTERS = [
    ("1.1 · Logistikstruktur", "gespraech-plab-1-logistikstruktur-elevenlabs.mp3", "plab-1-logistikstruktur.html"),
    ("1.2 · Logistiksysteme", "gespraech-plab-2-logistiksysteme-elevenlabs.mp3", "plab-2-logistiksysteme.html"),
    ("1.3 · Ziele und Kennzahlen", "gespraech-plab-3-kennzahlen-elevenlabs.mp3", "plab-3-logistische-ablaeufe.html"),
    ("2.1 · Logistikstrategie", "gespraech-plab-4-strategie-elevenlabs.mp3", "plab-4-strategie.html"),
    ("Logistikkonzepte und Analyse", "gespraech-gruber-1-konzept-elevenlabs.mp3", "gruber-1-konzepte.html"),
    ("Beschaffung und Bedarf", "gespraech-gruber-2-beschaffung-elevenlabs.mp3", "gruber-2-beschaffung.html"),
    ("Produktion, Lager und Distribution", "gespraech-gruber-3-lager-elevenlabs.mp3", "gruber-3-lager-transport.html"),
    ("Kurzcheck · Kapitel 1.1", "gespraech-plab-1-kurzcheck-elevenlabs.mp3", "plab-1-logistikstruktur.html"),
    ("Kurzcheck · Kapitel 1.2", "gespraech-plab-2-kurzcheck-elevenlabs.mp3", "plab-2-logistiksysteme.html"),
    ("Kurzcheck · Kapitel 1.3", "gespraech-plab-3-kurzcheck-elevenlabs.mp3", "plab-3-logistische-ablaeufe.html"),
]


def duration_ms(ffmpeg: str, path: Path) -> int:
    process = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", process.stderr)
    if not match:
        raise RuntimeError(f"MP3-Dauer nicht lesbar: {path}")
    hours, minutes, seconds = match.groups()
    return round((int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * 1000)


def main() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    BUILD.mkdir(parents=True, exist_ok=True)
    missing = [name for _, name, _ in CHAPTERS if not (AUDIO / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Fehlende Einzel-MP3s: {', '.join(missing)}")

    listing = BUILD / "lernfahrt-01-concat.txt"
    listing.write_text(
        "".join(f"file '{(AUDIO / name).resolve().as_posix()}'\n" for _, name, _ in CHAPTERS),
        encoding="utf-8",
    )
    metadata = BUILD / "lernfahrt-01-chapters.txt"
    lines = [";FFMETADATA1", "title=Lernfahrt 1: Logistikgrundlagen", "artist=Mara und Jonas", "comment=Kapitelgespraeche und Kurzchecks fuer unterwegs"]
    position = 0
    index = []
    for title, name, page in CHAPTERS:
        duration = duration_ms(ffmpeg, AUDIO / name)
        end = position + duration
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={position}", f"END={end}", f"title={title}"]
        index.append({"title": title, "startSeconds": round(position / 1000, 2), "durationSeconds": round(duration / 1000, 2), "audio": name, "page": page})
        print(f"{position // 60000:02d}:{(position // 1000) % 60:02d}  {title}")
        position = end
    metadata.write_text("\n".join(lines) + "\n", encoding="utf-8")
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run(
        [ffmpeg, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-f", "ffmetadata", "-i", str(metadata), "-map", "0:a", "-map_metadata", "1", "-map_chapters", "1",
         "-c:a", "copy", str(OUTPUT)],
        check=True,
    )
    subprocess.run([ffmpeg, "-v", "error", "-i", str(OUTPUT), "-f", "null", "NUL"], check=True)
    print(f"Fertig: {OUTPUT} · {position / 60000:.1f} Minuten")


if __name__ == "__main__":
    main()
