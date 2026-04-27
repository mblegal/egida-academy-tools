#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sanitize_dates.py: usuwa konkretne daty cykli z materialow pomocniczych.

Modyfikuje IN-PLACE pliki MD w {kurs_root}/{course_slug}/content/materialy-pomocnicze/.
Decyzja D14 (dokumenty elastyczne): prospekty, programy i wytyczne nie
wiaza sie z konkretnym rokiem; konkretny terminarz cyklu komunikuje
koordynator Fundacji w procesie rekrutacji.

Konfiguracja (env vars + CLI args):
  EGIDA_KURS_ROOT  default: ~/Documents/EGIDA/kurs
  COURSE_SLUG      default: kurs_tartak

Uzycie:
  python sanitize_dates.py
  python sanitize_dates.py --course-slug nowy_zawod
  EGIDA_KURS_ROOT=/sciezka/do/kursow python sanitize_dates.py
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--course-slug", default=os.environ.get("COURSE_SLUG", "kurs_tartak"))
    p.add_argument("--course-source",
                   help="Pelna sciezka do source kursu (override env+slug)")
    return p.parse_args()


args = parse_args()
DEFAULT_KURS_ROOT = Path.home() / "Documents" / "EGIDA" / "kurs"
EGIDA_KURS_ROOT = Path(os.environ.get("EGIDA_KURS_ROOT", str(DEFAULT_KURS_ROOT)))
KURS = Path(args.course_source) if args.course_source else EGIDA_KURS_ROOT / args.course_slug
MAT = KURS / "content" / "materialy-pomocnicze"

if not MAT.exists():
    print(f"BLAD: brak {MAT}")
    sys.exit(1)

# ============================================================
# PATTERNS
# ============================================================
# Kolejnosc ma znaczenie, konkretniejsze najpierw.
SUBSTITUTIONS = [
    # --- Cytat absolwenta poprzedniej edycji ---
    (r"absolwent Edycji 2025/2026", "absolwent poprzedniej edycji"),
    (r"graduate of the 2025/2026 Edition", "graduate of a previous edition"),
    (r"graduado de la Edición 2025/2026", "graduado de una edición anterior"),
    (r"випускник Едиції 2025/2026", "випускник попередньої едиції"),

    # --- Terminy zgloszen konkretne ---
    (r"\*\*Termin zgłoszeń do cyklu Jesień 2026\*\*: 15 sierpnia 2026\.",
     "**Termin zgłoszeń do najbliższego cyklu** ustala Fundacja EGIDA i komunikuje go w procesie rekrutacji."),
    (r"\*\*Application deadline for the Autumn 2026 cycle\*\*: [^\n]+",
     "**Application deadline for the upcoming cycle** is set by Fundacja EGIDA and communicated during recruitment."),
    (r"\*\*Plazo de inscripción para el ciclo Otoño 2026\*\*: [^\n]+",
     "**Plazo de inscripción para el próximo ciclo** lo establece Fundacja EGIDA y se comunica durante el proceso de reclutamiento."),
    (r"\*\*Термін зголошень до циклу Осінь 2026\*\*: [^\n]+",
     "**Термін зголошень до найближчого циклу** встановлює Fundacja EGIDA і повідомляє його під час рекрутації."),
]


