# Bauanleitung Lernportal – Fachwirt für Logistiksysteme

Verbindliches Regelwerk. Wer ein Kapitel neu baut oder aktualisiert, hält sich exakt daran.
Sonst brechen Notizen, Lernstand und Navigation.

---

## 1. Was dieses Portal leisten soll

Gabriel startet fachlich bei null. Das Skript muss **lehren**, nicht nur **auflisten**.
Ein Kapitel ist erst fertig, wenn jemand ohne Vorwissen es allein lesen und danach erklären kann.

Fünf Prinzipien, die in jedem Abschnitt sichtbar sein müssen:

1. **Vom Konkreten zum Abstrakten.** Erst die Situation aus der Praxis, dann der Fachbegriff – nie umgekehrt.
2. **Jeder Fachbegriff wird bei seiner ersten Nennung erklärt.** Kein „Kommissionierung“ ohne Erklärung, was das ist.
3. **Warum vor Was.** Welches Problem löst dieses Konzept? Ohne diese Antwort bleibt es auswendig gelernt.
4. **Active Recall.** Jeder Abschnitt endet mit Selbstabfragen (`details.abfrage`) – daraus baut die Engine Karteikarten.
5. **Abgrenzung.** Wo verwechselt man es? Der `.achtung`-Block ist Pflicht, wenn es eine typische Verwechslung gibt.

**Ton:** Du-Form, kurze Sätze, keine Werbesprache, keine Emojis im Fließtext.
**Herkunft:** Inhalte kommen aus den Dozentenquellen in `quellen/`. Nichts erfinden. Was das Portal
ergänzt (Beispiele, Erklärungen, Einordnung), muss fachlich korrekt sein und darf der Quelle nicht widersprechen.
Wo eine Quelle unklar ist: `.achtung`-Block mit dem Hinweis „im Unterricht nachfragen“.

---

## 2. Dateien

```
index.html                     Startseite (Fortschritt, Lernplan, Prüfungsinfos)
notizen.html                   Notizzentrale (Suche, Sicherung, Altnotizen)
assets/portal.css              Designsystem – wird nie in einer Kapiteldatei überschrieben
assets/portal.js               Engine – Navigation, Notizen, Status, Quiz, Karteikarten
<kapiteldatei>.html            je ein Kapitel, flach im Wurzelverzeichnis
quellen/*.txt                  extrahierte Dozentenquellen (nicht veröffentlichen)
```

Kapiteldateien und IDs stehen in `assets/portal.js` in `KAPITEL_LISTE`.
**Ein neues Kapitel existiert erst, wenn es dort eingetragen ist.**

---

## 3. Gerüst einer Kapiteldatei

```html
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kapitel 0 · Einführung in die Logistik</title>
<link rel="stylesheet" href="assets/portal.css">
</head>
<body class="mit-sidebar">

<aside class="sidebar"></aside>          <!-- leer lassen, die Engine füllt sie -->

<main class="inhalt">

  <div class="kopf-label">Raphael Kroul · Kapitel 0 · Stand 03.03.2026</div>
  <h1>Einführung in die Logistik</h1>
  <p class="kopf-sub">Ein Satz, der sagt, was man nach dem Kapitel kann.</p>

  <section class="abschnitt" id="was-ist-logistik" data-gruppe="Grundlagen">
    <div class="ab-kopf"><h2><span class="ab-nr">0.1</span>Was Logistik überhaupt ist</h2></div>
    ... Inhalt ...
  </section>

</main>

<script>window.KAPITEL = {id:'kroul-0', fach:'kroul', nummer:'Kapitel 0', titel:'Einführung in die Logistik'};</script>
<script src="assets/portal.js" defer></script>
</body>
</html>
```

Nicht selbst bauen – die Engine erledigt das: Sidebar-Navigation, Statusknöpfe, Notizfelder,
Fortschrittsbalken, aktiver Navigationspunkt, Quizauswertung, Lösungsknöpfe, Karteikarten,
Dunkelmodus, Druckansicht.

`fach` ist eines von: `plab`, `gruber`, `kroul`, `gruchala`, `werkzeug`.

---

## 4. Abschnitte

Ein `section.abschnitt` = **eine Unterrichtseinheit**, die man am Stück lernt.
Faustregel: 400–900 Wörter. Zu große Abschnitte machen den Lernstand wertlos, zu kleine die Navigation unbrauchbar.

```html
<section class="abschnitt" id="sieben-r" data-gruppe="Grundbegriffe">
  <div class="ab-kopf"><h2><span class="ab-nr">0.4</span>Die 7 R der Logistik</h2></div>
  ...
</section>
```

