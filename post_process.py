#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
post_process.py: post-processing hubu kursu po build_kurs.py.

Wykonuje 4 kroki na public/{course-hub-slug}/:
  STEP 0: wstrzykuje <script src="../assets/chrome.js"> do kursant/*.html
          (standalone HTML z dist/ kursu nie maja tego inline; rendered MD->HTML
          juz maja przez DOC_TEMPLATE).
  STEP 1: usuwa em-dash (U+2014) ze wszystkich plikow HTML, zamienia na ASCII -.
  STEP 2: wstrzykuje floating banner EGIDA do wszystkich plikow oprocz index.html
          (link powrotu do hubu + brand identification).
  STEP 3: wstrzykuje lesson-chrome (prev/next nav) do trener/M*/*.html z sequencing
          ARTIFACTS w obrebie modulu i cross-module M1->M2->M3.

Konfiguracja (env vars + CLI):
  EGIDA_OUT_DIR    default: <repo>/public          (override katalogu output)
  COURSE_HUB_SLUG  default: kurs-tartak

Wywolanie po build_kurs.py:
  python post_process.py
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--course-hub-slug", default=os.environ.get("COURSE_HUB_SLUG", "kurs-tartak"))
    p.add_argument("--output", help="Override OUT (sciezka do public/<slug>)")
    return p.parse_args()


args = parse_args()
REPO = Path(__file__).resolve().parent
DEFAULT_OUT_ROOT = REPO / "public"
OUT_ROOT = Path(os.environ.get("EGIDA_OUT_DIR", str(DEFAULT_OUT_ROOT)))
OUT = Path(args.output) if args.output else OUT_ROOT / args.course_hub_slug

if not OUT.exists():
    raise SystemExit(f"BLAD: brak {OUT}. Uruchom najpierw build_kurs.py.")

# ============== STEP 0: WSTRZYKNIJ chrome.js DO STANDALONE kursant/ ==============
# Rendered pages (rekrutacja/trener/koordynator) maja chrome.js w DOC_TEMPLATE.
# Standalone kursant/*.html (kopie z dist/) nie, wstrzykujemy recznie przed </body>.
CHROME_SCRIPT = '<script src="../assets/chrome.js"></script>'
kursant_dir = OUT / "kursant"
if kursant_dir.exists():
    for p in kursant_dir.glob("*.html"):
        t = p.read_text(encoding="utf-8")
        if "assets/chrome.js" in t:
            continue
        idx = t.rfind("</body>")
        if idx == -1:
            continue
        t2 = t[:idx] + CHROME_SCRIPT + "\n" + t[idx:]
        p.write_text(t2, encoding="utf-8")
print("STEP 0: chrome.js wstrzyk do kursant/ standalone")

# ============== STEP 1: USUN EM-DASHE ==============
em_total = 0
files_modified = 0
for p in OUT.rglob("*.html"):
    t = p.read_text(encoding="utf-8")
    em_count = t.count("—")
    if em_count:
        t2 = t.replace("—", "-")
        p.write_text(t2, encoding="utf-8")
        em_total += em_count
        files_modified += 1
print(f"STEP 1: usunieto {em_total} em-dashow z {files_modified} plikow")

