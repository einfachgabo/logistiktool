#!/usr/bin/env python3
"""Prüft alle Kapiteldateien des Lernportals auf die Regeln aus BAUANLEITUNG.md."""
import os, re, sys, glob, json

ROOT = os.path.dirname(os.path.abspath(__file__))
fehler, warnungen = [], []

def f(datei, text): fehler.append(f"{datei}: {text}")
def w(datei, text): warnungen.append(f"{datei}: {text}")

# ---- Kapitelliste aus portal.js lesen -------------------------------------
js = open(os.path.join(ROOT, 'assets', 'portal.js'), encoding='utf-8').read()
block = re.search(r'var KAPITEL_LISTE = \[(.*?)\n  \];', js, re.S)
registriert = {}
if not block:
    f('assets/portal.js', 'KAPITEL_LISTE nicht gefunden')
else:
    for m in re.finditer(r"\{\s*id:\s*'([^']+)'.*?datei:\s*'([^']+)'", block.group(1), re.S):
        registriert[m.group(1)] = m.group(2)

seiten = sorted(p for p in glob.glob(os.path.join(ROOT, '*.html')))
alle_dateien = {os.path.basename(p) for p in seiten}

# ---- Registrierte Dateien vorhanden? --------------------------------------
for kid, datei in registriert.items():
    if datei not in alle_dateien:
        f('assets/portal.js', f"Kapitel '{kid}' verweist auf fehlende Datei {datei}")

kapitel_gefunden = {}

for pfad in seiten:
    name = os.path.basename(pfad)
    html = open(pfad, encoding='utf-8').read()

    # --- Links prüfen ---
    for href in re.findall(r'href="([^"#?]+\.html)[^"]*"', html):
        if href not in alle_dateien:
            f(name, f'toter Link auf {href}')
    for src in re.findall(r'(?:src|href)="(assets/[^"]+)"', html):
        if not os.path.exists(os.path.join(ROOT, src)):
            f(name, f'fehlende Datei {src}')

    if 'window.KAPITEL' not in html:
        continue  # index.html, notizen.html

    kid = re.search(r"window\.KAPITEL\s*=\s*\{[^}]*id:\s*'([^']+)'", html)
    if not kid:
        f(name, 'window.KAPITEL ohne id')
        continue
    kid = kid.group(1)
    kapitel_gefunden[kid] = name

    if kid not in registriert:
        f(name, f"Kapitel-ID '{kid}' fehlt in KAPITEL_LISTE (assets/portal.js)")
    elif registriert[kid] != name:
        f(name, f"KAPITEL_LISTE erwartet Datei '{registriert[kid]}' für '{kid}'")

    # --- Pflichtstruktur ---
    if 'assets/portal.css' not in html: f(name, 'portal.css nicht eingebunden')
    if 'assets/portal.js' not in html:  f(name, 'portal.js nicht eingebunden')
    if 'class="mit-sidebar"' not in html: f(name, 'body ohne class="mit-sidebar"')
    if not re.search(r'<aside class="sidebar">\s*</aside>', html): f(name, 'leeres <aside class="sidebar"></aside> fehlt')
    if re.search(r'<style[^>]*>', html) and 'seitenspezifisch' not in html:
        w(name, 'eigener <style>-Block – nur erlaubt, wenn das Designsystem es nicht abdeckt')
    for verboten in ['localStorage', 'function toggleNotiz', 'notizen.js']:
        if verboten in html: f(name, f'verbotene Eigenlogik: {verboten}')

    # --- Abschnitte ---
    abschnitte = re.findall(r'<section class="abschnitt"([^>]*)>', html)
    if not abschnitte:
        f(name, 'keine section.abschnitt gefunden')
    ids = []
    for attr in abschnitte:
        m = re.search(r'id="([^"]+)"', attr)
        if not m: f(name, 'section.abschnitt ohne id'); continue
        ids.append(m.group(1))
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', m.group(1)):
            f(name, f'Abschnitts-ID "{m.group(1)}" verletzt die Namensregel (klein, Bindestriche)')
        if 'data-gruppe=' not in attr:
            w(name, f'Abschnitt "{m.group(1)}" ohne data-gruppe – landet ohne Überschrift in der Navigation')
    for i in set(ids):
        if ids.count(i) > 1: f(name, f'Abschnitts-ID "{i}" mehrfach vergeben')

    # jeder Abschnitt braucht .ab-kopf und eine Selbstabfrage
    for teil in re.split(r'(?=<section class="abschnitt")', html)[1:]:
        sid = re.search(r'id="([^"]+)"', teil)
        sid = sid.group(1) if sid else '?'
        if 'class="ab-kopf"' not in teil: f(name, f'Abschnitt "{sid}" ohne .ab-kopf')
        if 'abfrage-liste' not in teil and 'class="quiz"' not in teil:
            w(name, f'Abschnitt "{sid}" ohne Selbstabfrage')

    # --- Notiz-Slugs ---
    slugs = re.findall(r'data-notiz="([^"]+)"', html)
    for s in set(slugs):
        if slugs.count(s) > 1: f(name, f'data-notiz "{s}" mehrfach vergeben')
    for s in slugs:
        if re.fullmatch(r'\d+', s): f(name, f'data-notiz "{s}" ist eine reine Zahl – verboten')
        elif not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', s): f(name, f'data-notiz "{s}" verletzt die Namensregel')
    if len(slugs) < len(ids):
        w(name, f'nur {len(slugs)} Notiz-Anker bei {len(ids)} Abschnitten – zu wenig Notizmöglichkeiten')

    # --- Quiz ---
    for i, q in enumerate(re.findall(r'<div class="q-block">(.*?)</div>\s*</div>', html, re.S), 1):
        if 'data-richtig="true"' not in q: f(name, f'Quizfrage {i} ohne richtige Antwort')
        if q.count('data-richtig="true"') > 1: f(name, f'Quizfrage {i} hat mehrere richtige Antworten')
    for fb in re.findall(r'<div class="q-fb"([^>]*)>', html):
        if 'data-erklaerung' not in fb: w(name, 'Quiz-Feedback ohne data-erklaerung')

    # --- Aufgaben ---
    for auf in re.findall(r'<div class="aufgabe"(.*?)<!--/aufgabe-->|<div class="aufgabe"[^>]*>(.*?)</div>\s*(?=<)', html, re.S):
        pass
    n_btn, n_los = html.count('class="loesung-btn"'), html.count('class="loesung"')
    if n_btn != n_los: w(name, f'{n_btn} Lösungsknöpfe, aber {n_los} Lösungsblöcke')

# ---- registrierte Kapitel ohne Datei --------------------------------------
for kid in registriert:
    if kid not in kapitel_gefunden:
        w('assets/portal.js', f"Kapitel '{kid}' ist registriert, aber die Seite fehlt noch")

print('=' * 64)
print(f'Geprüft: {len(seiten)} Seiten, {len(kapitel_gefunden)} Kapitel')
print('=' * 64)
if fehler:
    print(f'\nFEHLER ({len(fehler)}):')
    for x in fehler: print('  ✗', x)
if warnungen:
    print(f'\nHinweise ({len(warnungen)}):')
    for x in warnungen: print('  •', x)
if not fehler and not warnungen:
    print('\nAlles in Ordnung.')
sys.exit(1 if fehler else 0)
