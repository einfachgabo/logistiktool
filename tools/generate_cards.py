"""Export existing portal questions, preserving the engine's review keys."""
import json
import re
from html import escape
from pathlib import Path
from lxml import html

ROOT = Path(__file__).resolve().parents[1]

def generate():
    register = (ROOT / 'assets/portal.js').read_text(encoding='utf-8')
    chapters = re.findall(r"\{ id: '([^']+)',\s+datei: '([^']+)',\s+fach: '([^']+)',\s+nummer: '([^']+)',\s+titel: '([^']+)'", register)
    cards = []
    for chapter, filename, subject, number, title in chapters:
        doc = html.fromstring((ROOT / filename).read_bytes())
        for detail in doc.xpath('//details[contains(concat(" ", normalize-space(@class), " "), " abfrage ")]'):
            question = detail.find('summary')
            answers = detail.xpath('.//*[contains(concat(" ", normalize-space(@class), " "), " antwort ")]')
            if question is None or not answers:
                continue
            answer = answers[0]
            section = next((p for p in detail.iterancestors('section') if 'abschnitt' in p.get('class', '').split()), None)
            section_id = section.get('id', '') if section is not None else ''
            text = question.text_content().strip()
            # JavaScript slices UTF-16 code units, rather than Python codepoints.
            slug = detail.get('data-kk') or text.encode('utf-16-le')[:120].decode('utf-16-le', errors='surrogatepass')
            markup = escape(answer.text or '') + ''.join(html.tostring(c, encoding='unicode') for c in answer)
            cards.append(dict(chapter=chapter, file=filename, subject=subject, title=title,
                              number=number, section=section_id, slug=slug,
                              reviewSlug=(section_id or 'allgemein') + '.' + slug,
                              question=text, answer=markup))
    output = 'window.LERNKARTEN = ' + json.dumps(cards, ensure_ascii=True, separators=(',', ':')) + ';\n'
    (ROOT / 'assets/lernkarten-data.js').write_text(output, encoding='utf-8')
    print(f'{len(cards)} Karten aus {len(chapters)} Kapiteln exportiert.')

if __name__ == '__main__':
    generate()
