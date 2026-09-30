"""Bündelt die neuen Gesprächsfolgen zu einer Autofahrt mit Kapitelmarken.

Benötigt imageio-ffmpeg. Zuerst alle Einzel-MP3s erzeugen, dann ausführen:
  python tools/build_lernfahrt.py
"""

from __future__ import annotations

import re
import subprocess
import json
import argparse
from pathlib import Path

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "assets" / "audio"
BUILD = ROOT / ".podcast-build" / "elevenlabs"
CHAPTERS_1 = [
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
CHAPTERS_2 = [
    ("Rückblick · Logistikkonzepte", "gespraech-gruber-1-konzept-elevenlabs.mp3", "gruber-1-konzepte.html"),
    ("Rückblick · Beschaffung", "gespraech-gruber-2-beschaffung-elevenlabs.mp3", "gruber-2-beschaffung.html"),
    ("Rückblick · Lager und Transport", "gespraech-gruber-3-lager-elevenlabs.mp3", "gruber-3-lager-transport.html"),
    ("Strategie, IT und Projekte", "gespraech-gruber-4-projekt-elevenlabs.mp3", "gruber-4-strategie.html"),
    ("Dienstleistungen und Verträge", "gespraech-gruber-5-vergabe-elevenlabs.mp3", "gruber-5-vergabe.html"),
    ("Logistik als System", "gespraech-kroul-0-einfuehrung-elevenlabs.mp3", "kroul-0-einfuehrung.html"),
    ("Veränderungsprozesse", "gespraech-kroul-1-wandel-elevenlabs.mp3", "kroul-1-changemanagement.html"),
    ("Menschen beteiligen", "gespraech-kroul-2-beteiligung-elevenlabs.mp3", "kroul-2-zweck-und-ziel.html"),
    ("Kommunikation und Konflikte", "gespraech-gruchala-1-kommunikation-elevenlabs.mp3", "gruchala-1-kommunikation.html"),
    ("Personalbedarf und Auswahl", "gespraech-gruchala-2-personal-elevenlabs.mp3", "gruchala-2-personal.html"),
    ("Arbeitszeit", "gespraech-gruchala-3-arbeitszeit-elevenlabs.mp3", "gruchala-3-arbeitsrecht.html"),
    ("Führung", "gespraech-gruchala-4-fuehrung-elevenlabs.mp3", "gruchala-4-fuehrung.html"),
    ("Ausbildung und Arbeitsschutz", "gespraech-gruchala-5-ausbildung-elevenlabs.mp3", "gruchala-5-ausbildung.html"),
    ("Mathe-Grundlagen", "gespraech-mathe-grundlagen-elevenlabs.mp3", "mathe-grundlagen.html"),
    ("Kurzcheck · Projekt", "gespraech-gruber-4-kurzcheck-elevenlabs.mp3", "gruber-4-strategie.html"),
    ("Kurzcheck · Vergabe", "gespraech-gruber-5-kurzcheck-elevenlabs.mp3", "gruber-5-vergabe.html"),
    ("Kurzcheck · Veränderung", "gespraech-kroul-1-kurzcheck-elevenlabs.mp3", "kroul-1-changemanagement.html"),
    ("Kurzcheck · Schichtplan", "gespraech-gruchala-3-kurzcheck-elevenlabs.mp3", "gruchala-3-arbeitsrecht.html"),
    ("Kurzcheck · Mathe", "gespraech-mathe-kurzcheck-elevenlabs.mp3", "mathe-grundlagen.html"),
]


def duration_ms(ffmpeg: str, path: Path) -> int:
    process = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", process.stderr)
    if not match:
        raise RuntimeError(f"MP3-Dauer nicht lesbar: {path}")
    hours, minutes, seconds = match.groups()
    return round((int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * 1000)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fahrt", choices=("1", "2"), default="1")
    args = parser.parse_args()
    nummer = args.fahrt.zfill(2)
    chapters = CHAPTERS_1 if args.fahrt == "1" else CHAPTERS_2
    name = "logistikgrundlagen" if args.fahrt == "1" else "planung-wandel-fuehrung"
    output = AUDIO / f"lernfahrt-{nummer}-{name}.mp3"
    index_path = AUDIO / f"lernfahrt-{nummer}-kapitel.json"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    BUILD.mkdir(parents=True, exist_ok=True)
    missing = [name for _, name, _ in chapters if not (AUDIO / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Fehlende Einzel-MP3s: {', '.join(missing)}")

    listing = BUILD / f"lernfahrt-{nummer}-concat.txt"
    listing.write_text(
        "".join(f"file '{(AUDIO / name).resolve().as_posix()}'\n" for _, name, _ in chapters),
        encoding="utf-8",
    )
    metadata = BUILD / f"lernfahrt-{nummer}-chapters.txt"
    title = "Logistikgrundlagen" if args.fahrt == "1" else "Planung, Wandel und Führung"
    lines = [";FFMETADATA1", f"title=Lernfahrt {args.fahrt}: {title}", "artist=Mara und Jonas", "comment=Kapitelgespraeche und Denkpausen fuer unterwegs"]
    position = 0
    index = []
    for title, name, page in chapters:
        duration = duration_ms(ffmpeg, AUDIO / name)
        end = position + duration
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={position}", f"END={end}", f"title={title}"]
        index.append({"title": title, "startSeconds": round(position / 1000, 2), "durationSeconds": round(duration / 1000, 2), "audio": name, "page": page})
        print(f"{position // 60000:02d}:{(position // 1000) % 60:02d}  {title}")
        position = end
    metadata.write_text("\n".join(lines) + "\n", encoding="utf-8")
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run(
        [ffmpeg, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-f", "ffmetadata", "-i", str(metadata), "-map", "0:a", "-map_metadata", "1", "-map_chapters", "1",
         "-c:a", "copy" if args.fahrt == "1" else "libmp3lame", *(([]) if args.fahrt == "1" else ["-b:a", "96k"]), str(output)],
        check=True,
    )
    subprocess.run([ffmpeg, "-v", "error", "-i", str(output), "-f", "null", "NUL"], check=True)
    print(f"Fertig: {output} · {position / 60000:.1f} Minuten")


if __name__ == "__main__":
    main()
