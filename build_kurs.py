#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_kurs.py: pipeline budowania Pakietu A kursu (treci dla kursanta + rekrutacji + trenera).

Kopiuje dist/ standalone HTML i renderuje materialy MD do HTML z brandingiem
EGIDA (egida.css). Generuje:
  public/<course-hub-slug>/kursant/{kurs,prezentacja}-M{1,2,3}.html  (6 plikow z dist/)
  public/<course-hub-slug>/rekrutacja/{program-ogolny,program-szczegolowy-{pl,en,es,uk}}.html
  public/<course-hub-slug>/trener/M{1,2,3}/{quiz,cwiczenia,scenariusze,wytyczne}-*.html
  public/<course-hub-slug>/assets/egida.css  (z templates/)

UWAGA: index.html hubu generuje build_hub_index.py. Run flow:
  1) python build_kurs.py
  2) python post_process.py
  3) python build_hub_index.py

Konfiguracja (env vars + CLI):
  EGIDA_KURS_ROOT   default: ~/Documents/EGIDA/kurs
  COURSE_SLUG       default: kurs_tartak
  COURSE_HUB_SLUG   default: kurs-tartak (auto z slug, _ -> -)
  EGIDA_OUT_DIR     default: <repo>/public

Uzycie:
  python build_kurs.py
  python build_kurs.py --course-slug nowy_zawod --course-hub-slug nowy-zawod
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

import markdown


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--course-slug", default=os.environ.get("COURSE_SLUG", "kurs_tartak"))
    p.add_argument("--course-hub-slug", default=os.environ.get("COURSE_HUB_SLUG"))
    p.add_argument("--course-source", help="Pelna sciezka do source kursu (override)")
    p.add_argument("--output", help="Override OUT (sciezka do public/<slug>)")
    return p.parse_args()


args = parse_args()
REPO = Path(__file__).resolve().parent
DEFAULT_KURS_ROOT = Path.home() / "Documents" / "EGIDA" / "kurs"
EGIDA_KURS_ROOT = Path(os.environ.get("EGIDA_KURS_ROOT", str(DEFAULT_KURS_ROOT)))

COURSE_SLUG = args.course_slug
COURSE_HUB_SLUG = args.course_hub_slug or COURSE_SLUG.replace("_", "-")

KURS = Path(args.course_source) if args.course_source else EGIDA_KURS_ROOT / COURSE_SLUG

DEFAULT_OUT_ROOT = REPO / "public"
OUT_ROOT = Path(os.environ.get("EGIDA_OUT_DIR", str(DEFAULT_OUT_ROOT)))
OUT = Path(args.output) if args.output else OUT_ROOT / COURSE_HUB_SLUG

TEMPLATES = REPO / "templates"
ASSETS = REPO / "assets"

if not KURS.exists():
    raise SystemExit(f"BLAD: brak source kursu: {KURS}")
if not (TEMPLATES / "egida.css").exists():
    raise SystemExit(f"BLAD: brak templates/egida.css w {TEMPLATES}")
if not (TEMPLATES / "doc.html.template").exists():
    raise SystemExit(f"BLAD: brak templates/doc.html.template w {TEMPLATES}")

# ============== STRUKTURA FOLDEROW ==============
(OUT / "assets").mkdir(parents=True, exist_ok=True)
(OUT / "kursant").mkdir(exist_ok=True)
(OUT / "rekrutacja").mkdir(exist_ok=True)
for m in ("M1", "M2", "M3"):
    (OUT / "trener" / m).mkdir(parents=True, exist_ok=True)

# ============== ASSETS (templates/egida.css + logo PNG) ==============
shutil.copy2(TEMPLATES / "egida.css", OUT / "assets" / "egida.css")
for logo in ASSETS.glob("egida-logo-*.png"):
    shutil.copy2(logo, OUT / "assets" / logo.name)
print(f"OK: assets/ skopiowane (egida.css + {len(list(ASSETS.glob('egida-logo-*.png')))} logo)")

# ============== TEMPLATE DOKUMENTU ==============
DOC_TEMPLATE = (TEMPLATES / "doc.html.template").read_text(encoding="utf-8")


def build_lang_switch(lang_variants, current_lang):
    """Generuje HTML dla doc-lang-switch w headerze podstrony.

    lang_variants: dict lang->href (np. {'pl': 'prospekt-pl.html', ...}); None = PL-only.
    """
    names = {"pl": "PL", "en": "EN", "es": "ES", "uk": "UK"}
    only_pl_msg = {"pl": "Dostępne tylko w języku polskim", "en": "Available in Polish only",
                   "es": "Disponible solo en polaco", "uk": "Доступно лише польською"}
    msg = only_pl_msg.get(current_lang, only_pl_msg["pl"])
    aria_labels = {"pl": "Język dokumentu", "en": "Document language",
                   "es": "Idioma del documento", "uk": "Мова документа"}
    aria = aria_labels.get(current_lang, aria_labels["pl"])
    parts = [f'    <nav class="doc-lang-switch" aria-label="{aria}">']
    for L in ("pl", "en", "es", "uk"):
        if lang_variants and L in lang_variants:
            is_current = (L == current_lang)
            cls = ' class="on" aria-current="page"' if is_current else ""
            href = lang_variants[L] if not is_current else "#"
            parts.append(f'      <a data-lang="{L}" href="{href}"{cls} hreflang="{L}">{names[L]}</a>')
        else:
            if L == "pl":
                parts.append(f'      <a data-lang="pl" href="#" class="on" aria-current="page" hreflang="pl">PL</a>')
            else:
                parts.append(f'      <span class="lang-disabled" aria-disabled="true" title="{msg}">{names[L]}</span>')
    parts.append('    </nav>')
    return "\n".join(parts)


