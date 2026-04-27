#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_validate_kurs_dist.py: walidator outputu Pakietu A (47+ plikow HTML + assets).

Sprawdza public/<course-hub-slug>/:
  * struktura katalogow (kursant/, rekrutacja/, trener/M{1,2,3}/, assets/)
  * obecnosc oczekiwanych plikow (kurs-Mn, prezentacja-Mn, programy, artefakty)
  * em-dash (UTF-8) = 0 we wszystkich HTML
  * chrome.js obecny w kursant/* (post_process STEP 0)
  * egida-banner obecny w plikach oprocz index.html (STEP 2)
  * lesson-chrome obecny w trener/* (STEP 3)
  * assets: chrome.css, chrome.js, egida.css, 3+ logo PNG

Uzycie: python scripts/_validate_kurs_dist.py [--course-hub-slug X] [--quiet]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--course-hub-slug", default=os.environ.get("COURSE_HUB_SLUG", "kurs-tartak"))
    p.add_argument("--output", help="Override OUT (sciezka do public/<slug>)")
    p.add_argument("--quiet", action="store_true", help="Tylko bledy + summary")
    return p.parse_args()


args = parse_args()
DEFAULT_OUT_ROOT = REPO / "public"
OUT_ROOT = Path(os.environ.get("EGIDA_OUT_DIR", str(DEFAULT_OUT_ROOT)))
OUT = Path(args.output) if args.output else OUT_ROOT / args.course_hub_slug

if not OUT.exists():
    print(f"BLAD: brak {OUT}")
    sys.exit(1)


def log(msg: str):
    if not args.quiet:
        print(msg)


errors: list[str] = []


def err(msg: str):
    errors.append(msg)
    print(f"  ! {msg}")


# ============== STRUKTURA KATALOGOW ==============
log(f"=== Walidacja {OUT} ===\n")
log("STEP 1: struktura katalogow")
expected_dirs = ["kursant", "rekrutacja", "assets", "trener/M1", "trener/M2", "trener/M3"]
for d in expected_dirs:
    if not (OUT / d).exists():
        err(f"brak katalogu: {d}")
    else:
        log(f"  OK   {d}/")

# ============== ASSETS ==============
log("\nSTEP 2: assets/")
expected_assets = ["chrome.css", "chrome.js", "egida.css", "egida-logo-64.png", "egida-logo-300.png", "egida-logo-wide-128.png"]
for a in expected_assets:
    p = OUT / "assets" / a
    if not p.exists():
        err(f"brak assetu: assets/{a}")
    elif p.stat().st_size < 100:
        err(f"asset za maly: assets/{a} ({p.stat().st_size} B)")
    else:
        log(f"  OK   assets/{a} ({p.stat().st_size:,} B)")

# ============== KURSANT (6 plikow standalone) ==============
log("\nSTEP 3: kursant/ (6 plikow standalone)")
expected_kursant = []
for m in ("M1", "M2", "M3"):
    expected_kursant.append(f"kurs-{m}.html")
    expected_kursant.append(f"prezentacja-{m}.html")
for fn in expected_kursant:
    p = OUT / "kursant" / fn
    if not p.exists():
        err(f"brak: kursant/{fn}")
        continue
    if p.stat().st_size < 100_000:
        err(f"kursant/{fn} za maly: {p.stat().st_size:,} B")
    t = p.read_text(encoding="utf-8")
    if "assets/chrome.js" not in t:
        err(f"kursant/{fn}: brak chrome.js (STEP 0 post_process)")
    if "egida-banner" not in t:
        err(f"kursant/{fn}: brak egida-banner (STEP 2 post_process)")
    log(f"  OK   kursant/{fn} ({p.stat().st_size:,} B)")

# ============== REKRUTACJA (5 plikow) ==============
log("\nSTEP 4: rekrutacja/ (5 plikow)")
expected_rekrut = ["program-ogolny.html"]
for L in ("pl", "en", "es", "uk"):
    expected_rekrut.append(f"program-szczegolowy-{L}.html")
for fn in expected_rekrut:
    p = OUT / "rekrutacja" / fn
    if not p.exists():
        err(f"brak: rekrutacja/{fn}")
        continue
    t = p.read_text(encoding="utf-8")
    if 'class="doc-content"' not in t:
        err(f"rekrutacja/{fn}: brak doc-content")
    if "egida-banner" not in t:
        err(f"rekrutacja/{fn}: brak egida-banner")
    log(f"  OK   rekrutacja/{fn} ({p.stat().st_size:,} B)")

# ============== TRENER (30 plikow) ==============
log("\nSTEP 5: trener/M{1,2,3}/ (10 plikow per modul)")
expected_trener_per_m = []
for kind in ("quiz-uzupelniajacy", "cwiczenia-teoretyczne"):
    for L in ("pl", "en", "es", "uk"):
        expected_trener_per_m.append(f"{kind}-{L}.html")
for kind in ("scenariusze-praktyczne", "wytyczne-trenera"):
    expected_trener_per_m.append(f"{kind}.html")

for m in ("M1", "M2", "M3"):
    log(f"  Modul {m}:")
    for fn in expected_trener_per_m:
        p = OUT / "trener" / m / fn
        if not p.exists():
            err(f"brak: trener/{m}/{fn}")
            continue
        t = p.read_text(encoding="utf-8")
        if "lesson-chrome" not in t:
            err(f"trener/{m}/{fn}: brak lesson-chrome (STEP 3 post_process)")
        if "egida-banner" not in t:
            err(f"trener/{m}/{fn}: brak egida-banner")
        log(f"    OK   {fn}")

# ============== INDEX.HTML ==============
log("\nSTEP 6: index.html (hub)")
idx = OUT / "index.html"
if not idx.exists():
    err("brak index.html")
else:
    t = idx.read_text(encoding="utf-8")
    if t.count("—"):
        err(f"index.html: {t.count('—')} em-dashow")
    for required in ("pin-screen", "pin-card", "lang-switch", "role-nav", "kpi-row",
                     "kursant", "trener", "rekrutacja", "projekt", "dokumenty"):
        if required not in t:
            err(f"index.html: brak '{required}'")
    log(f"  OK   index.html ({idx.stat().st_size:,} B)")

# ============== EM-DASH GLOBAL CHECK ==============
log("\nSTEP 7: em-dash (cel: 0 we wszystkich HTML)")
em_total = 0
em_files = []
for p in OUT.rglob("*.html"):
    n = p.read_text(encoding="utf-8").count("—")
    if n:
        em_total += n
        em_files.append((p.relative_to(OUT), n))
if em_total:
    err(f"em-dash globalnie: {em_total} w {len(em_files)} plikach")
    for rel, n in em_files[:10]:
        err(f"  {rel}: {n}")
else:
    log(f"  OK   0 em-dashow we wszystkich {sum(1 for _ in OUT.rglob('*.html'))} plikach HTML")

# ============== SUMMARY ==============
print()
print("=" * 60)
if errors:
    print(f"BLEDY: {len(errors)}")
    for e in errors[:30]:
        print(f"  - {e}")
    if len(errors) > 30:
        print(f"  ... i {len(errors) - 30} innych")
    sys.exit(1)
else:
    total_html = sum(1 for _ in OUT.rglob("*.html"))
    total_assets = sum(1 for _ in (OUT / "assets").iterdir())
    print(f"OK: {total_html} plikow HTML, {total_assets} assets, 0 bledow")
    sys.exit(0)
