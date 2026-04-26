#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_validate_dokumenty_dist.py: walidator outputu Pakietu B (~150 plikow).

Sprawdza KAZDY plik HTML/DOCX/PDF w web-hub/public/kurs-tartak/dokumenty/:
  * em-dash (UTF-8 i HTML/XML escapes) = 0
  * wzmianka EFS+/ESF+/FSE+ (per jezyk)
  * KRS, NIP, REGON Fundacji EGIDA
  * polskie diakrytyki obecne w PL (sanity)
  * cyrylica obecna w UK (sanity)
  * PDF: page_count >= 1
  * DOCX: zawiera word/document.xml z trescia
  * HTML: ma <main class="doc-content"> z trescia

Uzycie: python scripts/_validate_dokumenty_dist.py [--phase B1 B2 B3] [--quiet]
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

WEB_HUB = Path(__file__).resolve().parent.parent
OUT_ROOT = WEB_HUB / "public" / "kurs-tartak" / "dokumenty"

# Markery EFS+ w roznych konwencjach. Dokument musi zawierac PRZYNAJMNIEJ JEDEN
# z kanonicznych markerow per jezyk (lista kanoniczna), ale rozszerzamy tolerancje
# o cross-language acronyms (np. "ESF+" w UK plikach jest tez poprawne).
EFS_MARKERS = {
    "pl": ("EFS+",),
    "en": ("ESF+",),
    "es": ("FSE+",),
    "uk": ("ЄСФ", "ESF+"),  # cyrylica preferowana, latin acronym akceptowany
}

PL_DIACRITICS = ["ą", "ć", "ę", "ł", "ń", "ó", "ś", "ź", "ż"]
UK_CYRILLIC_SAMPLE = ["ф", "у", "н"]  # f, u, n in cyrillic


def check_html(path: Path, lang: str) -> list[str]:
    errs = []
    b = path.read_bytes()
    if len(b) < 2000:
        errs.append(f"HTML suspiciously small ({len(b)} bytes)")
    em_utf = b.count(b"\xe2\x80\x94")
    em_ent = b.count(b"&mdash;") + b.count(b"&#8212;")
    if em_utf or em_ent:
        errs.append(f"HTML em-dash: utf8={em_utf} entities={em_ent}")
    if b"main class=\"doc-content\"" not in b:
        errs.append("HTML missing <main class=\"doc-content\">")
    text = b.decode("utf-8", errors="replace")
    m = re.search(r'<main class="doc-content">(.*?)</main>', text, re.DOTALL)
    if not m or len(m.group(1).strip()) < 1000:
        errs.append("HTML body suspiciously small or missing")
    markers = EFS_MARKERS[lang]
    if not any(marker in b.decode("utf-8", errors="replace") for marker in markers):
        errs.append(f"HTML missing EFS marker {markers}")
    if b"KRS" not in b:
        errs.append("HTML missing KRS")
    if b"7543348716" not in b:
        errs.append("HTML missing NIP 7543348716")
    if b"521360040" not in b:
        errs.append("HTML missing REGON 521360040")
    if lang == "pl":
        for ch in PL_DIACRITICS:
            if ch.encode("utf-8") not in b:
                errs.append(f"HTML PL: diacritic '{ch}' not present")
                break
    if lang == "uk":
        cyr_count = sum(b.count(ch.encode("utf-8")) for ch in UK_CYRILLIC_SAMPLE)
        if cyr_count < 10:
            errs.append(f"HTML UK: cyrillic count too low ({cyr_count})")
    return errs


def check_docx(path: Path, lang: str) -> list[str]:
    errs = []
    if path.stat().st_size < 5000:
        errs.append(f"DOCX suspiciously small ({path.stat().st_size} bytes)")
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        errs.append(f"DOCX read failed: {exc}")
        return errs
    em_utf = xml.count(b"\xe2\x80\x94")
    em_xml = xml.count(b"&#x2014;") + xml.count(b"&#8212;")
    if em_utf or em_xml:
        errs.append(f"DOCX em-dash: utf8={em_utf} xml-esc={em_xml}")
    if len(xml) < 5000:
        errs.append(f"DOCX document.xml suspiciously small ({len(xml)} bytes)")
    text = xml.decode("utf-8", errors="replace")
    markers = EFS_MARKERS[lang]
    if not any(marker in text for marker in markers):
        errs.append(f"DOCX missing EFS marker {markers}")
    if "KRS" not in text:
        errs.append("DOCX missing KRS")
    if "7543348716" not in text:
        errs.append("DOCX missing NIP")
    if "521360040" not in text:
        errs.append("DOCX missing REGON")
    return errs


def check_pdf(path: Path, lang: str) -> list[str]:
    errs = []
    sz = path.stat().st_size
    if sz < 20000:
        errs.append(f"PDF suspiciously small ({sz} bytes)")
    try:
        import pypdf
        r = pypdf.PdfReader(str(path))
        if len(r.pages) < 1:
            errs.append("PDF has 0 pages")
    except ImportError:
        pass
    except Exception as exc:
        errs.append(f"PDF read failed: {exc}")
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Walidator outputu Pakietu B.")
    parser.add_argument("--phase", nargs="+", choices=["B1", "B2", "B3"])
    parser.add_argument("--quiet", action="store_true", help="tylko podsumowanie i FAILS")
    args = parser.parse_args()

    if not OUT_ROOT.exists():
        print(f"FAIL: brak {OUT_ROOT}", file=sys.stderr)
        return 1

    fail = ok = 0
    failures: list[tuple[str, list[str]]] = []

    for phase in ("B1", "B2", "B3"):
        if args.phase and phase not in args.phase:
            continue
        phase_dir = OUT_ROOT / phase
        if not phase_dir.exists():
            continue
        for slug_dir in sorted(phase_dir.glob("*")):
            slug = slug_dir.name
            for lang in ("pl", "en", "es", "uk"):
                html_p = slug_dir / lang / "index.html"
                docx_p = slug_dir / f"{slug}-{lang}.docx"
                pdf_p = slug_dir / f"{slug}-{lang}.pdf"
                if not html_p.exists():
                    continue
                doc_id = f"{phase}/{slug}/{lang}"
                errs = []
                errs.extend(f"HTML: {e}" for e in check_html(html_p, lang))
                errs.extend(f"DOCX: {e}" for e in check_docx(docx_p, lang))
                errs.extend(f"PDF: {e}" for e in check_pdf(pdf_p, lang))
                if errs:
                    fail += 1
                    failures.append((doc_id, errs))
                    if not args.quiet:
                        print(f"FAIL {doc_id}")
                        for e in errs:
                            print(f"  - {e}")
                else:
                    ok += 1
                    if not args.quiet:
                        print(f"OK   {doc_id}")

    print()
    print("=" * 60)
    print(f"Walidacja Pakietu B: OK={ok}  FAIL={fail}  total={ok + fail}")
    if failures:
        print()
        print("Failed documents:")
        for doc_id, errs in failures:
            print(f"  {doc_id}: {len(errs)} issue(s)")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
