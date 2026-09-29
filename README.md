# Lernportal – Fachwirt für Logistiksysteme

Persönliches Lernskript für die IHK-Fortbildung. Reine statische Website, läuft ohne Server
direkt über GitHub Pages.

## Was drin ist

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite: Fortschritt je Fach, aktueller Unterrichtsstand, Lernplan, Prüfungsinfos |
| `plab-1` … `plab-4` | Benedikt Plab – Logistikstruktur, Logistiksysteme, Logistische Abläufe, Leistungsfähigkeit & Strategie |
| `gruber-1` … `gruber-5` | Christian Gruber – Konzepte, Beschaffung, Lager/Distribution, Strategie & Projekte, Vergabe & Verträge |
| `kroul-0`, `kroul-1` | Raphael Kroul – Einführung, Veränderungsprozesse |
| `gruchala-1` … `gruchala-5` | Kerstin Gruchala – Kommunikation, Personal, Arbeitsrecht, Führung, Ausbildung & Arbeitsschutz |
| `mathe-grundlagen.html` | Rechnen von Grund auf |
| `formelsammlung.html` | alle Formeln mit Bedeutung, Einheiten und Rechenweg |
| `aufgaben.html` | 45 Aufgaben mit Lösungsweg, inkl. zwei Prüfungssimulationen |
| `notizen.html` | alle Notizen an einem Ort, Suche, Sicherung |
| `assets/portal.css` | das gesamte Design |
| `assets/portal.js` | die Engine: Navigation, Notizen, Lernstand, Quiz, Karteikarten |
| `assets/audio/` | 34 kurze Hörfolgen zu allen 18 Lernkapiteln und die bisherige Gesamtfolge |
| `assets/hefte/` | ausfüllbare Lernhefte als PDF; bisher Grundlagen und Kapitel 1.1 |
| `podcasts/manuskripte/` | bearbeitbare Texte der Hörfolgen |
| `podcasts/lesen.html` | lesefreundliche Ansicht der Manuskripte mit PDF-Druck |

## Bedienung

* **📍 wir sind hier** – im Unterricht antippen. Die Startseite merkt sich die Stelle.
* **im Unterricht dran / verstanden / nochmal ansehen** – Status je Abschnitt. Daraus entsteht der Lernplan.
* **✏ Notiz** – an jedem Block. Speichert automatisch, bleibt bei Skript-Updates erhalten.
* **Taste K** – Karteikarten aus allen Selbstabfragen des Kapitels.
* **🌓** – Hell/Dunkel. **🖨** – Druck bzw. PDF, inklusive Notizen und Lösungen.
* **Unterrichtsansicht** – zeigt Abschnittstitel, Status und das Notizfeld; der Volltext bleibt erreichbar.
* **5 Fragen üben** – Antworten erst selbst abrufen. Nach der Selbsteinschätzung erscheinen Karten nach 1, 3, 7, 14, 30 oder 60 Tagen wieder. Diese Abstände sind eine praktische Voreinstellung.
* **Hörfolgen** – alle Lernkapitel haben einen oder mehrere kurze Teile. Im Player kannst du die MP3 herunterladen oder den Text lesen und als PDF sichern.
* **Lernheft** – die PDF-Datei aus dem Kapitel herunterladen, in einer PDF-App ausfüllen und lokal speichern. Die Notizen in der Website bleiben getrennt davon.

## Wichtig: Notizen sichern

Notizen und Lernstände liegen im `localStorage` des jeweiligen Browsers – also nur auf dem
Gerät, auf dem du sie geschrieben hast. Einmal pro Woche über `notizen.html` →
**„Sicherung herunterladen"** eine JSON-Datei ziehen. Auf einem neuen Gerät oder nach dem
Leeren des Browser-Speichers dort wieder einlesen.

## Skripte aktualisieren

Regelwerk steht in `BAUANLEITUNG.md`. Kurzfassung:

* Abschnitts-IDs und `data-notiz`-Slugs sind **dauerhaft** – wer sie ändert, kappt die daran
  hängenden Notizen.
* Neue Kapitel müssen in `assets/portal.js` in `KAPITEL_LISTE` eingetragen werden.
* Nach jeder Änderung `python3 pruefen.py` laufen lassen: prüft doppelte IDs und Slugs, tote
  Links, fehlende Selbstabfragen und Quizfragen ohne richtige Antwort.

## Nicht ins Repository

Die extrahierten Dozentenunterlagen (`quellen/`) gehören nicht in ein öffentliches
Repository – sie sind Material des Bildungsträgers. Die `.gitignore` schließt sie aus.

## Lernmethode und Podcasts

Das Portal nutzt kurze Selbsttests und zeitlich verteilte Wiederholungen. Die Auswahl stützt sich auf Forschung zu [Testeffekten](https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.2006.01693.x/) und [verteiltem Üben](https://pubmed.ncbi.nlm.nih.gov/16719566/). Podcasts sind eine Ergänzung für unterwegs; sie ersetzen weder Abruffragen noch Fallaufgaben.

Jede Folge hat ein eigenes Manuskript unter `podcasts/manuskripte/` und eine gleichnamige MP3 unter `assets/audio/`. Die MP3s verwenden die KI-generierte Stimme Microsoft Katja Neural. Die neuen Folgen dauern meist drei bis vier Minuten und enthalten ein Praxisbeispiel und zwei Abruffragen. Für breite Kapitel gibt es mehrere Teile. Auch Kapitel 1.1 liegt in drei kurzen Teilen vor; die bisherige Gesamtfolge bleibt erhalten. Die Manuskripte können vor einer Neuaufnahme direkt als Textdatei bearbeitet werden.

Zur Neuerzeugung der MP3s `edge-tts` und `imageio-ffmpeg` installieren, dann `python tools/generate_podcasts.py FOLGENNAME --force` ausführen. Anschließend die Dauer beim Kapitel in `KAPITEL_LISTE` aktualisieren und `python pruefen.py` laufen lassen. Für mehrere Folgen `audios: [{ titel, datei, dauer }, ...]` verwenden. Die bestehenden Felder `audio` und `audioDauer` bleiben für ältere Einzelfolgen gültig. Quellen und redaktionelle Regeln stehen in `podcasts/QUELLEN.md`.