* `id` — **kleingeschrieben, mit Bindestrichen, sprechend, dauerhaft.** Sie ist der Anker für
  Lernstand, Notizen und Links. **Eine einmal veröffentlichte `id` wird nie geändert und nie neu vergeben.**
* `data-gruppe` — Überschrift in der Sidebar. Gleicher Text = gleiche Gruppe. Nur beim ersten
  Abschnitt einer Gruppe nötig, schadet aber nicht, wenn er überall steht.
* `.ab-nr` — Gliederungsnummer aus dem Dozentenskript, damit man im Unterricht mitkommt.

### Empfohlener Aufbau innerhalb eines Abschnitts

1. `.block.lernziel` – „Nach diesem Abschnitt kannst du …“ (2–4 Stichpunkte)
2. `.block.einstieg` – die konkrete Situation / das Problem, in Alltagssprache
3. Fließtext mit `h3`-Zwischenüberschriften, der Schritt für Schritt erklärt
4. `.block.def` für jeden Fachbegriff, `.block.beispiel` für den Praxisfall
5. `.block.achtung` bei typischen Verwechslungen, `.block.merk` für das, was sitzen muss
6. `.block.pruefung` – wie das in der IHK-Prüfung abgefragt wird
7. `.abfrage-liste` mit 3–6 Selbstabfragen (Pflicht)

---

## 5. Notizen – die wichtigste Regel

Jeder Abschnitt bekommt **automatisch** ein Notizfeld. Zusätzlich bekommt jedes Element mit
`data-notiz="slug"` ein eigenes:

```html
<div class="block def" data-notiz="def-logistik">…</div>
<div class="tab"  data-notiz="tab-xpl-stufen">…</div>
```

**Regeln für `slug`:**

* sprechend, kleingeschrieben, mit Bindestrichen: `def-logistik`, `tab-incoterms`, `bsp-schokolade`
* **innerhalb einer Kapiteldatei eindeutig**
* **niemals** eine laufende Nummer (`0`, `1`, `2`) — genau daran ist die Vorgängerversion gescheitert
* **niemals nachträglich ändern**, sonst ist die daran hängende Notiz verwaist
* Wird ein Block gelöscht, bleibt sein Slug für immer verbrannt und wird nicht neu vergeben

Speicherort: `lp.notiz.<kapitelId>.<slug>`, Zeitstempel unter `lp.notizmeta.…`.

Faustregel für die Dichte: **jeder Definitions-, Tabellen-, Beispiel-, Merk-, Prüfungs- und
Aufgabenblock bekommt ein `data-notiz`.** Fließtextabsätze nicht – dafür gibt es das Abschnittsfeld.

---

## 6. Bausteine (Klassen aus `portal.css`)

```html
<!-- Lernziel -->
<div class="block lernziel" data-notiz="ziel-scm">
  <div class="b-label">Nach diesem Abschnitt kannst du</div>
  <ul><li>…</li></ul>
</div>

<!-- Einstieg: konkrete Situation zuerst -->
<div class="block einstieg" data-notiz="ein-scm">
  <div class="b-label">Worum es geht</div>
  <p>…</p>
</div>

<!-- Definition -->
<div class="block def" data-notiz="def-scm">
  <div class="b-label">Definition</div>
  <div class="b-term">Supply Chain Management</div>
  <p>…</p>
</div>

<!-- Merksatz / Beispiel / Achtung / Prüfung -->
<div class="block merk"     data-notiz="merk-tul"><div class="b-label">Merksatz</div><p>…</p></div>
<div class="block beispiel" data-notiz="bsp-tul"><div class="b-label">Beispiel aus der Praxis</div><p>…</p></div>
<div class="block achtung"  data-notiz="ach-tul"><div class="b-label">Typische Verwechslung</div><p>…</p></div>
<div class="block pruefung" data-notiz="pru-tul"><div class="b-label">So kommt das in der Prüfung</div><p>…</p></div>

<!-- Vertiefung, ausklappbar -->
<details class="vertiefung"><summary>Warum ist das so?</summary><p>…</p></details>

<!-- Tabelle -->
<div class="tab" data-notiz="tab-xpl">
  <table>
    <thead><tr><th>Stufe</th><th>Aufgabe</th></tr></thead>
    <tbody><tr><td>1PL</td><td>…</td></tr></tbody>
  </table>
</div>

<!-- Kartenraster -->
<div class="raster">
  <div class="karte blue"><div class="k-titel">Richtiges Gut</div><div class="k-text">…</div></div>
</div>

<!-- Phasenkette -->
<div class="phasen" data-notiz="phasen-lewin">
  <div class="phase"><div class="p-nr">Phase 1</div><div class="p-name">Unfreezing</div><div class="p-text">…</div></div>
</div>

<!-- Formel -->
<div class="formel" data-notiz="formel-andler">
  <div class="formel-kopf"><span class="f-tag">Formel</span><span class="f-name">Andlersche Formel</span></div>
  <div class="formel-koerper">
    <div class="eq">x_opt = √( 2 × Jahresbedarf × Bestellkosten ÷ (Einstandspreis × Lagerkostensatz) )</div>
    <div class="f-erklaerung">…</div>
  </div>
</div>

<!-- Rechenweg -->
<div class="schritte" data-notiz="rechnung-andler">
  <div class="schritt"><div class="s-nr">1</div><div class="s-txt">Zähler: 2 × 80.000 × 180 = 28.800.000</div></div>
  <div class="s-warum">Erst alles über dem Bruchstrich.</div>
  <div class="schritt fertig"><div class="s-nr">✓</div><div class="s-txt">√16.000.000 = 4.000 Stück</div></div>
</div>

<!-- Selbstabfrage: Pflicht am Abschnittsende, wird zur Karteikarte -->
<div class="abfrage-liste">
  <div class="abfrage-kopf">Selbstabfrage</div>
  <details class="abfrage">
    <summary>Was unterscheidet 3PL von 4PL?</summary>
    <div class="antwort"><p>…</p></div>
  </details>
</div>

<!-- Aufgabe mit Lösung -->
<div class="aufgabe" data-notiz="aufg-pdca-lager">
  <div class="aufgabe-kopf"><span class="tag">Aufgabe</span>PDCA im Lager<span class="punkte">10 Pkt.</span></div>
  <div class="aufgabe-text"><p>…</p></div>
  <button class="loesung-btn"></button>
  <div class="loesung"><p>…</p></div>
</div>

<!-- Quiz -->
<div class="quiz">
  <div class="q-block">
    <div class="q-nr"></div>
    <div class="q-frage">…</div>
    <div class="q-optionen">
      <button class="q-opt" data-richtig="false">A) …</button>
      <button class="q-opt" data-richtig="true">B) …</button>
    </div>
    <div class="q-fb" data-erklaerung="Warum B richtig ist …"></div>
  </div>
  <div class="q-score"><div class="z"></div><div class="t"></div></div>
</div>
```

