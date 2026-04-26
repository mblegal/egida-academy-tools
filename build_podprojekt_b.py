#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_podprojekt_b.py: pipeline budowania Pakietu B (dokumenty kursowe formalne).

Wejście:  kurs_tartak/podprojekt-b/{B1,B2,B3}/{nazwa}/{pl,en,es,uk}.md
Wyjście:  web-hub/public/kurs-tartak/dokumenty/{B1,B2,B3}/{nazwa}/{lang}/index.html
        + web-hub/public/kurs-tartak/dokumenty/{B1,B2,B3}/{nazwa}/{nazwa}-{lang}.docx
        + web-hub/public/kurs-tartak/dokumenty/{B1,B2,B3}/{nazwa}/{nazwa}-{lang}.pdf

Zależności: pandoc 3.x, wkhtmltopdf 0.12+, pyyaml.
Idempotentność: skip jeśli output mtime > input mtime; FORCE_REBUILD=1 wymusza rebuild.

Synchronizuj DOC_TEMPLATE i build_lang_switch z build-kurs-tartak.py
(tech debt: wyciągnąć do wspólnego modułu po Part 47).
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# =====================================================================
# Konfiguracja: scieki i parametry per kurs
#
# Ustaw env var albo przekaz przez --course-source / --course-slug.
# Default zaklada strukture katalogow przyjeta na autorskim komputerze:
#   ~/Documents/EGIDA/kurs/{course_slug}/podprojekt-b/...
# Dla pracownika Fundacji ktory clonuje to repo do innego miejsca,
# wystarczy: EGIDA_KURS_ROOT=/sciezka/do/kursow python build_podprojekt_b.py
# =====================================================================
WEB_HUB = Path(__file__).resolve().parent

DEFAULT_KURS_ROOT = Path.home() / "Documents" / "EGIDA" / "kurs"
EGIDA_KURS_ROOT = Path(os.environ.get("EGIDA_KURS_ROOT", str(DEFAULT_KURS_ROOT)))

# Slug kursu (subdirectory w EGIDA_KURS_ROOT). Underscored = source dirname,
# myslnik = url-friendly hub slug.
COURSE_SLUG = os.environ.get("COURSE_SLUG", "kurs_tartak")
COURSE_HUB_SLUG = os.environ.get("COURSE_HUB_SLUG", COURSE_SLUG.replace("_", "-"))

KURS = EGIDA_KURS_ROOT / COURSE_SLUG
SRC_ROOT = KURS / "podprojekt-b"
OUT_ROOT = WEB_HUB / "public" / COURSE_HUB_SLUG / "dokumenty"


def _resolve_wkhtmltopdf() -> str:
    """Znajdz wkhtmltopdf: env var, PATH, Windows default. W tej kolejnosci."""
    env = os.environ.get("WKHTMLTOPDF_PATH")
    if env and Path(env).exists():
        return env
    found = shutil.which("wkhtmltopdf")
    if found:
        return found
    win_default = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if Path(win_default).exists():
        return win_default
    # Last resort: nadzieja ze pojawi sie w PATH przy uruchomieniu subprocess.
    # Jesli nie, subprocess.run zwroci jasny FileNotFoundError.
    return "wkhtmltopdf"


WKHTMLTOPDF = _resolve_wkhtmltopdf()
PANDOC = os.environ.get("PANDOC_PATH", "pandoc")

FORCE_REBUILD = os.environ.get("FORCE_REBUILD", "") == "1"

# =====================================================================
# Katalog dokumentów (13 typów w 3 fazach)
# =====================================================================
SECTION_LABELS = {
    "B1": {
        "pl": "Rdzeń prawny",
        "en": "Legal core",
        "es": "Núcleo jurídico",
        "uk": "Правове ядро",
    },
    "B2": {
        "pl": "Dokumenty kursanta",
        "en": "Participant documents",
        "es": "Documentos del cursante",
        "uk": "Документи курсанта",
    },
    "B3": {
        "pl": "Polityki i back-office",
        "en": "Policies and back-office",
        "es": "Políticas y back-office",
        "uk": "Політики та бек-офіс",
    },
}