# ============== STEP 2: DODAJ FLOATING BANNER EGIDA ==============
BANNER_HTML = """
<!-- EGIDA hub return banner (injected) -->
<style id="egida-banner-style">
  body { padding-top: 88px !important; }
  @media (max-width: 640px) {
    body { padding-top: 64px !important; }
  }
  /* Reveal.js prezentacja: nie modyfikujemy body padding, banner i tak fixed top-right */
  body:has(.reveal) { padding-top: 0 !important; }
  html:has(.reveal) { padding-top: 0 !important; }
  #egida-banner {
    position: fixed;
    top: 14px;
    right: 14px;
    z-index: 99999;
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
    font-size: 12px;
    background: rgba(28, 27, 23, 0.95);
    color: #fbfaf6;
    padding: 6px 14px 6px 8px;
    border-radius: 3px;
    box-shadow: 0 2px 10px rgba(28, 27, 23, 0.25);
    display: inline-flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    border: 1px solid rgba(122, 59, 26, 0.5);
    transition: background 0.15s, transform 0.15s, border-color 0.15s;
    max-width: calc(100vw - 28px);
  }
  #egida-banner:hover {
    background: rgba(28, 27, 23, 1);
    border-color: rgba(122, 59, 26, 0.9);
    transform: translateY(-1px);
  }
  #egida-banner .egida-logo {
    height: 48px;
    width: auto;
    background: #fbfaf6;
    border-radius: 2px;
    padding: 4px 8px;
    display: inline-flex;
    align-items: center;
    flex-shrink: 0;
  }
  #egida-banner .egida-logo img {
    height: 100%;
    width: auto;
    display: block;
  }
  #egida-banner .egida-link {
    color: #fbfaf6;
    font-weight: 500;
    letter-spacing: 0.01em;
  }
  #egida-banner .egida-arrow {
    color: #a86a3e;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    font-size: 11px;
    margin-right: 2px;
  }
  #egida-banner-hide {
    background: none;
    border: none;
    color: rgba(217, 212, 197, 0.45);
    cursor: pointer;
    font-size: 15px;
    padding: 0 2px 0 6px;
    line-height: 1;
    margin-left: 4px;
  }
  #egida-banner-hide:hover { color: #fbfaf6; }
  @media (max-width: 640px) {
    #egida-banner { top: 10px; right: 10px; font-size: 11px; padding: 5px 12px 5px 6px; gap: 8px; }
    #egida-banner .egida-logo { height: 38px; padding: 3px 6px; }
  }
</style>
<a id="egida-banner" href="../index.html" title="Powrot do hubu kursu tartakowego EGIDA">
  <span class="egida-logo"><img src="__LOGO_PATH__" alt="Logo Fundacji EGIDA"></span>
  <span class="egida-arrow">&larr;</span>
  <span class="egida-link">Menu kursu</span>
</a>
<script>
  (function() {
    var b = document.getElementById('egida-banner');
    if (!b) return;
    // Opcjonalnie: dodaj malenki przycisk ukrycia bannera (pamieta w sessionStorage)
    var hide = document.createElement('button');
    hide.id = 'egida-banner-hide';
    hide.setAttribute('aria-label', 'Ukryj baner');
    hide.textContent = 'x';
    hide.onclick = function(e) {
      e.preventDefault();
      b.style.display = 'none';
      try { sessionStorage.setItem('egida-banner-hidden', '1'); } catch (ex) {}
    };
    b.appendChild(hide);
    try {
      if (sessionStorage.getItem('egida-banner-hidden') === '1') {
        b.style.display = 'none';
      }
    } catch (ex) {}
  })();
</script>
<!-- /EGIDA hub return banner -->
"""

standalone = [p for p in OUT.rglob("*.html") if p != OUT / "index.html"]
print(f"STEP 2: wstrzykuje banner EGIDA do {len(standalone)} plikow (oprocz index.html hubu)")

for p in standalone:
    t = p.read_text(encoding="utf-8")
    if "egida-banner" in t:
        print(f"  SKIP {p.relative_to(OUT)}: banner juz wstrzykniety")
        continue
    idx = t.find("<body")
    if idx == -1:
        print(f"  SKIP {p.relative_to(OUT)}: brak <body>")
        continue
    body_end = t.find(">", idx)
    if body_end == -1:
        print(f"  SKIP {p.relative_to(OUT)}: niekompletny <body>")
        continue
    depth = len(p.relative_to(OUT).parts) - 1
    href = ("../" * depth) + "index.html" if depth else "index.html"
    logo_path = ("../" * depth) + "assets/egida-logo-wide-128.png" if depth else "assets/egida-logo-wide-128.png"
    banner = BANNER_HTML.replace('href="../index.html"', f'href="{href}"')
    banner = banner.replace("__LOGO_PATH__", logo_path)
    insert_at = body_end + 1
    t2 = t[:insert_at] + banner + t[insert_at:]
    p.write_text(t2, encoding="utf-8")
    print(f"  OK   {p.relative_to(OUT)} (href={href})")

