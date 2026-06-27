#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_scen.py : skleja czesci tygodniowe scenariuszy (src/_parts/scen-<lang>-w<n>.md)
w jeden spojny dokument src/scenariusze-blokow/<lang>.md.

Logika:
- usuwa pierwszy wiersz "# <tytul> - Tydzien N" z kazdej czesci,
- obniza wszystkie naglowki ATX o 1 poziom (## -> ###, ### -> ####),
- przed kazda czescia wstawia naglowek tygodnia "## <Tydzien N: modul>",
- na poczatku dokumentu daje "# <Tytul dokumentu>".
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTS = HERE / "src" / "_parts"
OUT = HERE / "src" / "scenariusze-blokow"

LANGS = ["pl", "en", "es"]

DOC_TITLE = {
    "pl": "Scenariusze blokow zajec",
    "en": "Lesson-block scenarios",
    "es": "Escenarios de los bloques de clase",
}
DOC_TITLE_DIAC = {  # poprawne diakrytyki w tytule (czesc PL z agenta moze byc bez)
    "pl": "Scenariusze bloków zajęć",
    "en": "Lesson-block scenarios",
    "es": "Escenarios de los bloques de clase",
}
WEEK_HEADERS = {
    "pl": {
        1: "Tydzień 1: Wprowadzenie, BHP i podstawy budowy",
        2: "Tydzień 2: Roboty ziemne, podbudowa i przygotowanie podłoża",
        3: "Tydzień 3: Układanie kostki brukowej (specjalizacja)",
        4: "Tydzień 4: Wykończenia, jakość, prace uzupełniające i zatrudnienie",
    },
    "en": {
        1: "Week 1: Introduction, OSH and construction basics",
        2: "Week 2: Earthworks, sub-base and ground preparation",
        3: "Week 3: Paving-stone laying (specialisation)",
        4: "Week 4: Finishing, quality, supplementary work and employment",
    },
    "es": {
        1: "Semana 1: Introducción, SST y fundamentos de construcción",
        2: "Semana 2: Movimiento de tierras, base y preparación del terreno",
        3: "Semana 3: Colocación de adoquines (especialidad)",
        4: "Semana 4: Acabados, calidad, trabajos complementarios y empleo",
    },
}
INTRO = {
    "pl": "Dokument zawiera szczegółowe scenariusze 20 bloków zajęć (po 5 na każdy z 4 tygodni). Każdy dzień opisano jednolicie: cele, materiały i środki ochrony, zagadnienia BHP, przebieg zajęć z podziałem czasu, metody, sposób oceny, kluczowe słownictwo oraz wskazówki dla trenera pracującego z grupą wielojęzyczną.",
    "en": "This document contains detailed scenarios for 20 lesson blocks (5 for each of the 4 weeks). Each day is described in a uniform way: objectives, materials and protective equipment, OSH topics, a timed run of the session, methods, assessment, key vocabulary and tips for a trainer working with a multilingual group.",
    "es": "Este documento contiene escenarios detallados de 20 bloques de clase (5 por cada una de las 4 semanas). Cada día se describe de forma uniforme: objetivos, materiales y equipos de protección, temas de SST, desarrollo cronometrado de la sesión, métodos, evaluación, vocabulario clave y consejos para el formador que trabaja con un grupo multilingüe.",
}


def demote_headings(text: str) -> str:
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            m = re.match(r"^(#{1,6})(\s)", line)
            if m:
                line = "#" + line  # +1 poziom
        out.append(line)
    return "\n".join(out)


def strip_first_h1(text: str) -> str:
    text = text.lstrip("﻿").lstrip()
    # usun pierwszy wiersz jesli to naglowek H1
    m = re.match(r"^#\s+.+?(\n|$)", text)
    if m:
        return text[m.end():].lstrip("\n")
    return text


def assemble(lang: str) -> None:
    chunks = [f"# {DOC_TITLE_DIAC[lang]}", "", INTRO[lang], ""]
    for n in (1, 2, 3, 4):
        p = PARTS / f"scen-{lang}-w{n}.md"
        if not p.exists():
            raise SystemExit(f"BRAK: {p}")
        body = strip_first_h1(p.read_text(encoding="utf-8"))
        body = demote_headings(body)
        chunks.append(f"## {WEEK_HEADERS[lang][n]}")
        chunks.append("")
        chunks.append(body.strip())
        chunks.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{lang}.md").write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    # raport
    txt = (OUT / f"{lang}.md").read_text(encoding="utf-8")
    print(f"  {lang}: {len(txt.split())} slow, em-dash={txt.count(chr(0x2014))}, "
          f"## sekcji={txt.count(chr(10)+'## ')}, ### podsekcji={txt.count(chr(10)+'### ')}")


def main() -> None:
    print("Skladanie scenariuszy...")
    for lang in LANGS:
        assemble(lang)
    print("OK")


if __name__ == "__main__":
    main()