# Etykiety UI per typ × per jęz (krótkie, do breadcrumb i tytułu strony).
DOC_LABELS = {
    "umowa-kursu": {
        "pl": "Umowa kursu",
        "en": "Course Agreement",
        "es": "Contrato del curso",
        "uk": "Договір курсу",
    },
    "zaswiadczenie-odbywania": {
        "pl": "Zaświadczenie o odbywaniu kursu",
        "en": "Certificate of Course Attendance",
        "es": "Certificado de asistencia al curso",
        "uk": "Довідка про відвідування курсу",
    },
    "zaswiadczenie-ukonczenia-modulu-m1": {
        "pl": "Zaświadczenie ukończenia Modułu M1",
        "en": "Certificate of Completion of Module M1",
        "es": "Certificado de finalización del Módulo M1",
        "uk": "Свідоцтво про завершення Модуля M1",
    },
    "zaswiadczenie-ukonczenia-modulu-m2": {
        "pl": "Zaświadczenie ukończenia Modułu M2",
        "en": "Certificate of Completion of Module M2",
        "es": "Certificado de finalización del Módulo M2",
        "uk": "Свідоцтво про завершення Модуля M2",
    },
    "zaswiadczenie-ukonczenia-modulu-m3": {
        "pl": "Zaświadczenie ukończenia Modułu M3",
        "en": "Certificate of Completion of Module M3",
        "es": "Certificado de finalización del Módulo M3",
        "uk": "Свідоцтво про завершення Модуля M3",
    },
    "zaswiadczenie-ukonczenia-kursu": {
        "pl": "Zaświadczenie ukończenia kursu",
        "en": "Course Completion Certificate",
        "es": "Certificado de finalización del curso",
        "uk": "Свідоцтво про завершення курсу",
    },
    "zaswiadczenie-praktyki-odbywania": {
        "pl": "Zaświadczenie o odbywaniu praktyki absolwenckiej",
        "en": "Certificate of Graduate Apprenticeship in Progress",
        "es": "Certificado de prácticas de graduado en curso",
        "uk": "Довідка про проходження випускницької практики",
    },
    "zaswiadczenie-praktyki-ukonczenia": {
        "pl": "Zaświadczenie ukończenia praktyki absolwenckiej",
        "en": "Certificate of Completion of Graduate Apprenticeship",
        "es": "Certificado de finalización de prácticas de graduado",
        "uk": "Свідоцтво про завершення випускницької практики",
    },
    "regulamin-kursu": {
        "pl": "Regulamin kursu",
        "en": "Course Regulations",
        "es": "Reglamento del curso",
        "uk": "Регламент курсу",
    },
    "rodo-klauzula-zgody": {
        "pl": "Klauzula informacyjna RODO i zgody",
        "en": "GDPR Information Notice and Consents",
        "es": "Cláusula informativa RGPD y consentimientos",
        "uk": "Інформаційна клаузула GDPR та згоди",
    },
    "formularz-rekrutacyjny": {
        "pl": "Formularz rekrutacyjny",
        "en": "Application Form",
        "es": "Formulario de admisión",
        "uk": "Анкета кандидата",
    },
    "polityka-reklamacji": {
        "pl": "Polityka reklamacji i odwołań",
        "en": "Complaints and Appeals Policy",
        "es": "Política de reclamaciones y apelaciones",
        "uk": "Політика розгляду скарг та апеляцій",
    },
    "umowa-wspolorganizacji": {
        "pl": "Umowa współorganizacji",
        "en": "Co-Organization Agreement",
    },
}