def render_md_to_html(md_path: Path, out_path: Path, title: str, section: str,
                     section_anchor: str, doc_label: str, lang: str = "pl",
                     hub_depth: int = 1, lang_variants: dict = None):
    """Renderuje plik Markdown do HTML z brandingiem EGIDA."""
    text = md_path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].lstrip()
    lines = text.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        text = "\n".join(lines).lstrip()
    html_body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
    )
    prefix = "../" * hub_depth
    lang_switch = build_lang_switch(lang_variants, lang)
    out_path.write_text(
        DOC_TEMPLATE.format(
            lang=lang,
            title=title,
            content=html_body,
            section=section,
            section_anchor=section_anchor,
            doc_label=doc_label,
            assets_prefix=prefix,
            hub_prefix=prefix,
            prev_next_html="",
            lang_switch_html=lang_switch,
        ),
        encoding="utf-8",
    )


# ============== KOPIA dist/ HTML ==============
for module in ("M1", "M2", "M3"):
    src_kurs = KURS / "dist" / f"kurs_{module}.html"
    src_prez = KURS / "dist" / f"prezentacja_{module}.html"
    if not src_kurs.exists() or not src_prez.exists():
        raise SystemExit(f"BLAD: brak {src_kurs} lub {src_prez}. Uruchom 'npm run build:all' w {KURS}.")
    shutil.copy2(src_kurs, OUT / "kursant" / f"kurs-{module}.html")
    shutil.copy2(src_prez, OUT / "kursant" / f"prezentacja-{module}.html")
print("OK: dist/ 6 plikow skopiowanych do kursant/")

# ============== REKRUTACJA ==============
# D1, program ogolny PL
render_md_to_html(
    KURS / "content/materialy-pomocnicze/program-ogolny/pl.md",
    OUT / "rekrutacja" / "program-ogolny.html",
    title="Program ogólny kursu",
    section="Dla rekrutacji",
    section_anchor="rekrutacja",
    doc_label="Program ogólny (D1)",
    lang="pl",
    hub_depth=1,
)

# D2, program szczegolowy x 4 jez
lang_names = {"pl": "polski", "en": "English", "es": "español", "uk": "українська"}
d2_variants = {L: f"program-szczegolowy-{L}.html" for L in ("pl", "en", "es", "uk")}
for lang in ("pl", "en", "es", "uk"):
    render_md_to_html(
        KURS / f"content/materialy-pomocnicze/program-szczegolowy/{lang}.md",
        OUT / "rekrutacja" / f"program-szczegolowy-{lang}.html",
        title=f"Program szczegółowy ({lang_names[lang]})",
        section="Dla rekrutacji",
        section_anchor="rekrutacja",
        doc_label=f"Program szczegółowy D2 · {lang_names[lang]}",
        lang=lang,
        hub_depth=1,
        lang_variants=d2_variants,
    )

print("OK: rekrutacja/ 5 plikow (D1 + D2x4)")

# ============== TRENER (artefakty M1/M2/M3) ==============
artefact_labels = {
    "quiz-uzupelniajacy": "Quiz uzupełniający (A1)",
    "cwiczenia-teoretyczne": "Ćwiczenia teoretyczne (A2)",
    "scenariusze-praktyczne": "Scenariusze praktyczne (A3)",
    "wytyczne-trenera": "Wytyczne dla trenera (A4)",
}

for module in ("M1", "M2", "M3"):
    # Quiz i cwiczenia, 4 jezyki kazdy
    for kind in ("quiz-uzupelniajacy", "cwiczenia-teoretyczne"):
        trener_variants = {L: f"{kind}-{L}.html" for L in ("pl", "en", "es", "uk")}
        for lang in ("pl", "en", "es", "uk"):
            src = KURS / f"content/{module}/artifacts/{kind}/{lang}.md"
            if not src.exists():
                print(f"SKIP: brak {src}")
                continue
            render_md_to_html(
                src,
                OUT / "trener" / module / f"{kind}-{lang}.html",
                title=f"{artefact_labels[kind]} · Moduł {module[-1]} ({lang_names[lang]})",
                section=f"Dla trenera · Moduł {module[-1]}",
                section_anchor="trener",
                doc_label=f"{artefact_labels[kind]} · {lang_names[lang]}",
                lang=lang,
                hub_depth=2,
                lang_variants=trener_variants,
            )
    # Scenariusze i wytyczne, tylko PL
    for kind in ("scenariusze-praktyczne", "wytyczne-trenera"):
        src = KURS / f"content/{module}/artifacts/{kind}/pl.md"
        if not src.exists():
            print(f"SKIP: brak {src}")
            continue
        render_md_to_html(
            src,
            OUT / "trener" / module / f"{kind}.html",
            title=f"{artefact_labels[kind]} · Moduł {module[-1]}",
            section=f"Dla trenera · Moduł {module[-1]}",
            section_anchor="trener",
            doc_label=f"{artefact_labels[kind]} · polski",
            lang="pl",
            hub_depth=2,
        )
print("OK: trener/ 30 plikow (10 per modul x M1/M2/M3)")

# ============== PROJEKT (dla koordynatora, opcjonalnie) ==============
projekt_md = KURS / "content/materialy-pomocnicze/projekt/pl.md"
if projekt_md.exists():
    (OUT / "projekt").mkdir(exist_ok=True)
    render_md_to_html(
        projekt_md,
        OUT / "projekt" / "index.html",
        title="O projekcie",
        section="Projekt",
        section_anchor="projekt",
        doc_label="O projekcie",
        lang="pl",
        hub_depth=1,
    )
    print("OK: projekt/index.html")

print()
print("=== build_kurs.py done ===")
print(f"Output: {OUT}")