# ============== STEP 3: LESSON-CHROME (prev/next w trener/) ==============
ARTIFACTS = [
    {"slug": "wytyczne-trenera",
     "labels": {"pl": "Wytyczne dla trenera", "en": "Trainer guidelines",
                "es": "Guía para formadores", "uk": "Настанови для тренера"},
     "multilang": False},
    {"slug": "cwiczenia-teoretyczne",
     "labels": {"pl": "Ćwiczenia teoretyczne", "en": "Theoretical exercises",
                "es": "Ejercicios teóricos", "uk": "Теоретичні вправи"},
     "multilang": True},
    {"slug": "quiz-uzupelniajacy",
     "labels": {"pl": "Quiz uzupełniający", "en": "Supplementary quiz",
                "es": "Cuestionario complementario", "uk": "Допоміжний квіз"},
     "multilang": True},
    {"slug": "scenariusze-praktyczne",
     "labels": {"pl": "Scenariusze praktyczne", "en": "Practical scenarios",
                "es": "Escenarios prácticos", "uk": "Практичні сценарії"},
     "multilang": False},
]

UI_LABELS = {
    "pl": {"prev": "Poprzedni", "next": "Następny", "of": "z", "artefact": "Artefakt", "first": "Początek", "last": "Koniec"},
    "en": {"prev": "Previous", "next": "Next", "of": "of", "artefact": "Artefact", "first": "First", "last": "Last"},
    "es": {"prev": "Anterior", "next": "Siguiente", "of": "de", "artefact": "Artefacto", "first": "Primero", "last": "Último"},
    "uk": {"prev": "Попередній", "next": "Наступний", "of": "з", "artefact": "Артефакт", "first": "Початок", "last": "Кінець"},
}


def parse_trener_filename(filename: str):
    name = filename.replace(".html", "")
    for lang in ("pl", "en", "es", "uk"):
        if name.endswith(f"-{lang}"):
            return (name[:-3], lang)
    return (name, None)


def build_artifact_href(slug: str, current_lang, target_artifact):
    if target_artifact["multilang"]:
        use_lang = current_lang if current_lang else "pl"
        return f"{target_artifact['slug']}-{use_lang}.html"
    return f"{target_artifact['slug']}.html"


