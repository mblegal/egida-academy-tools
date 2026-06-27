#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_kurs_bud.py : pipeline buildu panelu kursu prac ogolnobudowlanych (EGIDA).

Wejscie : src/<doc>/<lang>.md   (doc: program-ogolny, program-szczegolowy, scenariusze-blokow, dziennik-kursu; lang: pl,en,es)
Wyjscie : dist/egida-kurs-bud/
            index.html                         (hub: PIN gate 6-cyfr + 4 karty x 3 jez x 3 formaty)
            assets/ (panel.css, egida.css, dokument.css, chrome-bud.js, logo)
            <doc>/<lang>/index.html            (podglad online + downloads)
            <doc>/<doc>-<lang>.docx            (pandoc)
            <doc>/<doc>-<lang>.pdf             (wkhtmltopdf)

Zaleznosci: pandoc 3.x, wkhtmltopdf 0.12+.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
TEMPLATES = HERE / "templates"
ASSETS = HERE / "assets"
OUT = HERE / "dist" / "egida-kurs-bud"

PANDOC = shutil.which("pandoc") or "pandoc"
WK = None
for cand in (shutil.which("wkhtmltopdf"), r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"):
    if cand and Path(cand).exists():
        WK = cand
        break
if WK is None:
    WK = "wkhtmltopdf"

LANGS = ["pl", "en", "es"]
LANG_NAMES = {"pl": "PL", "en": "EN", "es": "ES"}

# (katalog/slug, klucz, tytuly per jezyk)
DOCS = [
    ("program-ogolny", "ogolny", {
        "pl": "Program ogólny kursu", "en": "General course programme", "es": "Programa general del curso"}),
    ("program-szczegolowy", "szczegolowy", {
        "pl": "Program szczegółowy kursu", "en": "Detailed course programme", "es": "Programa detallado del curso"}),
    ("scenariusze-blokow", "scen", {
        "pl": "Scenariusze bloków zajęć", "en": "Lesson-block scenarios", "es": "Escenarios de los bloques de clase"}),
    ("dziennik-kursu", "dziennik", {
        "pl": "Dziennik kursu", "en": "Course journal", "es": "Diario del curso"}),
]

COURSE_NAME = {
    "pl": "Kurs prac ogólnobudowlanych - Fundacja EGIDA",
    "en": "General construction course - EGIDA Foundation",
    "es": "Curso de construcción general - Fundación EGIDA",
}
# i18n chrome podstron dokumentu
DOC_I18N = {
    "pl": {"hub": "Kurs prac ogólnobudowlanych EGIDA", "docs": "Dokumenty kursu",
           "dl_docx": "Pobierz jako DOCX (do edycji)", "dl_pdf": "Pobierz jako PDF (do druku)",
           "back": "&larr; Powrót do panelu kursu", "dl_label": "Pobierz dokument",
           "lang_aria": "Język dokumentu", "logo_title": "Powrót do panelu Fundacji EGIDA"},
    "en": {"hub": "EGIDA general construction course", "docs": "Course documents",
           "dl_docx": "Download as DOCX (editable)", "dl_pdf": "Download as PDF (printable)",
           "back": "&larr; Back to course panel", "dl_label": "Download document",
           "lang_aria": "Document language", "logo_title": "Back to EGIDA Foundation panel"},
    "es": {"hub": "Curso de construcción general EGIDA", "docs": "Documentos del curso",
           "dl_docx": "Descargar como DOCX (editable)", "dl_pdf": "Descargar como PDF (imprimible)",
           "back": "&larr; Volver al panel del curso", "dl_label": "Descargar documento",
           "lang_aria": "Idioma del documento", "logo_title": "Volver al panel de la Fundación EGIDA"},
}
PRINT_MARK = {
    "pl": "Fundacja EGIDA - Kurs prac ogólnobudowlanych (kostka brukowa + BHP)",
    "en": "EGIDA Foundation - General construction course (paving + OSH)",
    "es": "Fundación EGIDA - Curso de construcción general (adoquines + SST)",
}
FOOT_ADDR = {
    "pl": "Fundacja pomocy prawnej EGIDA - Opole - kurs bezpłatny dla cudzoziemców - współfinansowanie EFS+",
    "en": "EGIDA Foundation for Legal Aid - Opole - free course for foreigners - co-financed by ESF+",
    "es": "Fundación de asistencia jurídica EGIDA - Opole - curso gratuito para extranjeros - cofinanciación FSE+",
}

# ---------------------------------------------------------------------------
DOC_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f6f4ef">
<title>{title} - {course}</title>
<link rel="stylesheet" href="../../assets/egida.css">
<link rel="stylesheet" href="../../assets/dokument.css">
<link rel="icon" type="image/png" href="../../assets/egida-logo-64.png">
</head>
<body>
<div class="doc-wrap">
  <header class="doc-header">
    <a class="doc-logo" href="../../index.html" title="{logo_title}">
      <img src="../../assets/egida-logo-wide-128.png" alt="Logo Fundacji EGIDA">
    </a>
    <div class="doc-header-body">
      <div class="doc-breadcrumb">
        <a href="../../index.html">{hub}</a> /
        {docs} /
        {title}
      </div>
      <h1 class="doc-title">{title}</h1>
    </div>
{lang_switch}
  </header>

  <main class="doc-content">
{content}
  </main>

  <section class="doc-downloads" aria-label="{dl_label}">
    <a class="doc-download doc-download-docx" href="../{slug}-{lang}.docx" download>
      <span class="doc-download-icon" aria-hidden="true">DOCX</span>
      <span class="doc-download-label">{dl_docx}</span>
    </a>
    <a class="doc-download doc-download-pdf" href="../{slug}-{lang}.pdf" download>
      <span class="doc-download-icon" aria-hidden="true">PDF</span>
      <span class="doc-download-label">{dl_pdf}</span>
    </a>
  </section>

  <footer class="doc-footer">
    <span class="egida-mark">{course}</span>
    <a href="../../index.html">{back}</a>
  </footer>
</div>
<script src="../../assets/chrome-bud.js"></script>
</body>
</html>
"""

PRINT_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
@page {{ margin: 17mm 16mm 18mm 16mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "Source Serif 4","Source Serif Pro",Georgia,"Times New Roman",serif; font-size: 10.5pt; line-height: 1.5; color: #1c1b17; margin: 0; }}
.print-header {{ border-bottom: 2px solid #7a3b1a; padding-bottom: 0.7em; margin-bottom: 1.1em; }}
.print-mark {{ font-family: Inter,Arial,sans-serif; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.1em; color: #7a3b1a; }}
.print-title {{ font-size: 17pt; font-weight: 700; margin: 0.2em 0 0; line-height: 1.2; }}
h1,h2,h3,h4 {{ font-family: "Source Serif 4",Georgia,serif; font-weight: 700; page-break-after: avoid; color: #1c1b17; }}
h1 {{ font-size: 14pt; margin: 1.3em 0 0.5em; color: #7a3b1a; }}
h2 {{ font-size: 12.5pt; margin: 1.1em 0 0.45em; color: #7a3b1a; border-bottom: 1px solid #e0dccd; padding-bottom: 0.15em; }}
h3 {{ font-size: 11pt; margin: 0.9em 0 0.35em; color: #a86a3e; }}
h4 {{ font-size: 10.5pt; margin: 0.8em 0 0.3em; }}
p {{ margin: 0.35em 0 0.6em; }}
table {{ border-collapse: collapse; width: 100%; margin: 0.6em 0; font-size: 9pt; page-break-inside: auto; }}
th,td {{ border: 1px solid #d9d4c5; padding: 0.32em 0.45em; vertical-align: top; text-align: left; word-break: break-word; }}
th {{ background: #f1ede2; font-weight: 600; font-family: Inter,Arial,sans-serif; }}
tr {{ page-break-inside: avoid; }}
ul,ol {{ margin: 0.35em 0 0.6em 1.3em; padding: 0; }}
li {{ margin: 0.15em 0; }}
hr {{ border: none; border-top: 1px solid #d9d4c5; margin: 1.2em 0; }}
blockquote {{ margin: 0.7em 0.8em; padding: 0.3em 0.9em; border-left: 3px solid #d9d4c5; color: #3a3833; }}
strong {{ color: #5a2f15; }}
code {{ font-family: Consolas,monospace; font-size: 0.9em; background: #f1ede2; padding: 0.05em 0.3em; border-radius: 2px; }}
.print-footer {{ margin-top: 1.6em; padding-top: 0.5em; border-top: 1px solid #d9d4c5; font-family: Inter,Arial,sans-serif; font-size: 7.5pt; color: #5a574e; text-align: center; }}
</style>
</head>
<body>
<header class="print-header">
  <div class="print-mark">{mark}</div>
  <h1 class="print-title">{title}</h1>
</header>
<main>
{content}
</main>
<footer class="print-footer">{addr}</footer>
</body>
</html>
"""


def build_lang_switch(slug_dir: str, current: str, aria: str) -> str:
    parts = [f'    <nav class="doc-lang-switch" aria-label="{aria}">']
    for L in LANGS:
        is_cur = (L == current)
        cls = ' class="on" aria-current="page"' if is_cur else ""
        href = "#" if is_cur else f"../{L}/index.html"
        parts.append(f'      <a data-lang="{L}" href="{href}"{cls} hreflang="{L}">{LANG_NAMES[L]}</a>')
    parts.append("    </nav>")
    return "\n".join(parts)


def strip_leading_h1(md: str):
    """Usuwa pierwszy '# Tytul' (tytul pokazuje header). Zwraca (tytul_or_None, reszta)."""
    md = md.lstrip("﻿").lstrip()
    m = re.match(r"^#\s+(.+?)\s*\n", md)
    if m:
        return m.group(1).strip(), md[m.end():].lstrip("\n")
    return None, md


def md_body_to_html(body: str) -> str:
    r = subprocess.run(
        [PANDOC, "-f", "markdown+pipe_tables+yaml_metadata_block-implicit_figures",
         "-t", "html5", "--no-highlight"],
        input=body, encoding="utf-8", capture_output=True, check=True)
    return r.stdout


def md_to_docx(src_md: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([PANDOC, "-f", "markdown+pipe_tables-implicit_figures", "-t", "docx",
                    str(src_md), "-o", str(dst)], check=True)


def html_to_pdf(html_path: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([WK, "--quiet", "--enable-local-file-access", "--encoding", "UTF-8",
                    "--print-media-type",
                    "--margin-top", "16mm", "--margin-bottom", "16mm",
                    "--margin-left", "14mm", "--margin-right", "14mm",
                    str(html_path), str(dst)], check=True)


def copy_assets() -> None:
    a = OUT / "assets"
    a.mkdir(parents=True, exist_ok=True)
    for f in ("panel.css", "egida.css", "chrome-bud.js"):
        shutil.copy2(TEMPLATES / f, a / f)
    write_dokument_css(a)
    for logo in ASSETS.glob("egida-logo-*.png"):
        shutil.copy2(logo, a / logo.name)


def write_dokument_css(a: Path) -> None:
    css = """/* dokument.css : sekcja downloads + drobne dodatki dla podstron */
.doc-downloads { display:flex; gap:1rem; margin:2.5rem 0 1.5rem; padding:1.3rem; background:var(--color-bg,#fbfaf6); border:1px solid var(--color-line,#d9d4c5); border-radius:6px; flex-wrap:wrap; }
.doc-download { display:inline-flex; align-items:center; gap:0.7rem; padding:0.7rem 1.1rem; background:#fff; border:1px solid var(--color-line,#d9d4c5); border-radius:5px; text-decoration:none; color:var(--color-text,#1c1b17); font-weight:500; transition:border-color .15s,background .15s; }
.doc-download:hover { border-color:var(--color-navy,#7a3b1a); background:var(--color-bg,#fbfaf6); }
.doc-download-icon { display:inline-block; padding:0.22rem 0.5rem; color:#fff; font-size:0.72rem; font-weight:700; letter-spacing:0.04em; border-radius:3px; }
.doc-download-docx .doc-download-icon { background:#2f4858; }
.doc-download-pdf .doc-download-icon { background:#7a3b1a; }
.doc-download-label { font-size:0.92rem; }
@media (max-width:640px){ .doc-downloads{flex-direction:column;} .doc-download{width:100%; justify-content:center;} }
@media print { .doc-downloads,.doc-lang-switch,.doc-footer a { display:none !important; } .doc-wrap{padding:0;} }
"""
    (a / "dokument.css").write_text(css, encoding="utf-8")


def build_doc(dir_slug: str, key: str, titles: dict) -> dict:
    res = {}
    for lang in LANGS:
        src_md = SRC / dir_slug / f"{lang}.md"
        if not src_md.exists():
            res[lang] = "MISSING-SRC"
            continue
        raw = src_md.read_text(encoding="utf-8")
        _, body = strip_leading_h1(raw)
        title = titles[lang]
        i18n = DOC_I18N[lang]

        out_dir = OUT / dir_slug
        html_dir = out_dir / lang
        html_dir.mkdir(parents=True, exist_ok=True)

        # HTML view
        body_html = md_body_to_html(body)
        html = DOC_TEMPLATE.format(
            lang=lang, title=title, course=COURSE_NAME[lang],
            hub=i18n["hub"], docs=i18n["docs"], slug=dir_slug,
            content=body_html, lang_switch=build_lang_switch(dir_slug, lang, i18n["lang_aria"]),
            dl_label=i18n["dl_label"], dl_docx=i18n["dl_docx"], dl_pdf=i18n["dl_pdf"],
            back=i18n["back"], logo_title=i18n["logo_title"])
        (html_dir / "index.html").write_text(html, encoding="utf-8")

        # DOCX
        md_to_docx(src_md, out_dir / f"{dir_slug}-{lang}.docx")

        # PDF
        print_html = PRINT_TEMPLATE.format(lang=lang, title=title, mark=PRINT_MARK[lang],
                                           content=body_html, addr=FOOT_ADDR[lang])
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(print_html)
            tmp_path = Path(tmp.name)
        try:
            html_to_pdf(tmp_path, out_dir / f"{dir_slug}-{lang}.pdf")
        finally:
            tmp_path.unlink(missing_ok=True)
        res[lang] = "OK"
    return res


def build_index() -> None:
    cards = []
    for dir_slug, key, _titles in DOCS:
        rows = []
        for lang in LANGS:
            links = (
                f'<a class="flink flink--html" href="{dir_slug}/{lang}/index.html"><span class="flink__tag">HTML</span>online</a>'
                f'<a class="flink flink--docx" href="{dir_slug}/{dir_slug}-{lang}.docx" download><span class="flink__tag">DOCX</span>Word</a>'
                f'<a class="flink flink--pdf" href="{dir_slug}/{dir_slug}-{lang}.pdf" download><span class="flink__tag">PDF</span>PDF</a>'
            )
            rows.append(
                f'        <div class="langrow" data-lang="{lang}">\n'
                f'          <span class="langrow__lang">{LANG_NAMES[lang]}</span>\n'
                f'          <span class="langrow__links">{links}</span>\n'
                f'        </div>')
        rows_html = "\n".join(rows)
        cards.append(
            f'      <article class="dcard">\n'
            f'        <div class="dcard__eye" data-i18n="doc.{key}.eye"></div>\n'
            f'        <h3 class="dcard__title" data-i18n="doc.{key}.title"></h3>\n'
            f'        <p class="dcard__desc" data-i18n="doc.{key}.desc"></p>\n'
            f'{rows_html}\n'
            f'      </article>')
    cards_html = "\n".join(cards)

    index = INDEX_TEMPLATE.replace("__CARDS__", cards_html).replace("__CB__", str(int(time.time())))
    (OUT / "index.html").write_text(index, encoding="utf-8")


INDEX_TEMPLATE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f6f4ef">
<title>Kurs prac ogólnobudowlanych - Fundacja EGIDA</title>
<link rel="stylesheet" href="assets/panel.css?v=__CB__">
<link rel="icon" type="image/png" href="assets/egida-logo-64.png">
</head>
<body class="hub-locked">
<a class="skip-link" href="#docs" data-i18n="hdr.skip">Przejdź do treści</a>

<!-- PIN GATE -->
<div class="pin-screen" id="pin-screen" role="dialog" aria-modal="true" aria-labelledby="pin-title">
  <div class="pin-card">
    <div class="pin-card__logo"><img src="assets/egida-logo-wide-256.png" alt="Logo Fundacji EGIDA"></div>
    <div class="pin-card__eyebrow" data-i18n="pin.eyebrow">Dostęp PIN</div>
    <h1 class="pin-card__title" id="pin-title" data-i18n="pin.title_html">Kurs prac ogólnobudowlanych<br><em>Fundacja EGIDA</em></h1>
    <p class="pin-card__lead" data-i18n="pin.lead">Materiały kursu są chronione kodem PIN.</p>
    <div class="pin-fields" role="group" aria-label="Kod PIN">
      <input type="tel" inputmode="numeric" maxlength="1" aria-label="cyfra 1">
      <input type="tel" inputmode="numeric" maxlength="1" aria-label="cyfra 2">
      <input type="tel" inputmode="numeric" maxlength="1" aria-label="cyfra 3">
      <input type="tel" inputmode="numeric" maxlength="1" aria-label="cyfra 4">
      <input type="tel" inputmode="numeric" maxlength="1" aria-label="cyfra 5">
      <input type="tel" inputmode="numeric" maxlength="1" aria-label="cyfra 6">
    </div>
    <div class="pin-msg" role="status" aria-live="polite"></div>
    <div class="pin-footnote" data-i18n="pin.footnote_html"></div>
  </div>
</div>

<div class="hub-wrap">
  <header class="site-header">
    <div class="site-header__row">
      <a class="site-header__brand" href="index.html">
        <span class="site-header__logo"><img src="assets/egida-logo-wide-128.png" alt="Logo Fundacji EGIDA"></span>
        <span class="site-header__title">
          <span class="site-header__eyebrow" data-i18n="hdr.eyebrow">Fundacja EGIDA</span>
          <span class="site-header__name" data-i18n="hdr.name_html">Prace <em>ogólnobudowlane</em></span>
        </span>
      </a>
      <div class="site-header__spacer"></div>
      <span class="pin-state" data-i18n="hdr.pin_state">Dostęp aktywny</span>
      <nav class="lang-switch" aria-label="Jezyk" data-i18n-attr="aria-label:lang.label">
        <button type="button" data-lang="pl" aria-pressed="false">PL</button>
        <button type="button" data-lang="en" aria-pressed="false">EN</button>
        <button type="button" data-lang="es" aria-pressed="false">ES</button>
      </nav>
    </div>
  </header>

  <section class="hero">
    <div class="hero__eyebrow" data-i18n="hero.eyebrow"></div>
    <h1 class="hero__title" data-i18n="hero.title_html"></h1>
    <div class="hero__sub" data-i18n="hero.sub"></div>
    <p class="hero__lead" data-i18n="hero.lead"></p>
    <div class="facts">
      <span class="fact" data-i18n="fact.weeks"></span>
      <span class="fact" data-i18n="fact.site"></span>
      <span class="fact" data-i18n="fact.langs"></span>
      <span class="fact fact--safety" data-i18n="fact.bhp"></span>
      <span class="fact" data-i18n="fact.job"></span>
    </div>
  </section>

  <main id="docs">
    <h2 class="hero__title" style="font-size:1.5rem;margin:2.4rem 0 0.3rem" data-i18n="docs.heading">Dokumenty kursu</h2>
    <p class="hero__lead" data-i18n="docs.sub"></p>
    <div class="docs">
__CARDS__
    </div>

    <div class="strip">
      <h3 data-i18n="strip.title"></h3>
      <p data-i18n="strip.body"></p>
    </div>
  </main>

  <footer class="site-footer">
    <p class="site-footer__disclaimer" data-i18n="footer.disclaimer_html"></p>
    <div class="site-footer__logos">
      <span class="logo-ph"><img src="assets/egida-logo-64.png" alt="">Fundacja EGIDA</span>
    </div>
  </footer>
</div>

<script src="assets/chrome-bud.js?v=__CB__"></script>
</body>
</html>
"""


def validate() -> int:
    problems = 0
    EM = chr(0x2014)  # em-dash (zakazany w outputach) - wykrywany, nie wpisany doslownie
    html_files = list(OUT.rglob("*.html"))
    for f in html_files:
        t = f.read_text(encoding="utf-8")
        em = t.count(EM)
        if em:
            print(f"  EM-DASH x{em}: {f.relative_to(OUT)}")
            problems += 1
    # pliki obecne?
    for dir_slug, key, _t in DOCS:
        for lang in LANGS:
            for ext, sub in (("index.html", f"{lang}/index.html"),
                             (".docx", f"{dir_slug}-{lang}.docx"),
                             (".pdf", f"{dir_slug}-{lang}.pdf")):
                p = OUT / dir_slug / sub
                if not p.exists() or p.stat().st_size == 0:
                    print(f"  MISSING/EMPTY: {p.relative_to(OUT)}")
                    problems += 1
    # diakrytyki PL w pliku pl
    plpath = OUT / "program-ogolny" / "pl" / "index.html"
    if plpath.exists():
        if not re.search(r"[ąćęłńóśźż]", plpath.read_text(encoding="utf-8")):
            print("  WARN: brak polskich diakrytykow w program-ogolny/pl")
            problems += 1
    return problems


def main() -> int:
    if not SRC.exists():
        print(f"BLAD: brak {SRC}", file=sys.stderr)
        return 2
    print(f"pandoc: {PANDOC}")
    print(f"wkhtmltopdf: {WK}")
    OUT.mkdir(parents=True, exist_ok=True)
    copy_assets()
    print("OK assets")
    for dir_slug, key, titles in DOCS:
        r = build_doc(dir_slug, key, titles)
        print(f"  {dir_slug}: " + " ".join(f"{k}={v}" for k, v in r.items()))
    build_index()
    print("OK index.html")
    print()
    print("=== walidacja ===")
    p = validate()
    if p == 0:
        print("OK: brak problemow")
    else:
        print(f"UWAGA: {p} problemow")
    print(f"\nOutput: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