# Lista dokumentów do zbudowania (slug, faza, języki).
DOCS = [
    ("B1", "umowa-kursu", ["pl", "en", "es", "uk"]),
    ("B1", "zaswiadczenie-odbywania", ["pl", "en", "es", "uk"]),
    ("B1", "zaswiadczenie-ukonczenia-modulu-m1", ["pl", "en", "es", "uk"]),
    ("B1", "zaswiadczenie-ukonczenia-modulu-m2", ["pl", "en", "es", "uk"]),
    ("B1", "zaswiadczenie-ukonczenia-modulu-m3", ["pl", "en", "es", "uk"]),
    ("B1", "zaswiadczenie-ukonczenia-kursu", ["pl", "en", "es", "uk"]),
    ("B1", "zaswiadczenie-praktyki-odbywania", ["pl", "en", "es", "uk"]),
    ("B1", "zaswiadczenie-praktyki-ukonczenia", ["pl", "en", "es", "uk"]),
    ("B2", "regulamin-kursu", ["pl", "en", "es", "uk"]),
    ("B2", "rodo-klauzula-zgody", ["pl", "en", "es", "uk"]),
    ("B2", "formularz-rekrutacyjny", ["pl", "en", "es", "uk"]),
    ("B3", "polityka-reklamacji", ["pl", "en", "es", "uk"]),
    ("B3", "umowa-wspolorganizacji", ["pl", "en"]),
]

# =====================================================================
# DOC_TEMPLATE: synchronizuj z build-kurs-tartak.py:265 (DOC_TEMPLATE).
# Refaktor wspólnego modułu: tech debt na Part 47 (cel pomocniczy).
# =====================================================================
DOC_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f6f4ef">
<meta name="page-context" content="dokumenty/{phase}/{slug}/{lang}">
<title>{title} · Kurs tartakowy EGIDA</title>
<link rel="stylesheet" href="{assets_prefix}assets/egida.css">
<link rel="stylesheet" href="{assets_prefix}assets/dokument.css">
<link rel="icon" type="image/png" href="{assets_prefix}assets/egida-logo-64.png">
</head>
<body>
<div class="doc-wrap">
  <header class="doc-header">
    <a class="doc-logo" href="{hub_prefix}index.html" title="{logo_title}">
      <img src="{assets_prefix}assets/egida-logo-wide-128.png" alt="Logo Fundacji EGIDA">
    </a>
    <div class="doc-header-body">
      <div class="doc-breadcrumb">
        <a href="{hub_prefix}index.html">Kurs tartakowy EGIDA</a> /
        <a href="{hub_prefix}dokumenty/index.html">{docs_section}</a> /
        {section_label} /
        {doc_label}
      </div>
      <h1 class="doc-title">{title}</h1>
      <div class="doc-meta">{meta_html}</div>
    </div>
{lang_switch_html}
  </header>

  <main class="doc-content">
{content}
  </main>

  <section class="doc-downloads" aria-label="{downloads_label}">
    <a class="doc-download doc-download-docx" href="{slug}-{lang}.docx" download>
      <span class="doc-download-icon" aria-hidden="true">DOCX</span>
      <span class="doc-download-label">{download_docx}</span>
    </a>
    <a class="doc-download doc-download-pdf" href="{slug}-{lang}.pdf" download>
      <span class="doc-download-icon" aria-hidden="true">PDF</span>
      <span class="doc-download-label">{download_pdf}</span>
    </a>
  </section>

  <footer class="doc-footer">
    <span class="egida-mark">Fundacja EGIDA · Kurs „Praca w tartaku" · {version_label}</span>
    <a href="{hub_prefix}dokumenty/index.html">{back_to_list}</a>
  </footer>
