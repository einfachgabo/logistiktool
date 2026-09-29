"""Erzeuge ausfüllbare Unterrichtshefte zu den Lernkapiteln des Portals."""

from __future__ import annotations

import re
from pathlib import Path

from lxml import html
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "hefte"
PAGE_W, PAGE_H = A4
MARGIN = 48
TEXT_W = PAGE_W - 2 * MARGIN
INK = colors.HexColor("#1d292c")
MUTED = colors.HexColor("#526469")
PALE = colors.HexColor("#eef3f2")
ACCENTS = {
    "plab": colors.HexColor("#2865a5"),
    "gruber": colors.HexColor("#22806b"),
    "kroul": colors.HexColor("#985c34"),
    "gruchala": colors.HexColor("#7651a2"),
    "mathe": colors.HexColor("#2865a5"),
}


def register_fonts() -> None:
    fonts = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Workbook", str(fonts / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Workbook-Bold", str(fonts / "arialbd.ttf")))


def cleaned(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")


def chapter_files() -> list[tuple[str, Path]]:
    source = (ROOT / "assets" / "portal.js").read_text(encoding="utf-8-sig")
    entries = re.findall(r"\{\s*id:\s*'([^']+)'\s*,\s*datei:\s*'([^']+)'", source)
    return [(key, ROOT / name) for key, name in entries if key not in {"plab-1", "formeln", "aufgaben"}]


def chapter_data(path: Path) -> tuple[str, str, list[tuple[str, str, str, list[str]]]]:
    doc = html.fromstring(path.read_text(encoding="utf-8-sig"))
    title = cleaned(doc.xpath("//main//h1")[0].text_content())
    subtitles = doc.xpath('//main//p[contains(concat(" ",normalize-space(@class)," ")," kopf-sub ")]')
    subtitle = cleaned(subtitles[0].text_content()) if subtitles else ""
    sections = []
    for section in doc.xpath('//section[contains(concat(" ",normalize-space(@class)," ")," abschnitt ")]'):
        heading = section.xpath('.//div[contains(concat(" ",normalize-space(@class)," ")," ab-kopf ")]/h2')
        if not heading:
            continue
        raw = cleaned(heading[0].text_content())
        nr = heading[0].xpath('./span[contains(concat(" ",normalize-space(@class)," ")," ab-nr ")]/text()')
        if nr and raw.startswith(cleaned(nr[0])):
            raw = raw[len(cleaned(nr[0])):].strip()
        group = cleaned(section.get("data-gruppe") or "Kapitelnotizen")
        summary = ""
        for kind in ("merk", "def", "einstieg"):
            matches = section.xpath('.//div[contains(concat(" ",normalize-space(@class)," ")," ' + kind + ' ")]//p')
            if matches:
                summary = cleaned(matches[0].text_content())
                break
        if not summary:
            matches = section.xpath("./p")
            summary = cleaned(matches[0].text_content()) if matches else "Erkläre die Kernidee dieses Abschnitts mit einem eigenen Beispiel."
        if "Selbsttest" in raw:
            summary = "Beantworte die Fragen zuerst ohne Vorlage. Prüfe danach deine Lösung und notiere, wo du noch unsicher bist."
        elif len(simpleSplit(summary, "Workbook", 9.5, TEXT_W)) > 5:
            summary = re.split(r"(?<=[.!?])\s+", summary, maxsplit=1)[0]
        questions = [cleaned(q.text_content()) for q in section.xpath('.//details[contains(concat(" ",normalize-space(@class)," ")," abfrage ")]/summary')[:2]]
        if not questions:
            if "Selbsttest" in raw:
                questions = ["Welche drei Aufgaben konntest du noch nicht sicher beantworten?", "Welche Regel oder welcher Rechenweg hilft dir dabei?"]
            else:
                subheads = [cleaned(h.text_content()) for h in section.xpath('./h3')[:2]]
                questions = ["Erkläre mit einem eigenen Beispiel: " + s for s in subheads] or ["Was ist die wichtigste Idee dieses Abschnitts?"]
        sections.append((group, raw, summary, questions))
    if not sections:
        raise ValueError(f"Keine Abschnitte gefunden: {path.name}")
    return title, subtitle, sections


def draw_lines(pdf: canvas.Canvas, text: str, x: float, y: float, width: float, size: int, leading: int, font: str, color: colors.Color, max_lines: int | None = None) -> float:
    pdf.setFillColor(color)
    pdf.setFont(font, size)
    lines = simpleSplit(cleaned(text), font, size, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + " ..."
    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def frame(pdf: canvas.Canvas, accent: colors.Color, chapter: str, page: int, total: int) -> None:
    pdf.setFillColor(INK)
    pdf.rect(0, PAGE_H - 77, PAGE_W, 77, stroke=0, fill=1)
    pdf.setFillColor(accent)
    pdf.rect(0, PAGE_H - 80, PAGE_W, 3, stroke=0, fill=1)
    pdf.setFont("Workbook-Bold", 9)
    pdf.setFillColor(colors.white)
    pdf.drawString(MARGIN, PAGE_H - 34, "FACHWIRT FÜR LOGISTIKSYSTEME")
    draw_lines(pdf, chapter, MARGIN, PAGE_H - 55, TEXT_W, 10, 12, "Workbook", colors.HexColor("#cbd8db"), 1)
    pdf.setStrokeColor(colors.HexColor("#d5dddc"))
    pdf.line(MARGIN, 42, PAGE_W - MARGIN, 42)
    pdf.setFont("Workbook", 8.5)
    pdf.setFillColor(MUTED)
    pdf.drawString(MARGIN, 27, "Mein Unterrichtsheft - ausfüllbar und druckbar")
    pdf.drawRightString(PAGE_W - MARGIN, 27, f"{page} / {total}")


def field(pdf: canvas.Canvas, name: str, tooltip: str, x: float, y: float, width: float, height: float, multiline: bool = True) -> None:
    pdf.acroForm.textfield(
        name=name, tooltip=tooltip, x=x, y=y, width=width, height=height,
        borderStyle="solid", borderWidth=0.9, borderColor=colors.HexColor("#a9bfba"),
        fillColor=colors.white, textColor=INK, fontName="Helvetica", fontSize=11,
        fieldFlags="multiline" if multiline else "",
        forceBorder=True,
    )


def checkbox(pdf: canvas.Canvas, name: str, label: str, x: float, y: float, accent: colors.Color) -> None:
    pdf.acroForm.checkbox(
        name=name, tooltip=label, x=x, y=y - 2, size=13, buttonStyle="check",
        borderWidth=0.9, borderColor=accent, fillColor=colors.white,
        textColor=accent, checked=False, forceBorder=True,
    )
    pdf.setFont("Workbook", 10)
    pdf.setFillColor(INK)
    pdf.drawString(x + 20, y, label)


def create_workbook(key: str, source: Path) -> tuple[Path, int]:
    title, _subtitle, sections = chapter_data(source)
    target = OUTPUT / (source.stem + ".pdf")
    accent = ACCENTS.get(key.split("-")[0], ACCENTS["mathe"])
    pdf = canvas.Canvas(str(target), pagesize=A4, pageCompression=1)
    pdf.setTitle("Unterrichtsheft - " + title)
    pdf.setAuthor("Lernportal Fachwirt für Logistiksysteme")
    total = len(sections) + 1

    frame(pdf, accent, title, 1, total)
    pdf.setFillColor(accent)
    pdf.setFont("Workbook-Bold", 10)
    pdf.drawString(MARGIN, 716, "KAPITELHEFT")
    draw_lines(pdf, title, MARGIN, 682, TEXT_W, 24, 30, "Workbook-Bold", INK, 2)
    pdf.setFillColor(PALE)
    pdf.roundRect(MARGIN, 552, TEXT_W, 62, 8, stroke=0, fill=1)
    draw_lines(pdf, f"{len(sections)} Abschnitte - pro Abschnitt eine eigene Notizseite.", MARGIN + 14, 591, TEXT_W - 28, 11, 16, "Workbook-Bold", INK, 1)
    draw_lines(pdf, "Schreibe im Unterricht mit. Danach beantworte die Fragen ohne Vorlage und markiere, was du erklären kannst.", MARGIN + 14, 573, TEXT_W - 28, 9.5, 13, "Workbook", MUTED, 2)

    pdf.setFont("Workbook-Bold", 11)
    pdf.setFillColor(INK)
    pdf.drawString(MARGIN, 524, "Datum / Kursabend")
    field(pdf, "unterricht_datum", "Unterrichtsdatum", MARGIN, 486, TEXT_W, 29, False)
    pdf.drawString(MARGIN, 460, "Was weiß ich schon? Ein Beispiel aus meinem Betrieb")
    field(pdf, "vorwissen", "Vorwissen und Praxisbeispiel", MARGIN, 299, TEXT_W, 150)
    pdf.drawString(MARGIN, 273, "Meine Fragen für den Unterricht")
    field(pdf, "meine_fragen", "Fragen für den Unterricht", MARGIN, 91, TEXT_W, 171)
    pdf.showPage()

    for index, (group, heading, summary, questions) in enumerate(sections, 1):
        frame(pdf, accent, title, index + 1, total)
        pdf.setFont("Workbook-Bold", 9)
        pdf.setFillColor(accent)
        pdf.drawString(MARGIN, 738, cleaned(group).upper()[:90])
        draw_lines(pdf, heading, MARGIN, 716, TEXT_W, 20, 26, "Workbook-Bold", INK, 3)
        pdf.setFont("Workbook", 9)
        pdf.setFillColor(MUTED)
        pdf.drawString(MARGIN, 632, f"Abschnitt {index} von {len(sections)}")
        pdf.setFont("Workbook-Bold", 10)
        pdf.setFillColor(accent)
        pdf.drawString(MARGIN, 611, "KERNIDEE ZUM NACHLESEN")
        draw_lines(pdf, summary, MARGIN, 592, TEXT_W, 9.5, 13, "Workbook", MUTED, 5)
        pdf.setFont("Workbook-Bold", 10)
        pdf.setFillColor(accent)
        pdf.drawString(MARGIN, 522, "FRAGEN OHNE VORLAGE")
        qy = 502
        for number, question in enumerate(questions, 1):
            qy = draw_lines(pdf, f"{number}. {question}", MARGIN, qy, TEXT_W, 10, 14, "Workbook", INK, 3) - 7
        pdf.setFont("Workbook-Bold", 10)
        pdf.setFillColor(accent)
        pdf.drawString(MARGIN, 400, "MEINE NOTIZEN UND EIN EIGENES BEISPIEL")
        field(pdf, f"notiz_{index:02d}", "Notizen zu " + heading, MARGIN, 164, TEXT_W, 222)
        checkbox(pdf, f"besprochen_{index:02d}", "Im Unterricht besprochen", MARGIN, 121, accent)
        checkbox(pdf, f"erklaerbar_{index:02d}", "Ich kann es erklären", MARGIN + 260, 121, accent)
        pdf.showPage()

    pdf.save()
    reader = PdfReader(target)
    fields = reader.get_fields() or {}
    expected = 3 + len(sections) * 3
    if len(reader.pages) != total or len(fields) != expected:
        raise AssertionError(f"Fehler im Formular {target.name}: {len(reader.pages)} Seiten, {len(fields)} Felder statt {total}/{expected}")
    widgets = 0
    for page in reader.pages:
        for reference in page.get("/Annots", []):
            widget = reference.get_object()
            if widget.get("/Subtype") != "/Widget":
                continue
            widgets += 1
            if not widget.get("/AP") or not widget["/AP"].get("/N"):
                raise AssertionError(f"Darstellung eines Formularfeldes fehlt in {target.name}")
    if widgets != expected:
        raise AssertionError(f"Widgets fehlen in {target.name}: {widgets} statt {expected}")
    return target, len(sections)


def main() -> None:
    register_fonts()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    chapters = chapter_files()
    if len(chapters) != 17:
        raise AssertionError(f"Erwartet: 17 neue Kapitelhefte; gefunden: {len(chapters)}")
    for key, path in chapters:
        target, count = create_workbook(key, path)
        print(f"{target.name}: {count} Abschnitte, {count + 1} Seiten")


if __name__ == "__main__":
    main()
