"""Vertone ein Gesprächsmanuskript mit der ElevenLabs Text-to-Dialogue API.

Beispiel ohne API-Kosten:
  python tools/generate_elevenlabs_dialogue.py --dry-run

Zur Aufnahme ELEVENLABS_API_KEY lokal als Umgebungsvariable setzen oder den
Schlüssel in ~/.codex/elevenlabs.key.txt speichern. Zwei deutschsprachige
voice_id-Werte aus dem eigenen ElevenLabs-Konto übergeben:
  python tools/generate_elevenlabs_dialogue.py --female-voice ID --male-voice ID

Die Ausgabe bekommt den Zusatz -elevenlabs und ersetzt nie automatisch die
bereits veröffentlichte Folge. API-Schlüssel gehören nicht ins Repository.
--sample erzeugt mit vier Sprecherbeiträgen eine lokale Hörprobe im Build-Ordner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "podcasts" / "manuskripte"
BUILD = ROOT / ".podcast-build" / "elevenlabs"
OUTPUT = ROOT / "assets" / "audio"
MODEL = "eleven_v4"
MAX_CHARS = 1900  # ElevenLabs empfiehlt höchstens 2.000 Zeichen je Anfrage.
DEFAULT_KEY_FILE = Path.home() / ".codex" / "elevenlabs.key.txt"


def read_key(path: Path) -> str:
    value = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not value and path.is_file():
        value = path.read_text(encoding="utf-8-sig").strip()
    if value.startswith("ELEVENLABS_API_KEY="):
        value = value.split("=", 1)[1].strip()
    return value.strip('"\'')


def parse(path: Path) -> list[tuple[str, str | int]]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig")) if p.strip()]
    if not parts or not parts[0].startswith("Gesprächsfolge:"):
        raise ValueError(f"Kein Gesprächsmanuskript: {path}")
    turns: list[tuple[str, str | int]] = []
    for part in parts[1:]:
        speaker = re.fullmatch(r"(Mara|Jonas):\s*(.+)", part, re.S)
        pause = re.fullmatch(r"PAUSE:\s*([1-8])", part)
        if speaker:
            turns.append((speaker[1], re.sub(r"\s+", " ", speaker[2]).strip()))
        elif pause:
            turns.append(("Pause", int(pause[1])))
        else:
            raise ValueError(f"Unbekannter Absatz: {part[:70]}")
    return turns


def chunks(turns: list[tuple[str, str | int]]) -> list[list[tuple[str, str | int]] | int]:
    result: list[list[tuple[str, str | int]] | int] = []
    current: list[tuple[str, str | int]] = []
    length = 0
    for speaker, value in turns:
        if speaker == "Pause":
            if current:
                result.append(current)
                current = []
                length = 0
            result.append(int(value))
            continue
        text_length = len(str(value))
        if text_length > MAX_CHARS:
            raise ValueError(f"Ein einzelner Sprecherbeitrag ist zu lang ({text_length} Zeichen).")
        if current and length + text_length > MAX_CHARS:
            result.append(current)
            current = []
            length = 0
        current.append((speaker, value))
        length += text_length
    if current:
        result.append(current)
    return result


def generate(chunk: list[tuple[str, str | int]], voices: dict[str, str], key: str, path: Path) -> None:
    payload = {
        "model_id": MODEL,
        "language_code": "de",
        "inputs": [{"text": str(value), "voice_id": voices[speaker]} for speaker, value in chunk],
    }
    request = urllib.request.Request(
        "https://api.elevenlabs.io/v1/text-to-dialogue?output_format=mp3_44100_128",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read(1000).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs meldet HTTP {error.code}: {detail}") from None
    if not data.startswith(b"ID3") and data[:2] not in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        raise RuntimeError("ElevenLabs hat keine erkennbare MP3-Datei geliefert.")
    path.write_bytes(data)


def check_balance(key: str, needed: int) -> None:
    request = urllib.request.Request(
        "https://api.elevenlabs.io/v1/user/subscription",
        headers={"xi-api-key": key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            subscription = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"ElevenLabs-Zugang konnte nicht geprüft werden (HTTP {error.code}).") from None
    used = subscription.get("character_count")
    limit = subscription.get("character_limit")
    if isinstance(used, int) and isinstance(limit, int):
        remaining = limit - used
        print(f"ElevenLabs-Tarif: {subscription.get('tier', 'unbekannt')} · etwa {remaining} Credits verfügbar")
        if remaining < needed:
            raise RuntimeError(f"Für die noch nicht erzeugten Abschnitte werden etwa {needed} Credits benötigt. Bitte keinen kostenpflichtigen Mehrverbrauch unbeabsichtigt starten.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", nargs="?", default="gespraech-plab-1-logistikstruktur", help="Manuskriptname ohne .txt")
    parser.add_argument("--female-voice", help="ElevenLabs voice_id für Mara")
    parser.add_argument("--male-voice", help="ElevenLabs voice_id für Jonas")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE, help="Private Schlüsseldatei außerhalb des Repositories")
    parser.add_argument("--sample", action="store_true", help="Nur vier Sprecherbeiträge als lokale Hörprobe")
    parser.add_argument("--dry-run", action="store_true", help="Abschnitte und Zeichenzahl zeigen, ohne API-Anfrage")
    args = parser.parse_args()
    script = SOURCE / f"{args.name}.txt"
    if not script.is_file() or not args.name.startswith("gespraech-"):
        parser.error(f"Gesprächsmanuskript fehlt: {script}")
    turns = parse(script)
    if args.sample:
        sample = []
        for speaker, content in turns:
            if speaker == "Pause":
                continue
            sample.append((speaker, content))
            if len(sample) == 4:
                break
        turns = sample
    parts = chunks(turns)
    voiced = [p for p in parts if isinstance(p, list)]
    total = sum(len(str(value)) for part in voiced for _, value in part)
    print(f"{args.name}: {len(voiced)} API-Abschnitte, {len(parts) - len(voiced)} Denkpausen, {total} Textzeichen")
    if args.dry_run:
        for index, part in enumerate(voiced, 1):
            print(f"  Abschnitt {index}: {sum(len(str(value)) for _, value in part)} Zeichen, {len(part)} Sprecherbeiträge")
        return
    key = read_key(args.key_file)
    if not key:
        parser.error(f"ElevenLabs-Schlüssel fehlt. Lokal unter {args.key_file} speichern oder ELEVENLABS_API_KEY setzen; nie in Git eintragen.")
    if not key.startswith("sk_"):
        parser.error("Die Datei enthält keine gültige API-Schlüsselzeichenfolge. Bitte den bei ElevenLabs nur einmal angezeigten Schlüssel statt der Key-ID speichern.")
    if not args.female_voice or not args.male_voice:
        parser.error("Bitte --female-voice und --male-voice aus dem eigenen ElevenLabs-Konto angeben.")
    if args.female_voice == args.male_voice:
        parser.error("Für das Gespräch sind zwei verschiedene Stimmen nötig.")
    voices = {"Mara": args.female_voice, "Jonas": args.male_voice}
    import imageio_ffmpeg  # Erst bei einer tatsächlichen Aufnahme benötigt.

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    BUILD.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    missing = 0
    for index, part in enumerate(parts, 1):
        if isinstance(part, int):
            continue
        identity = json.dumps({"model": MODEL, "voices": voices, "turns": part}, ensure_ascii=False)
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:14]
        clip = BUILD / f"{args.name}-{index:02d}-{digest}.mp3"
        if not clip.exists() or clip.stat().st_size < 1000:
            missing += sum(len(str(value)) for _, value in part)
    if missing:
        check_balance(key, missing)
    clips: list[Path] = []
    for index, part in enumerate(parts, 1):
        if isinstance(part, int):
            pause = BUILD / f"pause-{part}.mp3"
            if not pause.exists():
                subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(part), "-c:a", "libmp3lame", "-b:a", "128k", str(pause)], check=True)
            clips.append(pause)
            continue
        identity = json.dumps({"model": MODEL, "voices": voices, "turns": part}, ensure_ascii=False)
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:14]
        clip = BUILD / f"{args.name}-{index:02d}-{digest}.mp3"
        if not clip.exists() or clip.stat().st_size < 1000:
            generate(part, voices, key, clip)
        clips.append(clip)
        print(f"  {index}/{len(parts)} fertig", flush=True)
    listing = BUILD / f"{args.name}-{'sample' if args.sample else 'full'}-concat.txt"
    listing.write_text("".join(f"file '{clip.resolve().as_posix()}'\n" for clip in clips), encoding="utf-8")
    output = (BUILD if args.sample else OUTPUT) / f"{args.name}-elevenlabs{'-probe' if args.sample else ''}.mp3"
    subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c:a", "libmp3lame", "-b:a", "128k", str(output)], check=True)
    print(f"Hörprobe fertig: {output}")


if __name__ == "__main__":
    main()
