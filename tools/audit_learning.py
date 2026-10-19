"""Reproduzierbarer Strukturcheck; ersetzt keine fachliche Quellenprüfung."""
from pathlib import Path
import re
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
rows, issues = [], []
for path in sorted(ROOT.glob('*.html')):
    text = path.read_text(encoding='utf-8')
    if 'window.KAPITEL' not in text:
        continue
    doc = html.fromstring(text)
    sections = doc.xpath('//section[contains(concat(" ",normalize-space(@class)," ")," abschnitt ")]')
    cards = doc.xpath('//details[contains(concat(" ",normalize-space(@class)," ")," abfrage ")]')
    for card in cards:
        q = card.xpath('./summary')
        a = card.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," antwort ")]')
        if not q or not a or not q[0].text_content().strip() or not a[0].text_content().strip():
            issues.append(f'{path.name}: leere Frage oder Antwort')
    missing = []
    for sec in sections:
        if not sec.xpath('.//details[contains(concat(" ",normalize-space(@class)," ")," abfrage ")]'):
            missing.append(sec.get('id', '?'))
    rows.append((path.name, len(sections), len(cards), ', '.join(missing) or '–'))
js = (ROOT / 'assets/portal.js').read_text(encoding='utf-8')
audio = re.findall(r"\{ titel: '[^']*', datei: '(assets/audio/[^']+)'[^\n]*", js)
for file in audio:
    p = ROOT / file
    if not p.exists() or p.stat().st_size < 1000:
        issues.append(f'{file}: fehlt oder auffällig klein')
    script = ROOT / 'podcasts/manuskripte' / (p.stem.removesuffix('-elevenlabs') + '.txt')
    if not script.exists():
        issues.append(f'{file}: Manuskript fehlt')
    elif p.stem.startswith('gespraech-'):
        paragraphs = re.split(r'\n\s*\n', script.read_text(encoding='utf-8-sig').strip())[1:]
        for paragraph in paragraphs:
            if not re.fullmatch(r'(?:Mara|Jonas):\s*.+|PAUSE:\s*[1-8]', paragraph.strip(), re.S):
                issues.append(f'{script.name}: Absatz ohne gültigen Sprecher/Pause')
report = ['# Lernportalprüfung · 19. Oktober 2026', '',
          '## Automatisch geprüfte Abdeckung', '',
          '| Kapitel | Abschnitte | Frage-Antwort-Karten | Abschnitte ohne Karten |',
          '|---|---:|---:|---|']
report += [f'| {name} | {sections} | {cards} | {missing} |' for name, sections, cards, missing in rows]
report += ['', f'Gesamt: {sum(r[2] for r in rows)} Karten; {len(audio)} registrierte Audiodateien.', '',
           '## Befunde', '']
report += issues or ['Keine leeren Frage-Antwort-Paare, fehlenden Audio-/Manuskriptdateien oder ungültigen Gesprächsabsätze gefunden.']
output = ROOT / 'tmp' / 'audit' / 'struktur.md'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text('\n'.join(report), encoding='utf-8')
print('\n'.join(report))
raise SystemExit(bool(issues))
