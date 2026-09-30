"""Gesprächsfolge mit zwei Resemble-AI-Stimmen erzeugen.

Ohne API-Kosten prüfen:
  python tools/generate_resemble_dialogue.py --dry-run

Kurze lokale Hörprobe (ungefähr die ersten sechs Sprecherbeiträge):
  python tools/generate_resemble_dialogue.py --key-file PFAD_ZUM_SCHLUESSEL

Vollständige Folge nach Hörprüfung:
  python tools/generate_resemble_dialogue.py --key-file PFAD_ZUM_SCHLUESSEL --full

Der Schlüssel kann alternativ in RESEMBLE_API_KEY liegen. Er wird nie ausgegeben.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPTS = ROOT / "podcasts" / "manuskripte"
BUILD = ROOT / ".podcast-build" / "resemble"
OUTPUT = ROOT / "assets" / "audio"
DEFAULT_VOICES = {"Mara": "3143af68", "Jonas": "e7e459d6"}  # Resemble: Anita und Ulrich


def read_key(path: Path | None) -> str:
    if path:
        value = path.read_text(encoding="utf-8-sig").strip()
    else:
        value = os.environ.get("RESEMBLE_API_KEY", "").strip()
    if value.startswith("RESEMBLE_API_KEY="):
        value = value.split("=", 1)[1].strip()
    return value.strip('"\'')


def request_json(url: str, key: str, body: dict | None = None) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        try:
            message = json.loads(error.read(2000)).get("error_params", {}).get("explanation", "")
        except (ValueError, TypeError):
            message = ""
        raise RuntimeError(f"Resemble meldet HTTP {error.code}: {message or 'Anfrage fehlgeschlagen'}") from None


def parse(path: Path) -> list[tuple[str, str | int]]:
    parts = [part.strip() for part in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig")) if part.strip()]
    if not parts or not parts[0].startswith("Gesprächsfolge:"):
        raise ValueError(f"Kein Gesprächsmanuskript: {path.name}")
    turns: list[tuple[str, str | int]] = []
    for part in parts[1:]:
        speech = re.fullmatch(r"(Mara|Jonas):\s*(.+)", part, re.S)
        pause = re.fullmatch(r"PAUSE:\s*([1-8])", part)
        if speech:
            text = re.sub(r"\s+", " ", speech[2]).strip()
            if len(text) > 3000:
                raise ValueError("Ein Sprecherbeitrag überschreitet das Resemble-Limit von 3.000 Zeichen.")
            turns.append((speech[1], text))
        elif pause:
            turns.append(("Pause", int(pause[1])))
        else:
            raise ValueError(f"Unbekannter Absatz: {part[:60]}")
    return turns


def choose(turns: list[tuple[str, str | int]], full: bool) -> list[tuple[str, str | int]]:
    if full:
        return turns
    sample: list[tuple[str, str | int]] = []
    for speaker, content in turns:
        if speaker == "Pause":
            continue
        sample.append((speaker, content))
        if len(sample) == 6:
            break
    return sample


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", nargs="?", default="gespraech-plab-1-logistikstruktur")
    parser.add_argument("--key-file", type=Path, help="Lokale Schlüsseldatei außerhalb des Repositories")
    parser.add_argument("--mara-voice", default=DEFAULT_VOICES["Mara"], help="Resemble voice_uuid; Standard: Anita")
    parser.add_argument("--jonas-voice", default=DEFAULT_VOICES["Jonas"], help="Resemble voice_uuid; Standard: Ulrich")
    parser.add_argument("--full", action="store_true", help="Ganzes Kapitel aufnehmen")
    parser.add_argument("--dry-run", action="store_true", help="Ohne API-Anfragen planen")
    args = parser.parse_args()
    if not re.fullmatch(r"gespraech-[a-z0-9-]+", args.name):
        parser.error("Nur Gesprächsmanuskripte sind erlaubt.")
    source = MANUSCRIPTS / f"{args.name}.txt"
    if not source.is_file():
        parser.error(f"Manuskript fehlt: {source}")
    turns = choose(parse(source), args.full)
    speech_count = sum(speaker != "Pause" for speaker, _ in turns)
    print(f"{args.name}: {speech_count} Sprecherbeiträge, {sum(len(str(content)) for speaker, content in turns if speaker != 'Pause')} Textzeichen")
    if args.dry_run:
        return
    key = read_key(args.key_file)
    if not key:
        parser.error("RESEMBLE_API_KEY oder --key-file fehlt.")
    voices = {"Mara": args.mara_voice, "Jonas": args.jonas_voice}
    if voices["Mara"] == voices["Jonas"]:
        parser.error("Bitte zwei verschiedene Stimmen wählen.")
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    BUILD.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    missing = 0
    for index, (speaker, content) in enumerate(turns, 1):
        if speaker == "Pause":
            continue
        digest = hashlib.sha256(f"{voices[speaker]}|{content}".encode("utf-8")).hexdigest()[:14]
        file = BUILD / f"{args.name}-{index:03d}-{digest}.mp3"
        if not file.is_file() or file.stat().st_size < 1000:
            missing += 1
    if missing:
        wallet_response = request_json("https://app.resemble.ai/billing/api/v1/wallet", key)
        wallet = wallet_response.get("wallet") or wallet_response
        balance = wallet.get("balance_cents")
        if isinstance(balance, (int, float)) and balance <= 0:
            raise RuntimeError("Das Resemble-Guthaben ist leer. Es wurden keine Sprachabschnitte erzeugt.")
    for index, (speaker, content) in enumerate(turns, 1):
        if speaker == "Pause":
            pause = BUILD / f"pause-{content}.mp3"
            if not pause.exists():
                subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(content), "-c:a", "libmp3lame", "-b:a", "128k", str(pause)], check=True)
            files.append(pause)
            continue
        digest = hashlib.sha256(f"{voices[speaker]}|{content}".encode("utf-8")).hexdigest()[:14]
        file = BUILD / f"{args.name}-{index:03d}-{digest}.mp3"
        if not file.is_file() or file.stat().st_size < 1000:
            response = request_json(
                "https://f.cluster.resemble.ai/synthesize",
                key,
                {"voice_uuid": voices[speaker], "data": str(content), "output_format": "mp3", "sample_rate": 44100},
            )
            if not response.get("success") or not response.get("audio_content"):
                raise RuntimeError(f"Resemble konnte Abschnitt {index} nicht erzeugen: {response.get('issues', [])}")
            audio = base64.b64decode(response["audio_content"])
            if len(audio) < 1000:
                raise RuntimeError(f"Resemble lieferte für Abschnitt {index} keine nutzbare MP3.")
            file.write_bytes(audio)
            print(f"  {index}/{len(turns)} erzeugt", flush=True)
        files.append(file)
    playlist = BUILD / f"{args.name}-{'full' if args.full else 'sample'}-concat.txt"
    playlist.write_text("".join(f"file '{file.resolve().as_posix()}'\n" for file in files), encoding="utf-8")
    target = (OUTPUT if args.full else BUILD) / f"{args.name}-resemble{'-probe' if not args.full else ''}.mp3"
    subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(playlist), "-c:a", "libmp3lame", "-b:a", "128k", str(target)], check=True)
    print(f"Fertig: {target}")


if __name__ == "__main__":
    main()
