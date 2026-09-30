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
| `assets/audio/` | kurze Hörfolgen, Gespräche zu allen 18 Lernkapiteln, Vertiefungen und drei Lernfahrten |
| `assets/hefte/` | ausfüllbare Unterrichtshefte als PDF zu allen 18 Lernkapiteln |
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
* **Hörfolgen** – alle Lernkapitel haben einen oder mehrere Teile mit zwei KI-Stimmen. Besonders dichte Kapitel haben zusätzliche Gespräche zum Vertiefen. Im Player kannst du die MP3 herunterladen oder den Text lesen und als PDF sichern. Drei Lernfahrten bündeln Folgen für unterwegs und bieten einzelne Kapitel als Sprungmarken.
* **Lernheft** – jedes Lernkapitel hat ein ausfüllbares PDF mit kurzer Kernaussage, Abruffragen und Notizfeld pro Abschnitt. Das Heft herunterladen, in einer PDF-App ausfüllen und lokal speichern. Mit **Volltext drucken / als PDF** kannst du zusätzlich das ausführliche Kapitel aus dem Browser drucken. Die Notizen in der Website bleiben getrennt vom ausfüllbaren Heft.

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

Jede Folge hat ein Manuskript unter `podcasts/manuskripte/` und eine zugeordnete MP3 unter `assets/audio/`. Die älteren kurzen MP3s verwenden die KI-generierte Stimme Microsoft Katja Neural. Die neuen Kapitelgespräche, Kurzchecks und Vertiefungen verwenden die ElevenLabs-Stimmen Susi und Christian Plasa. `lernfahrt.html`, `lernfahrt-2.html` und `lernfahrt-3.html` bündeln die Gespräche; alle Folgen bleiben einzeln in den Kapiteln erreichbar. Manuskripte können vor einer Neuaufnahme als Textdateien bearbeitet werden.

Zur Neuerzeugung der MP3s `edge-tts` und `imageio-ffmpeg` installieren, dann `python tools/generate_podcasts.py FOLGENNAME --force` ausführen. Anschließend die Dauer beim Kapitel in `KAPITEL_LISTE` aktualisieren und `python pruefen.py` laufen lassen. Für mehrere Folgen `audios: [{ titel, datei, dauer }, ...]` verwenden. Die bestehenden Felder `audio` und `audioDauer` bleiben für ältere Einzelfolgen gültig. Quellen und redaktionelle Regeln stehen in `podcasts/QUELLEN.md`.

Gesprächsmanuskripte beginnen mit `Gesprächsfolge:`. Jeder weitere Absatz beginnt mit `Mara:` oder `Jonas:`; `PAUSE: 3` fügt eine Denkpause ein. Mit `python tools/generate_dialogue_podcasts.py gespraech-plab-1-logistikstruktur --force` wird die MP3 aus den beiden Stimmen neu erzeugt. Das Skript speichert Zwischenstücke im ignorierten Ordner `.podcast-build/gespraeche/`. Die Stimmen sind synthetisch und bilden keine reale Person nach.

Alternativ kann `tools/generate_elevenlabs_dialogue.py` dasselbe Gespräch mit zwei ElevenLabs-Stimmen und dem Dialogmodell Eleven v4 aufnehmen. `python tools/generate_elevenlabs_dialogue.py --dry-run` zeigt die benötigten Abschnitte und Textzeichen ohne API-Anfrage. Für die Aufnahme wird ein eigener ElevenLabs-API-Schlüssel als lokale Umgebungsvariable `ELEVENLABS_API_KEY` oder als reine Textdatei unter `~/.codex/elevenlabs.key.txt` außerhalb des Repositories benötigt. Dazu kommen je eine deutschsprachige `voice_id` für Mara und Jonas: `python tools/generate_elevenlabs_dialogue.py --female-voice ID --male-voice ID`. Das Skript prüft vor kostenpflichtigen Anfragen die verfügbaren Credits, speichert Zwischenstücke nur im ignorierten Build-Ordner und erzeugt eine neue MP3 mit dem Zusatz `-elevenlabs`. Erst nach Hörprüfung wird diese Datei im Portal verlinkt. Schlüssel niemals in Dateien des öffentlichen Repositories eintragen.

Mit `--sample` werden nur vier Sprecherbeiträge als lokale Hörprobe erzeugt. Eine abweichende private Schlüsseldatei kann mit `--key-file PFAD` angegeben werden; die Datei muss den vollständigen Schlüssel enthalten, nicht nur die im Dashboard sichtbare Key-ID. Für die neuen Gesprächsfolgen sprechen die ElevenLabs-Stimmen **Susi – Effortless and Confident** (`v3V1d2rk6528UrLKRuy8`) und **Christian Plasa – Soft and Mild** (`z1EhmmPwF0ENGYE8dBE6`). Die gespeicherte Christian-Plasa-Stimme stammt aus der ElevenLabs Voice Library; es wird keine eigene Stimmkopie erstellt. Vor jeder weiteren Aufnahme Guthaben und Stimmensatz prüfen. Nach den Einzelaufnahmen bündelt zum Beispiel `python tools/build_lernfahrt.py --fahrt 3` die jeweiligen Folgen mit Kapitelmarken. Die Einzel-MP3s bleiben für gezieltes Wiederholen verfügbar.

Für Resemble AI gibt es `tools/generate_resemble_dialogue.py`. Die vorgewählten deutschen Stimmen heißen Anita und Ulrich; ihre IDs können per `--mara-voice` und `--jonas-voice` geändert werden. `python tools/generate_resemble_dialogue.py --dry-run` plant eine lokale Hörprobe mit sechs Sprecherbeiträgen. Mit `--key-file PFAD` liest das Skript den Schlüssel aus einer privaten Datei **außerhalb** des Repositories. Es prüft das verfügbare Guthaben, bevor es Sprachabschnitte erzeugt. `--full` nimmt die ganze Folge auf; die Resemble-MP3 wird erst nach Hörprüfung im Portal verlinkt. Zwischendateien und die Hörprobe liegen im ignorierten Ordner `.podcast-build/resemble/`.

Die 17 weiteren ausfüllbaren Hefte werden mit `python tools/generate_workbooks.py` aus den Kapitelüberschriften, Kernaussagen und Selbstabfragen des Portals erzeugt. Dafür werden `lxml`, `reportlab` und `pypdf` benötigt. Die PDF-Dateien liegen unter `assets/hefte/` und sind in `KAPITEL_LISTE` beim jeweiligen Kapitel verlinkt. Die bisherige PDF zu Kapitel 1.1 bleibt erhalten.
