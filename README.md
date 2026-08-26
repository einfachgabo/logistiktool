# Lernportal – Fachwirt für Logistiksysteme

Persönliches Lernskript für die IHK-Fortbildung. Reine statische Website, läuft ohne Server
direkt über GitHub Pages.

## Was drin ist

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite: Fortschritt je Fach, aktueller Unterrichtsstand, Lernplan, Prüfungsinfos |
| `plab-1` … `plab-3` | Benedikt Plab – Logistikstruktur, Logistiksysteme, Logistische Abläufe |
| `gruber-1` … `gruber-4` | Christian Gruber – Konzepte, Beschaffung, Lager/Distribution, Strategie & Projekte |
| `kroul-0`, `kroul-1` | Raphael Kroul – Einführung, Veränderungsprozesse |
| `gruchala-1` … `gruchala-5` | Kerstin Gruchala – Kommunikation, Personal, Arbeitsrecht, Führung, Ausbildung & Arbeitsschutz |
| `mathe-grundlagen.html` | Rechnen von Grund auf |
| `formelsammlung.html` | alle Formeln mit Bedeutung, Einheiten und Rechenweg |
| `aufgaben.html` | 45 Aufgaben mit Lösungsweg, inkl. zwei Prüfungssimulationen |
| `notizen.html` | alle Notizen an einem Ort, Suche, Sicherung |
| `assets/portal.css` | das gesamte Design |
| `assets/portal.js` | die Engine: Navigation, Notizen, Lernstand, Quiz, Karteikarten |

## Bedienung

* **📍 wir sind hier** – im Unterricht antippen. Die Startseite merkt sich die Stelle.
* **im Unterricht dran / verstanden / nochmal ansehen** – Status je Abschnitt. Daraus entsteht der Lernplan.
* **✏ Notiz** – an jedem Block. Speichert automatisch, bleibt bei Skript-Updates erhalten.
* **Taste K** – Karteikarten aus allen Selbstabfragen des Kapitels.
* **🌓** – Hell/Dunkel. **🖨** – Druck bzw. PDF, inklusive Notizen und Lösungen.

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