def remove_cycle_tables(text: str) -> str:
    """Usuwa tabele z cyklami kursu i zastepuje je ogolnym stwierdzeniem PL/EN/ES/UK."""
    patterns_pl = [
        (r"\| Cykl \| Rekrutacja \| Start kursu \| Egzamin końcowy M3 \|\n\|[-\s|]+\|\n"
         r"\|[^\n]*Jesień 2026[^\n]*\|\n"
         r"\|[^\n]*Zima 2026/2027[^\n]*\|\n"
         r"\|[^\n]*Wiosna 2027[^\n]*\|",
         "Kursy organizowane są w kilku cyklach rocznie. Aktualny kalendarz rekrutacji, startu cyklu i egzaminu końcowego M3 udostępnia koordynator Fundacji EGIDA na zapytanie kandydata."),
        (r"\| Cykl \| Rekrutacja \| M1 \| Przerwa międzymodułowa \| M2 \| Przerwa międzymodułowa \| M3 \| Egzaminy \|\n\|[-\s|]+\|\n"
         r"\|[^\n]*Jesień 2026[^\n]*\|\n"
         r"\|[^\n]*Zima 2026/2027[^\n]*\|\n"
         r"\|[^\n]*Wiosna 2027[^\n]*\|",
         "Fundacja EGIDA uruchamia kurs w kilku cyklach rocznie, każdy obejmujący pełny ciąg M1 + M2 + M3 oraz dwie przerwy międzymodułowe na staż. Konkretny harmonogram cyklu bieżącego przygotowuje i komunikuje koordynator Fundacji."),
        (r"### 3\.1\. Cykl Jesień 2026\n\n\| Tydzień \| Zakres pracy \| Kluczowe działanie koordynatora \|\n\|[-\s|]+\|\n(?:\|[^\n]+\|\n)+",
         "### 3.1. Przykładowy cykl roczny\n\nKażdy cykl roczny obejmuje 3-tygodniowy etap rekrutacji, 4 tygodnie M1, 1 tydzień stażu pomocnika, 4 tygodnie M2, 1 tydzień stażu operatora juniora, 4 tygodnie M3, 2 tygodnie egzaminów i ewaluacji. Koordynator w każdym tygodniu prowadzi cotygodniowe spotkania z trenerem, raporty do MFiPR w połowie każdego modułu i dokonuje decyzji o certyfikatach BTM/Wood-Mizer po egzaminach M2.\n\n"),
        (r"### 3\.2\. Cykl Zima 2026/2027 i Wiosna 2027\n\n[\s\S]*?(?=### 3\.3\.)",
         "### 3.2. Elastyczność sezonowa\n\nHarmonogram cykli uwzględnia sezonowość dostępu do placów tartacznych. Cykle jesienno-zimowe wymagają alternatywnego planu stażu (tartaki częściowo zamknięte w okresie świątecznym, ograniczony dostęp zewnętrzny w mróz), koordynator kieruje wtedy kursantów do stolarni zamkniętych. Cykle wiosenne i letnie dają najwyższą dostępność stażu u partnerów (sezonowy szczyt produkcji).\n\n"),
    ]
    for pattern, replacement in patterns_pl:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)

    patterns_other = [
        (r"\| Cycle \| Recruitment \| Course start \| Final M3 exam \|\n\|[-\s|]+\|\n"
         r"\|[^\n]*Autumn 2026[^\n]*\|\n"
         r"\|[^\n]*Winter 2026/2027[^\n]*\|\n"
         r"\|[^\n]*Spring 2027[^\n]*\|",
         "Courses run in several cycles per year. The exact calendar of recruitment, cycle start and the final M3 exam is shared by the Fundacja EGIDA coordinator on candidate request."),
        (r"\| Ciclo \| Reclutamiento \| Inicio del curso \| Examen final M3 \|\n\|[-\s|]+\|\n"
         r"\|[^\n]*Otoño 2026[^\n]*\|\n"
         r"\|[^\n]*Invierno 2026/2027[^\n]*\|\n"
         r"\|[^\n]*Primavera 2027[^\n]*\|",
         "Los cursos se imparten en varios ciclos al año. El calendario exacto de reclutamiento, inicio del ciclo y examen final M3 lo comparte la coordinadora de Fundacja EGIDA a petición del candidato."),
        (r"\| Цикл \| Рекрутація \| Початок курсу \| Фінальний іспит M3 \|\n\|[-\s|]+\|\n"
         r"\|[^\n]*Осінь 2026[^\n]*\|\n"
         r"\|[^\n]*Зима 2026/2027[^\n]*\|\n"
         r"\|[^\n]*Весна 2027[^\n]*\|",
         "Курси проводяться у кількох циклах на рік. Точний календар рекрутації, початку циклу та фінального іспиту M3 надає координатор Fundacja EGIDA на запит кандидата."),
    ]
    for pattern, replacement in patterns_other:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)

    return text


# ============================================================
# EXECUTE
# ============================================================
files = list(MAT.rglob("*.md"))
total_changes = 0

for f in files:
    original = f.read_text(encoding="utf-8")
    new = original
    for pattern, replacement in SUBSTITUTIONS:
        new = re.sub(pattern, replacement, new)
    new = remove_cycle_tables(new)
    if new != original:
        diff_lines = len(new) - len(original)
        f.write_text(new, encoding="utf-8")
        print(f"OK  {f.relative_to(MAT)} ({diff_lines:+d} chars)")
        total_changes += 1
    else:
        has_dates = any(k in original for k in [
            "Jesień 2026", "Zima 2026", "Wiosna 2027", "2025/2026",
            "Autumn 2026", "Otoño 2026", "Осінь 2026"])
        if has_dates:
            print(f"??? {f.relative_to(MAT)}: daty pozostaly, wymaga sprawdzenia")
        else:
            print(f"-   {f.relative_to(MAT)}: brak dat kursu")

print(f"\nZmodyfikowano {total_changes} z {len(files)} plikow")

leftover = []
for f in files:
    t = f.read_text(encoding="utf-8")
    for pat in [
        "Jesień 2026", "Zima 2026", "Wiosna 2027", "Edycji 2025/2026",
        "1 września 2026", "15 grudnia 2026", "15 sierpnia 2026",
        "Autumn 2026", "Winter 2026", "Spring 2027", "2025/2026 Edition",
        "Otoño 2026", "Invierno 2026", "Primavera 2027", "Edición 2025/2026",
        "Осінь 2026", "Зима 2026", "Весна 2027", "Едиції 2025/2026",
    ]:
        if pat in t:
            leftover.append(f"{f.relative_to(MAT)}: '{pat}'")

if leftover:
    print(f"\n!!! POZOSTALY daty ({len(leftover)}):")
    for l in leftover[:20]:
        print(f"    {l}")
else:
    print("\nOK: 0 dat cyklu kursu pozostalo w MD")