Merke: `.q-nr` leer lassen (Engine nummeriert), `.loesung-btn` ohne Text lassen (Engine beschriftet),
Quiz-Feedback steht in `data-erklaerung`, nie im Elementtext.

---

## 7. Workflow für künftige Unterrichtsstunden

**Fall A – ein bestehendes Skript wurde im Unterricht erweitert**
1. Betroffenes Kapitel und die geänderten Stellen bestimmen.
2. Neue Inhalte **ergänzen**, vorhandene Abschnitts-`id`s und `data-notiz`-Slugs **unverändert lassen**.
3. Neue Abschnitte bekommen neue, sprechende `id`s. Reihenfolge darf sich ändern, IDs nicht.
4. `Stand`-Datum in `.kopf-label` aktualisieren.
5. Gabriel darauf hinweisen, welche Abschnitte neu sind.

**Fall B – ein ganz neues Skript kommt dazu**
1. Quelle nach `quellen/` extrahieren (`pdftotext -layout`, `python-docx`, `python-pptx`).
2. Gliederung bilden: 8–20 Abschnitte, an der Nummerierung des Dozenten orientiert.
3. Kapitel nach diesem Regelwerk bauen.
4. Eintrag in `KAPITEL_LISTE` in `assets/portal.js` ergänzen (`id`, `datei`, `fach`, `nummer`, `titel`, `desc`).
5. Prüfen: `id`s eindeutig, Slugs eindeutig, Quizantworten korrekt, Links gültig.

**Fall C – ein Kapitel wird inhaltlich umgebaut**
Slugs, die es weiter gibt, bleiben. Entfallene Slugs werden nicht wiederverwendet.
Gabriel bekommt eine Liste der entfallenen Slugs, damit er die zugehörigen Notizen retten kann.

**Immer am Ende:** `pruefen.py` laufen lassen (prüft doppelte IDs/Slugs, tote Links,
fehlende Selbstabfragen, Quizfragen ohne richtige Antwort).

---

## 8. Was ausdrücklich verboten ist

* eigene `<style>`-Blöcke in Kapiteldateien, die `portal.css` überschreiben
  (seitenspezifische Ergänzungen sind erlaubt, aber nur für Dinge, die es im Designsystem nicht gibt)
* eigene Notiz-, Status- oder Quiz-Logik in einer Kapiteldatei
* `localStorage`-Schlüssel außerhalb des Präfixes `lp.`
* Zahlen-Slugs, Positions-IDs, `data-notiz="3"`
* Sidebar-Navigation von Hand schreiben
* Inhalte, die nicht durch die Dozentenquellen gedeckt sind, ohne Kennzeichnung
