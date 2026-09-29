"""Teile die ursprüngliche Folge zu Kapitel 1.1 in kurze Themenfolgen."""

import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
source = root / "podcasts" / "manuskripte" / "plab-1-logistikstruktur.txt"
paragraphs = [part.strip() for part in re.split(r"\n\s*\n", source.read_text(encoding="utf-8-sig")) if part.strip()]

episodes = [
    (
        "plab-1-a-grundlagen",
        "Kapitel 1.1, Teil eins. Grundlagen und Zielkonflikte.",
        paragraphs[1:6],
        "Zwei Fragen für dich. Welche fünf richtigen Größen gehören zur Logistikaufgabe? Und warum kann ein günstiger Einkaufspreis insgesamt teuer werden? Pausiere und antworte mit einem eigenen Beispiel.",
    ),
    (
        "plab-1-b-prozesse",
        "Kapitel 1.1, Teil zwei. Prozesse und Leistung.",
        paragraphs[6:12],
        "Zwei Fragen für dich. Worin unterscheiden sich Effektivität und Effizienz? Und welche der vier Leistungsarten würdest du bei einer Verbesserung zuerst reduzieren? Pausiere und erkläre deine Antwort laut.",
    ),
    (
        "plab-1-c-lieferkette",
        "Kapitel 1.1, Teil drei. Lieferkette, Umfeld und Organisation.",
        paragraphs[12:20],
        "Zwei Fragen für dich. Wie kann eine kleine Nachfrageschwankung zum Bullwhip-Effekt werden? Und was unterscheidet Aufbauorganisation von Ablauforganisation? Pausiere und finde für beides ein Beispiel aus deinem Betrieb.",
    ),
]

for slug, title, body, questions in episodes:
    target = source.with_name(slug + ".txt")
    target.write_text("\n\n".join([title, *body, questions]) + "\n", encoding="utf-8")
    print(target.name)