def build_lesson_chrome(module: str, slug: str, current_lang) -> str:
    idx = next((i for i, a in enumerate(ARTIFACTS) if a["slug"] == slug), None)
    if idx is None:
        return ""
    ui_lang = current_lang or "pl"
    ui = UI_LABELS[ui_lang]
    total = len(ARTIFACTS)

    if idx > 0:
        prev_art = ARTIFACTS[idx - 1]
        prev_href = build_artifact_href(slug, current_lang, prev_art)
        prev_label = prev_art["labels"][ui_lang]
        prev_html = f'<a class="lc-prev" href="{prev_href}"><span class="lc-arrow" aria-hidden="true">&larr;</span> <span class="lc-label">{prev_label}</span></a>'
    elif module != "M1":
        prev_module = "M" + str(int(module[1]) - 1)
        last_art = ARTIFACTS[-1]
        prev_href = f"../{prev_module}/" + build_artifact_href(slug, current_lang, last_art)
        prev_label = f'{prev_module} &middot; {last_art["labels"][ui_lang]}'
        prev_html = f'<a class="lc-prev" href="{prev_href}"><span class="lc-arrow" aria-hidden="true">&larr;</span> <span class="lc-label">{prev_label}</span></a>'
    else:
        prev_html = f'<span class="lc-prev lc-disabled"><span class="lc-arrow" aria-hidden="true">&larr;</span> <span class="lc-label">{ui["first"]}</span></span>'

    if idx < total - 1:
        next_art = ARTIFACTS[idx + 1]
        next_href = build_artifact_href(slug, current_lang, next_art)
        next_label = next_art["labels"][ui_lang]
        next_html = f'<a class="lc-next" href="{next_href}"><span class="lc-label">{next_label}</span> <span class="lc-arrow" aria-hidden="true">&rarr;</span></a>'
    elif module != "M3":
        next_module = "M" + str(int(module[1]) + 1)
        first_art = ARTIFACTS[0]
        next_href = f"../{next_module}/" + build_artifact_href(slug, current_lang, first_art)
        next_label = f'{next_module} &middot; {first_art["labels"][ui_lang]}'
        next_html = f'<a class="lc-next" href="{next_href}"><span class="lc-label">{next_label}</span> <span class="lc-arrow" aria-hidden="true">&rarr;</span></a>'
    else:
        next_html = f'<span class="lc-next lc-disabled"><span class="lc-label">{ui["last"]}</span> <span class="lc-arrow" aria-hidden="true">&rarr;</span></span>'

    counter = f'{ui["artefact"]} {idx + 1} {ui["of"]} {total} &middot; {module}'

    return (
        f'<nav class="lesson-chrome" aria-label="{ui["prev"]} / {ui["next"]}">\n'
        f'  {prev_html}\n'
        f'  <span class="lc-counter">{counter}</span>\n'
        f'  {next_html}\n'
        f'</nav>\n'
    )


LESSON_CHROME_RE = re.compile(r'\s*<nav class="lesson-chrome".*?</nav>\s*', re.DOTALL)
trener_dir = OUT / "trener"
trener_files = list(trener_dir.rglob("*.html")) if trener_dir.exists() else []
chrome_count = 0
print()
print(f"STEP 3: wstrzykuje lesson-chrome do plikow trener/ ({len(trener_files)} kandydatow)")
for p in trener_files:
    module = p.parent.name
    if module not in ("M1", "M2", "M3"):
        continue
    slug, lang = parse_trener_filename(p.name)
    if not any(a["slug"] == slug for a in ARTIFACTS):
        print(f"  SKIP {p.relative_to(OUT)}: nieznany slug")
        continue
    chrome_html = build_lesson_chrome(module, slug, lang)
    t = p.read_text(encoding="utf-8")
    if "lesson-chrome" in t:
        t = LESSON_CHROME_RE.sub("\n", t, count=1)
    idx_h = t.find("</header>")
    if idx_h == -1:
        print(f"  SKIP {p.relative_to(OUT)}: brak </header>")
        continue
    insert_at = idx_h + len("</header>")
    t2 = t[:insert_at] + "\n  " + chrome_html + t[insert_at:]
    p.write_text(t2, encoding="utf-8")
    chrome_count += 1
print(f"  OK: lesson-chrome wstrzykniety do {chrome_count} plikow")

# ============== WERYFIKACJA ==============
print()
print("=== Weryfikacja po post-processingu ===")
em_total_after = sum(p.read_text(encoding="utf-8").count("—") for p in OUT.rglob("*.html"))
banner_count = sum(1 for p in standalone if "egida-banner" in p.read_text(encoding="utf-8"))
chrome_after = sum(1 for p in trener_files if "lesson-chrome" in p.read_text(encoding="utf-8"))
print(f"Em-dashow pozostalo: {em_total_after} (cel: 0)")
print(f"Plikow standalone z bannerem EGIDA: {banner_count}/{len(standalone)}")
print(f"Plikow trener/ z lesson-chrome: {chrome_after}/{len(trener_files)}")