</div>
<script src="{assets_prefix}assets/chrome.js"></script>
</body>
</html>
"""

# =====================================================================
# i18n etykiet dla footera, lang switch itp.
# =====================================================================
I18N = {
    "pl": {
        "logo_title": "Powrót do hubu Fundacji EGIDA",
        "docs_section": "Dokumenty kursu",
        "downloads_label": "Pobierz dokument",
        "download_docx": "Pobierz jako DOCX (do edycji)",
        "download_pdf": "Pobierz jako PDF (do druku)",
        "back_to_list": "← Powrót do listy dokumentów",
        "version_label_template": "wersja {wersja} · stan na {stan}",
        "doc_lang_aria": "Język dokumentu",
        "no_translations_msg": "Dokument dostępny tylko w języku polskim",
    },
    "en": {
        "logo_title": "Back to EGIDA Foundation hub",
        "docs_section": "Course documents",
        "downloads_label": "Download document",
        "download_docx": "Download as DOCX (editable)",
        "download_pdf": "Download as PDF (printable)",
        "back_to_list": "← Back to document list",
        "version_label_template": "version {wersja} · as of {stan}",
        "doc_lang_aria": "Document language",
        "no_translations_msg": "Document available in Polish only",
    },
    "es": {
        "logo_title": "Volver al portal de la Fundación EGIDA",
        "docs_section": "Documentos del curso",
        "downloads_label": "Descargar documento",
        "download_docx": "Descargar como DOCX (editable)",
        "download_pdf": "Descargar como PDF (imprimible)",
        "back_to_list": "← Volver a la lista de documentos",
        "version_label_template": "versión {wersja} · vigente desde {stan}",
        "doc_lang_aria": "Idioma del documento",
        "no_translations_msg": "Documento disponible solo en polaco",
    },
    "uk": {
        "logo_title": "Повернення на портал Фундації EGIDA",
        "docs_section": "Документи курсу",
        "downloads_label": "Завантажити документ",
        "download_docx": "Завантажити DOCX (для редагування)",
        "download_pdf": "Завантажити PDF (для друку)",
        "back_to_list": "← Повернутися до списку документів",
        "version_label_template": "версія {wersja} · станом на {stan}",
        "doc_lang_aria": "Мова документа",
        "no_translations_msg": "Документ доступний лише польською",
    },
}

LANG_NAMES = {"pl": "PL", "en": "EN", "es": "ES", "uk": "UK"}


# =====================================================================
# Pomocnicze
# =====================================================================
@dataclass
class DocBuild:
    phase: str        # "B1" / "B2" / "B3"
    slug: str         # "umowa-kursu"
    langs: list[str]  # ["pl","en","es","uk"]


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    """Wyciąga YAML frontmatter z początku pliku. Zwraca (metadata, body)."""
    if not md_text.startswith("---"):
        return {}, md_text
    end = md_text.find("\n---", 3)
    if end == -1:
        return {}, md_text
    yaml_part = md_text[3:end].strip()
    body = md_text[end + 4 :].lstrip("\n")
    try:
        meta = yaml.safe_load(yaml_part) or {}
    except yaml.YAMLError as exc:
        print(f"  WARN: YAML parse error: {exc}", file=sys.stderr)
        meta = {}
    return meta, body


def needs_rebuild(src: Path, dst: Path) -> bool:
    if FORCE_REBUILD:
        return True
    if not dst.exists():
        return True
    return src.stat().st_mtime > dst.stat().st_mtime


def build_lang_switch(slug: str, langs: list[str], current_lang: str, doc_lang_aria: str, no_translations_msg: str) -> str:
    """Generuje nawigację języków u góry dokumentu.

    URL form: ../{lang}/index.html (z {lang}/index.html → ../{other_lang}/index.html).
    """
    parts = [f'    <nav class="doc-lang-switch" aria-label="{doc_lang_aria}">']
    for L in ("pl", "en", "es", "uk"):
        if L in langs:
            is_current = (L == current_lang)
            cls = ' class="on" aria-current="page"' if is_current else ""
            href = "#" if is_current else f"../{L}/index.html"
            parts.append(f'      <a data-lang="{L}" href="{href}"{cls} hreflang="{L}">{LANG_NAMES[L]}</a>')
        else:
            parts.append(f'      <span class="lang-disabled" aria-disabled="true" title="{no_translations_msg}">{LANG_NAMES[L]}</span>')
    parts.append("    </nav>")
    return "\n".join(parts)


def render_md_body_to_html(md_path: Path, body_text: str) -> str:
    """Renderuje body MD (po stripie frontmatter) do HTML fragmentu przez pandoc.

    Pandoc zachowuje footnotes, tabele, inline HTML. Body fragment (nie standalone),
    bo wstawiamy go do DOC_TEMPLATE.
    """
    result = subprocess.run(
        [PANDOC, "-f", "markdown+yaml_metadata_block-implicit_figures",
         "-t", "html5", "--no-highlight"],
        input=body_text,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return result.stdout


def render_md_to_docx(md_path: Path, dst: Path) -> None:
    """Pandoc MD → DOCX. Frontmatter pandoc traktuje jako metadata YAML i nie wstawia go do treści."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [PANDOC, "-f", "markdown+yaml_metadata_block-implicit_figures",
         "-t", "docx", str(md_path), "-o", str(dst)],
        check=True,
    )


# PRINT_TEMPLATE: standalone HTML do generowania PDF.
# Bez chrome.js (PIN gate ukrywa body), bez doc-downloads i lang-switch
# (w PDF zbędne), inline CSS (deterministyczne, nie zależy od path resolution).
PRINT_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
@page {{ margin: 18mm 20mm; }}
* {{ box-sizing: border-box; }}
body {{
  font-family: "Source Serif 4", "Source Serif Pro", Georgia, "Times New Roman", serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1c1b17;
  margin: 0;
  padding: 0;
  background: #fff;
}}
.print-header {{
  border-bottom: 2px solid #7a3b1a;
  padding-bottom: 0.8em;
  margin-bottom: 1.2em;
}}
.print-mark {{
  font-family: Inter, "Helvetica Neue", Arial, sans-serif;
  font-size: 9pt;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #7a3b1a;
}}
.print-title {{
  font-size: 16pt;
  font-weight: 700;
  margin: 0.2em 0 0.1em 0;
  line-height: 1.25;
}}
.print-meta {{
  font-family: Inter, "Helvetica Neue", Arial, sans-serif;
  font-size: 8.5pt;
  color: #5a574e;
  margin-top: 0.3em;
}}
h1, h2, h3 {{
  font-family: "Source Serif 4", Georgia, serif;
  font-weight: 700;
  page-break-after: avoid;
}}
h1 {{ font-size: 14pt; margin: 1.4em 0 0.6em; }}
h2 {{ font-size: 12pt; margin: 1.2em 0 0.5em; }}
h3 {{ font-size: 10.5pt; margin: 1em 0 0.4em; }}
p {{ margin: 0.4em 0 0.7em; }}
table {{
  border-collapse: collapse;
  width: 100%;
  margin: 0.7em 0;
  font-size: 9.5pt;
  page-break-inside: auto;
}}
th, td {{
  border: 1px solid #d9d4c5;
  padding: 0.4em 0.6em;
  vertical-align: top;
  text-align: left;
}}
th {{ background: #f6f4ef; font-weight: 600; }}
tr {{ page-break-inside: avoid; }}
ul, ol {{ margin: 0.4em 0 0.7em 1.4em; padding: 0; }}
li {{ margin: 0.2em 0; }}
hr {{ border: none; border-top: 1px solid #d9d4c5; margin: 1.4em 0; }}
.footnotes {{
  margin-top: 2em;
  padding-top: 0.8em;
  border-top: 1px solid #d9d4c5;
  font-size: 9pt;
  color: #3a3833;
}}
.footnotes ol {{ margin-left: 1.2em; }}
.footnotes p {{ margin: 0.2em 0; }}
sup, .footnote-ref {{ font-size: 0.8em; line-height: 0; }}
a {{ color: #1c1b17; text-decoration: none; }}
a.footnote-ref {{ color: #7a3b1a; }}
blockquote {{
  margin: 0.8em 1em;
  padding: 0.4em 1em;
  border-left: 3px solid #d9d4c5;
  color: #3a3833;
}}
.print-footer {{
  margin-top: 2em;
  padding-top: 0.6em;
  border-top: 1px solid #d9d4c5;
  font-family: Inter, "Helvetica Neue", Arial, sans-serif;
  font-size: 8pt;
  color: #5a574e;
  text-align: center;
}}
</style>
</head>
<body>
<header class="print-header">
  <div class="print-mark">Fundacja EGIDA · Kurs „Praca w tartaku" · {section_label}</div>
  <h1 class="print-title">{title}</h1>
  <div class="print-meta">{version_label}</div>
</header>
<main>
{content}
</main>
<footer class="print-footer">
  Fundacja pomocy prawnej EGIDA · ul. Ozimska 14-16/314A, 45-057 Opole · KRS 0000957190
</footer>
</body>
</html>
"""


def render_html_to_pdf(print_html_path: Path, dst: Path) -> None:
    """wkhtmltopdf HTML do PDF. Wejście: standalone print HTML (PRINT_TEMPLATE), bez chrome.js."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            WKHTMLTOPDF,
            "--quiet",
            "--enable-local-file-access",
            "--encoding", "UTF-8",
            "--margin-top", "18mm",
            "--margin-bottom", "18mm",
            "--margin-left", "20mm",
            "--margin-right", "20mm",
            "--print-media-type",
            str(print_html_path),
            str(dst),
        ],
        check=True,
    )


def fmt_meta(metadata: dict) -> str:
    """Renderuje metadata YAML do bloku <dl> w nagłówku dokumentu."""
    keys_show = [
        ("dokument", "Typ"),
        ("kurs", "Kurs"),
        ("podstawa-prawna", "Podstawa prawna"),
    ]
    pairs = []
    for key, _label in keys_show:
        v = metadata.get(key)
        if not v:
            continue
        if isinstance(v, list):
            joined = "; ".join(str(x) for x in v)
            pairs.append(f'<span class="doc-meta-item"><strong>{_label}:</strong> {joined}</span>')
        else:
            pairs.append(f'<span class="doc-meta-item"><strong>{_label}:</strong> {v}</span>')
    return "\n".join(pairs)


def write_dokument_css(out_assets: Path) -> None:
    """Pisze dodatkowy CSS dla podstron dokumentów (sekcja downloads + meta).

    Bazuje na egida.css; dokładamy tylko klasy dla doc-downloads i doc-meta-item.
    """
    out_assets.mkdir(parents=True, exist_ok=True)
    css = """/* dokument.css: dodatki dla podstron Pakietu B (build_podprojekt_b.py) */

.doc-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: var(--ink-muted, #5a574e);
  line-height: 1.5;
}
.doc-meta-item strong {
  font-weight: 600;
  color: var(--ink, #1c1b17);
}

.doc-downloads {
  display: flex;
  gap: 1rem;
  margin: 3rem 0 2rem;
  padding: 1.5rem;
  background: var(--paper, #fbfaf6);
  border: 1px solid var(--rule, #d9d4c5);
  border-radius: 4px;
  flex-wrap: wrap;
}
.doc-download {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  background: var(--bg, #f6f4ef);
  border: 1px solid var(--rule, #d9d4c5);
  border-radius: 4px;
  text-decoration: none;
  color: var(--ink, #1c1b17);
  font-weight: 500;
  transition: background 0.15s ease, border-color 0.15s ease;
}
.doc-download:hover,
.doc-download:focus-visible {
  background: var(--paper, #fbfaf6);
  border-color: var(--accent, #7a3b1a);
  outline: none;
}
.doc-download:focus-visible {
  outline: 2px solid var(--accent, #7a3b1a);
  outline-offset: 2px;
}
.doc-download-icon {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: var(--accent, #7a3b1a);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  border-radius: 2px;
}
.doc-download-label {
  font-size: 0.9375rem;
}

@media print {
  .doc-downloads,
  .doc-lang-switch,
  .doc-footer a[href*="dokumenty"] {
    display: none !important;
  }
  .doc-wrap {
    padding: 0;
  }
  .doc-content {
    font-size: 10.5pt;
  }
}

@media (max-width: 640px) {
  .doc-downloads {
    flex-direction: column;
    gap: 0.5rem;
  }
  .doc-download {
    width: 100%;
    justify-content: center;
  }
}
"""
    (out_assets / "dokument.css").write_text(css, encoding="utf-8")


# =====================================================================
# Główna pętla budowania
# =====================================================================
def build_one(phase: str, slug: str, langs: list[str], lang: str) -> dict:
    """Buduje 3 pliki (HTML, DOCX, PDF) dla jednego dokumentu × jednego języka.

    Zwraca dict z wynikami (built/skipped per format).
    """
    src = SRC_ROOT / phase / slug / f"{lang}.md"
    if not src.exists():
        raise FileNotFoundError(f"Brak źródła: {src}")

    out_dir = OUT_ROOT / phase / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    html_dir = out_dir / lang
    html_dir.mkdir(parents=True, exist_ok=True)
    html_dst = html_dir / "index.html"
    docx_dst = out_dir / f"{slug}-{lang}.docx"
    pdf_dst = out_dir / f"{slug}-{lang}.pdf"

    md_text = src.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(md_text)

    i18n = I18N[lang]
    doc_label = DOC_LABELS[slug][lang]
    section_label = SECTION_LABELS[phase][lang]
    title = doc_label

    wersja = str(metadata.get("wersja", "1.0"))
    stan = str(metadata.get("stan-na", ""))
    version_label = i18n["version_label_template"].format(wersja=wersja, stan=stan)

    assets_prefix = "../" * 4  # dokumenty/{phase}/{slug}/{lang}/index.html → ../../../../assets
    hub_prefix = "../" * 4

    result = {"html": "skipped", "docx": "skipped", "pdf": "skipped"}

    if needs_rebuild(src, html_dst):
        body_html = render_md_body_to_html(src, body)
        lang_switch = build_lang_switch(
            slug=slug, langs=langs, current_lang=lang,
            doc_lang_aria=i18n["doc_lang_aria"],
            no_translations_msg=i18n["no_translations_msg"],
        )
        html_dst.write_text(
            DOC_TEMPLATE.format(
                lang=lang,
                title=title,
                phase=phase,
                slug=slug,
                content=body_html,
                section_label=section_label,
                doc_label=doc_label,
                docs_section=i18n["docs_section"],
                logo_title=i18n["logo_title"],
                downloads_label=i18n["downloads_label"],
                download_docx=i18n["download_docx"],
                download_pdf=i18n["download_pdf"],
                back_to_list=i18n["back_to_list"],
                version_label=version_label,
                meta_html=fmt_meta(metadata),
                lang_switch_html=lang_switch,
                assets_prefix=assets_prefix,
                hub_prefix=hub_prefix,
            ),
            encoding="utf-8",
        )
        result["html"] = "built"

    if needs_rebuild(src, docx_dst):
        render_md_to_docx(src, docx_dst)
        result["docx"] = "built"

    if needs_rebuild(src, pdf_dst):
        body_html = render_md_body_to_html(src, body)
        print_html = PRINT_TEMPLATE.format(
            lang=lang,
            title=title,
            section_label=section_label,
            version_label=version_label,
            content=body_html,
        )
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8",
        ) as tmp:
            tmp.write(print_html)
            tmp_path = Path(tmp.name)
        try:
            render_html_to_pdf(tmp_path, pdf_dst)
        finally:
            tmp_path.unlink(missing_ok=True)
        result["pdf"] = "built"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Pakiet B (50 MD do ~150 plikow).")
    parser.add_argument(
        "--course-source",
        metavar="PATH",
        help="Sciezka do katalogu kursu (zawiera podprojekt-b/). Nadpisuje EGIDA_KURS_ROOT/COURSE_SLUG.",
    )
    parser.add_argument(
        "--course-slug",
        metavar="SLUG",
        help="Slug kursu (np. kurs_tartak). Nadpisuje COURSE_SLUG env var.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="SLUG",
        help="Buduj tylko podane slugi (np. --only umowa-kursu regulamin-kursu polityka-reklamacji)",
    )
    parser.add_argument(
        "--phase",
        nargs="+",
        choices=["B1", "B2", "B3"],
        help="Buduj tylko podane fazy",
    )
    args = parser.parse_args()

    # CLI nadpisuje env vars / defaults
    global KURS, SRC_ROOT, OUT_ROOT, COURSE_SLUG, COURSE_HUB_SLUG
    if args.course_source:
        KURS = Path(args.course_source).resolve()
        SRC_ROOT = KURS / "podprojekt-b"
        if args.course_slug:
            COURSE_SLUG = args.course_slug
            COURSE_HUB_SLUG = COURSE_SLUG.replace("_", "-")
        else:
            COURSE_SLUG = KURS.name
            COURSE_HUB_SLUG = COURSE_SLUG.replace("_", "-")
        OUT_ROOT = WEB_HUB / "public" / COURSE_HUB_SLUG / "dokumenty"
    elif args.course_slug:
        COURSE_SLUG = args.course_slug
        COURSE_HUB_SLUG = COURSE_SLUG.replace("_", "-")
        KURS = EGIDA_KURS_ROOT / COURSE_SLUG
        SRC_ROOT = KURS / "podprojekt-b"
        OUT_ROOT = WEB_HUB / "public" / COURSE_HUB_SLUG / "dokumenty"

    if not SRC_ROOT.exists():
        print(f"FAIL: brak katalogu zrodlowego: {SRC_ROOT}", file=sys.stderr)
        print(f"  EGIDA_KURS_ROOT: {EGIDA_KURS_ROOT}", file=sys.stderr)
        print(f"  COURSE_SLUG: {COURSE_SLUG}", file=sys.stderr)
        print(f"  Sprawdz: --course-source PATH lub --course-slug SLUG lub env var EGIDA_KURS_ROOT.", file=sys.stderr)
        return 2

    docs_to_build = []
    for phase, slug, langs in DOCS:
        if args.phase and phase not in args.phase:
            continue
        if args.only and slug not in args.only:
            continue
        docs_to_build.append(DocBuild(phase=phase, slug=slug, langs=langs))

    if not docs_to_build:
        print("Brak dokumentów do zbudowania (sprawdź --only / --phase).", file=sys.stderr)
        return 1

    print(f"Pakiet B build: {len(docs_to_build)} dokumentow x {{2,4}} jez x 3 formaty")
    print(f"  Course slug: {COURSE_SLUG} (hub: {COURSE_HUB_SLUG})")
    print(f"  Source:      {SRC_ROOT}")
    print(f"  Output:      {OUT_ROOT}")
    print(f"  Pandoc:      {PANDOC}")
    print(f"  wkhtmltopdf: {WKHTMLTOPDF}")
    print(f"  FORCE_REBUILD: {FORCE_REBUILD}")
    print()

    write_dokument_css(WEB_HUB / "public" / "kurs-tartak" / "assets")

    counters = {"built_html": 0, "built_docx": 0, "built_pdf": 0,
                "skipped_html": 0, "skipped_docx": 0, "skipped_pdf": 0,
                "errors": 0}

    for doc in docs_to_build:
        for lang in doc.langs:
            try:
                r = build_one(doc.phase, doc.slug, doc.langs, lang)
                tag = " ".join(f"{k}={v}" for k, v in r.items())
                print(f"  [{doc.phase}/{doc.slug}/{lang}] {tag}")
                for fmt in ("html", "docx", "pdf"):
                    counters[f"{r[fmt]}_{fmt}"] += 1
            except Exception as exc:
                print(f"  ERROR [{doc.phase}/{doc.slug}/{lang}]: {exc}", file=sys.stderr)
                counters["errors"] += 1

    print()
    print("== Podsumowanie ==")
    for k, v in counters.items():
        print(f"  {k}: {v}")
    return 0 if counters["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
