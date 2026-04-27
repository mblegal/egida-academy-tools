#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_hub_index.py: pipeline budowania hub-index dla kursu (Sprint 1 audit UI/UX).

Generuje:
  public/<course-hub-slug>/index.html              (PIN gate + 5 sekcji + role-nav + KPI)
  public/<course-hub-slug>/assets/chrome.css       (z templates/chrome.css)
  public/<course-hub-slug>/assets/chrome.js        (z templates/chrome.js)

UWAGA: chrome.js i chrome.css to **artefakty generowane** z templates/, NIE source.
Edytuj templates/chrome.js i templates/chrome.css, potem rerun build_hub_index.py
(lekcja Part 47: bezposrednie edycje assets/chrome.js sa nadpisywane).

Run flow:
  1) python build_kurs.py
  2) python post_process.py
  3) python build_hub_index.py     # ten skrypt nadpisuje index.html

Konfiguracja (env vars + CLI):
  COURSE_HUB_SLUG  default: kurs-tartak
  EGIDA_OUT_DIR    default: <repo>/public

Uzycie:
  python build_hub_index.py
"""
from __future__ import annotations

import argparse
import os
import time
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
TEMPLATES = REPO / "templates"

if not TEMPLATES.exists():
    raise SystemExit(f"BLAD: brak {TEMPLATES}")
for tpl in ("chrome.css", "chrome.js"):
    if not (TEMPLATES / tpl).exists():
        raise SystemExit(f"BLAD: brak templates/{tpl}")
(OUT / "assets").mkdir(parents=True, exist_ok=True)

# ============== ASSETS: chrome.css + chrome.js z templates/ ==============
# Trailing newline gwarantujemy zeby zachowac zgodnosc z poprzednim pipeline'em
# (sprint1 pisal CHROME_JS z newline po zamykajacym """).
chrome_css = (TEMPLATES / "chrome.css").read_text(encoding="utf-8")
chrome_js = (TEMPLATES / "chrome.js").read_text(encoding="utf-8")
if not chrome_css.endswith("\n"):
    chrome_css += "\n"
if not chrome_js.endswith("\n"):
    chrome_js += "\n"
(OUT / "assets" / "chrome.css").write_text(chrome_css, encoding="utf-8")
(OUT / "assets" / "chrome.js").write_text(chrome_js, encoding="utf-8")
print(f"OK: assets/chrome.css ({len(chrome_css):,} B) + assets/chrome.js ({len(chrome_js):,} B)")


# ============== KOMPONENTY HTML ==============
def module_card(num, role_name, title, bullets, time, size, href, key):
    """key = 'M1' | 'M2' | 'M3', bazowy klucz i18n karty kursanta."""
    bl = "".join("<li>{0}</li>".format(b) for b in bullets)
    return """      <a class="module-card" href="{href}" data-format="course">
        <div class="module-card__eye" data-i18n="card.kursant.{key}.eye">Moduł {num} · {role_name}</div>
        <h3 class="module-card__title" data-i18n="card.kursant.{key}.title">{title}</h3>
        <ul class="module-card__bullets" data-i18n="card.kursant.{key}.bullets_html">{bl}</ul>
        <div class="module-card__meta"><span data-i18n="card.kursant.{key}.time">{time}</span><span data-i18n="card.kursant.{key}.size">{size}</span></div>
        <div class="module-card__progress" data-progress-module="{key}" aria-live="polite"></div>
      </a>""".format(num=num, role_name=role_name, title=title, bl=bl, time=time, size=size, href=href, key=key)


def deck_card(num, title, time, size, href, key):
    """key = 'D1' | 'D2' | 'D3', bazowy klucz i18n karty decka Reveal.js."""
    return """      <a class="module-card" href="{href}" data-format="deck">
        <div class="module-card__eye" data-i18n="card.kursant.{key}.eye">Prezentacja M{num} · Reveal.js</div>
        <h3 class="module-card__title" data-i18n="card.kursant.{key}.title">{title}</h3>
        <div class="module-card__meta"><span data-i18n="card.kursant.{key}.time">{time}</span><span data-i18n="card.kursant.{key}.size">{size}</span></div>
      </a>""".format(num=num, title=title, time=time, size=size, href=href, key=key)


# Dane modulow (3 bullets per modul)
MODULES = [
    dict(num="01", role="Pomocnik", title="BHP, drewno, rytm dnia",
         bullets=["BHP i ŚOI w tartaku", "gatunki drewna, narzędzia ręczne", "stanowisko, rytm zmiany, komunikacja"],
         time="4 tyg. · ~32 h", size="3,3 MB", href="kursant/kurs-M1.html", key="M1"),
    dict(num="02", role="Młodszy operator", title="Pilarka taśmowa, trak pionowy",
         bullets=["obsługa pilarki taśmowej i traka", "dokumenty techniczne, karta stanowiska", "usterki, raportowanie"],
         time="4 tyg. · ~32 h", size="3,5 MB", href="kursant/kurs-M2.html", key="M2"),
    dict(num="03", role="Samodzielny", title="Koordynacja zmiany, audyty",
         bullets=["prowadzenie zmiany 8h, nadzór nad 2-4 M2", "reklamacje klienta, KC art. 556-563", "audyty FSC, ISO 9001"],
         time="4 tyg. · ~32 h", size="6,5 MB", href="kursant/kurs-M3.html", key="M3"),
]

DECKS = [
    dict(num="1", title="Slajdy M1 (Reveal.js)", time="163 sekcji", size="2,8 MB", href="kursant/prezentacja-M1.html", key="D1"),
    dict(num="2", title="Slajdy M2 (Reveal.js)", time="163 sekcji", size="2,7 MB", href="kursant/prezentacja-M2.html", key="D2"),
    dict(num="3", title="Slajdy M3 (Reveal.js)", time="147 sekcji", size="4,4 MB", href="kursant/prezentacja-M3.html", key="D3"),
]

modules_html = "\n".join(module_card(m["num"], m["role"], m["title"], m["bullets"], m["time"], m["size"], m["href"], m["key"]) for m in MODULES)
decks_html = "\n".join(deck_card(d["num"], d["title"], d["time"], d["size"], d["href"], d["key"]) for d in DECKS)

# Trener: 3 wiersze (M1/M2/M3) x 4 kolumny (Quiz A1, Cwiczenia A2, Scenariusze A3, Wytyczne A4)
TRENER_MODULES = [
    dict(code="M1", name="Pomocnik", desc="BHP, drewno, rytm dnia"),
    dict(code="M2", name="Młodszy operator", desc="Pilarka, trak, usterki"),
    dict(code="M3", name="Samodzielny", desc="Koordynacja, reklamacje, FSC"),
]
TRENER_COLS = [
    dict(code="A1", name="Quiz uzupełniający", path="quiz-uzupelniajacy", langs=["pl", "en", "es", "uk"]),
    dict(code="A2", name="Ćwiczenia teoretyczne", path="cwiczenia-teoretyczne", langs=["pl", "en", "es", "uk"]),
    dict(code="A3", name="Scenariusze praktyczne", path="scenariusze-praktyczne", langs=["pl"]),
    dict(code="A4", name="Wytyczne dla trenera", path="wytyczne-trenera", langs=["pl"]),
]


def trener_cell(module_code, col):
    base_href = "trener/{0}/{1}".format(module_code, col["path"])
    name_i18n = 'data-i18n="card.trener.col.{0}.name"'.format(col["code"])
    if col["langs"] == ["pl"]:
        href = "{0}.html".format(base_href)
        return """      <div class="trener-cell"><a href="{href}" {ni}>{name}</a><div class="langs"><a href="{href}" class="pl-only" hreflang="pl">PL</a></div></div>""".format(href=href, name=col["name"], ni=name_i18n)
    data_attrs = " ".join('data-href-{0}="{1}-{0}.html"'.format(L, base_href) for L in col["langs"])
    return """      <div class="trener-cell"><a href="{0}-pl.html" {1} data-label-base="{2}" {ni}>{2}</a><div class="langs">{3}</div></div>""".format(
        base_href,
        data_attrs,
        col["name"],
        "".join('<a href="{0}-{1}.html" hreflang="{1}">{2}</a>'.format(base_href, L, L.upper()) for L in col["langs"]),
        ni=name_i18n
    )


trener_table_html = "    <div class=\"trener-table\">\n"
trener_table_html += "      <div class=\"trener-table__corner\" data-i18n=\"tbl.corner\">Moduł × typ</div>\n"
for col in TRENER_COLS:
    trener_table_html += '      <div class="trener-table__col-hd"><span class="col-name" data-i18n="card.trener.col.{1}.name">{0}</span><span class="col-code">{1}</span></div>\n'.format(col["name"], col["code"])
for mod in TRENER_MODULES:
    trener_table_html += '      <div class="trener-table__row-hd"><span class="row-name">{0}</span><span class="row-desc" data-i18n="card.trener.row.{0}.desc">{1}</span></div>\n'.format(mod["code"], mod["desc"])
    for col in TRENER_COLS:
        trener_table_html += trener_cell(mod["code"], col) + "\n"
trener_table_html += "    </div>\n"

# Rekrutacja
REC_CARDS = [
    dict(eye="D1 · program ogólny", title="Program ogólny kursu",
         desc="Jednostronicowy dokument z tabelami modułów, artefaktów i harmonogramu cyklu 2026/2027.",
         meta="1 468 słów · tabele · tylko PL",
         href="rekrutacja/program-ogolny.html", langs=None, i18n_key="D1"),
    dict(eye="D2 · program szczegółowy", title="Program szczegółowy 96 lekcji",
         desc="Każda lekcja: tytuł, czas, cel dydaktyczny, 5-8 kluczowych terminów polskich.",
         meta="~6-7 tys. słów",
         href="rekrutacja/program-szczegolowy-pl.html",
         langs=["pl", "en", "es", "uk"],
         path="rekrutacja/program-szczegolowy", i18n_key="D2"),
]

rec_cards_html = ""
for card in REC_CARDS:
    k = card["i18n_key"]
    if card["langs"]:
        data_attrs = " ".join('data-href-{0}="{1}-{0}.html"'.format(L, card["path"]) for L in card["langs"])
        rec_cards_html += """      <a class="rec-card" href="{href}" {data_attrs} data-label-base="{title}">
        <div class="rec-card__eye" data-i18n="card.rekrutacja.{k}.eye">{eye}</div>
        <h3 class="rec-card__title" data-i18n="card.rekrutacja.{k}.title">{title}</h3>
        <p class="rec-card__desc" data-i18n="card.rekrutacja.{k}.desc">{desc}</p>
        <div class="rec-card__meta" data-i18n="card.rekrutacja.{k}.meta">{meta}</div>
      </a>
""".format(href=card["href"], data_attrs=data_attrs, title=card["title"], eye=card["eye"], desc=card["desc"], meta=card["meta"], k=k)
    else:
        rec_cards_html += """      <a class="rec-card" href="{href}" data-lang-only="pl">
        <div class="rec-card__eye" data-i18n="card.rekrutacja.{k}.eye">{eye}</div>
        <h3 class="rec-card__title" data-i18n="card.rekrutacja.{k}.title">{title}</h3>
        <p class="rec-card__desc" data-i18n="card.rekrutacja.{k}.desc">{desc}</p>
        <div class="rec-card__meta" data-i18n="card.rekrutacja.{k}.meta">{meta}</div>
      </a>
""".format(href=card["href"], title=card["title"], eye=card["eye"], desc=card["desc"], meta=card["meta"], k=k)


# =================================================================
# INDEX TEMPLATE (inline, 220 linii)
# UWAGA: zawiera Python .format() placeholders {modules_html}, {decks_html},
# {trener_table_html}, {rec_cards_html} + __CACHE_BUST__ replace.
# Wszystkie inne klamry { } w CSS/JS sa zaeskejpowane przez {{ }}.
# Inline zostaje (zamiast templates/) bo .format() escape utrudnia czytelnosc
# a zmiany struktury zwykle ida razem ze zmianami danych powyzej.
# =================================================================
INDEX = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f6f4ef">
<title>Kurs tartakowy · Fundacja EGIDA</title>
<link rel="stylesheet" href="assets/chrome.css?v=__CACHE_BUST__">
<link rel="icon" type="image/png" href="assets/egida-logo-64.png">
</head>
<body class="hub-locked">

<a class="skip-link" href="#kursant" data-i18n="hdr.skip_link">Przejdź do treści</a>

<!-- PIN GATE -->
<div class="pin-screen" id="pin-screen" role="dialog" aria-modal="true" aria-labelledby="pin-title">
  <div class="pin-card">
    <div class="pin-card__logo"><img src="assets/egida-logo-wide-256.png" alt="Logo Fundacji EGIDA"></div>
    <div class="pin-card__eyebrow" data-i18n="pin.eyebrow">Dostęp PIN</div>
    <h1 class="pin-card__title" id="pin-title" data-i18n="pin.title_html">Kurs tartakowy<br><em>Fundacja EGIDA</em></h1>
    <p class="pin-card__lead" data-i18n="pin.lead">Materiały kursu są chronione kodem PIN. Wprowadź 4-cyfrowy kod otrzymany od koordynatora kursu.</p>
    <div class="pin-fields" role="group" aria-label="Pole 4-cyfrowego kodu PIN" data-i18n-attr="aria-label:pin.fields_label">
      <input type="tel" inputmode="numeric" pattern="\\d*" maxlength="1" aria-label="Pierwsza cyfra PIN">
      <input type="tel" inputmode="numeric" pattern="\\d*" maxlength="1" aria-label="Druga cyfra PIN">
      <input type="tel" inputmode="numeric" pattern="\\d*" maxlength="1" aria-label="Trzecia cyfra PIN">
      <input type="tel" inputmode="numeric" pattern="\\d*" maxlength="1" aria-label="Czwarta cyfra PIN">
    </div>
    <div class="pin-msg" role="status" aria-live="polite"></div>
    <div class="pin-footnote" data-i18n="pin.footnote_html">Materiały kursu „Praca w tartaku" · Fundacja EGIDA.<br>Kod jest zapamiętywany w przeglądarce do końca sesji.</div>
  </div>
</div>

<div class="hub-wrap">

<!-- SITE HEADER -->
<header class="site-header">
  <div class="site-header__row">
    <a class="site-header__brand" href="index.html">
      <span class="site-header__logo"><img src="assets/egida-logo-wide-128.png" alt="Logo Fundacji EGIDA"></span>
      <span class="site-header__title">
        <span class="site-header__eyebrow" data-i18n="hdr.eyebrow">Fundacja EGIDA</span>
        <span class="site-header__name" data-i18n="hdr.name_html">Praca <em>w tartaku</em></span>
      </span>
    </a>
    <div class="site-header__spacer"></div>
    <span class="pin-state" data-i18n="hdr.pin_state">Dostęp aktywny</span>
    <nav class="lang-switch" aria-label="Język treści" data-i18n-attr="aria-label:lang.label">
      <button type="button" data-lang="pl" aria-pressed="false">PL</button>
      <button type="button" data-lang="en" aria-pressed="false">EN</button>
      <button type="button" data-lang="es" aria-pressed="false">ES</button>
      <button type="button" data-lang="uk" aria-pressed="false">UK</button>
    </nav>
  </div>
  <nav class="role-nav" aria-label="Wybierz swoją rolę" data-i18n-attr="aria-label:role.nav_label">
    <a href="#kursant"><span class="role-num">01</span><span class="role-label" data-i18n="role.1">Kursant</span></a>
    <a href="#trener"><span class="role-num">02</span><span class="role-label" data-i18n="role.2">Trener</span></a>
    <a href="#rekrutacja"><span class="role-num">03</span><span class="role-label" data-i18n="role.3">Rekrutacja</span></a>
    <a href="#projekt"><span class="role-num">04</span><span class="role-label" data-i18n="role.4">O projekcie</span></a>
    <a href="#dokumenty"><span class="role-num">05</span><span class="role-label" data-i18n="role.5">Dokumenty</span></a>
  </nav>
</header>

<!-- HERO -->
<section class="hero">
  <div class="hero__eyebrow" data-i18n="hero.eyebrow">Kurs zawodowy · 12 tygodni · 4 języki · bezpłatnie</div>
  <h1 class="hero__title" data-i18n="hero.title_html">Zawód operatora tartaku <em>w 12 tygodni</em></h1>
  <p class="hero__lead" data-i18n="hero.lead">Trzy moduły: pomocnik → młodszy operator → operator samodzielny z elementami nadzoru. Materiały w polskim, angielskim, hiszpańskim i ukraińskim: dla kursanta, trenera, rekrutera i koordynatora.</p>
</section>

<!-- KPI -->
<div class="kpi-row" role="list">
  <a class="kpi" href="#kursant" role="listitem">
    <div class="kpi__n">96</div>
    <div class="kpi__l" data-i18n="kpi.1.l">lekcji × 4 języki</div>
    <div class="kpi__ctx" data-i18n="kpi.1.ctx">Trzy moduły po 32 lekcje (2h każda). PL/EN/ES/UK.</div>
  </a>
  <a class="kpi" href="#trener" role="listitem">
    <div class="kpi__n">30</div>
    <div class="kpi__l" data-i18n="kpi.2.l">artefaktów trenera</div>
    <div class="kpi__ctx" data-i18n="kpi.2.ctx">Quizy, ćwiczenia, scenariusze, wytyczne × M1/M2/M3.</div>
  </a>
  <a class="kpi" href="#rekrutacja" role="listitem">
    <div class="kpi__n">5</div>
    <div class="kpi__l" data-i18n="kpi.3.l">materiałów rekrutacji</div>
    <div class="kpi__ctx" data-i18n="kpi.3.ctx">Program ogólny i szczegółowy × 4 języki.</div>
  </a>
  <a class="kpi" href="#projekt" role="listitem">
    <div class="kpi__n">~1,56 mln</div>
    <div class="kpi__l" data-i18n="kpi.4.l">słów produkcyjnych</div>
    <div class="kpi__ctx" data-i18n="kpi.4.ctx">Efekt potencjału budowanego w projekcie SMART + EGIDA.</div>
  </a>
</div>

<main class="hub">

  <!-- 1. KURSANT -->
  <section class="section" id="kursant" aria-labelledby="sec-kursant-h">
    <div class="section__hd">
      <div>
        <div class="section__n" data-i18n="sec.1.n">01 · Dla kursanta</div>
        <h2 class="section__h" id="sec-kursant-h" data-i18n="sec.1.h">Trzy moduły po cztery tygodnie</h2>
      </div>
      <p class="section__desc" data-i18n="sec.1.d">Dwa formaty: interaktywny kurs HTML do samodzielnej nauki oraz prezentacja Reveal.js do projekcji w sali dydaktycznej.</p>
    </div>

    <div class="mode-label" data-i18n="sec.1.mode1">Do samodzielnej nauki · 3 moduły · 12 tygodni</div>
    <div class="card-grid-3">
{modules_html}
    </div>

    <div class="mode-label" data-i18n="sec.1.mode2">Do projekcji w sali</div>
    <div class="card-grid-3">
{decks_html}
    </div>
  </section>

  <!-- 2. TRENER -->
  <section class="section" id="trener" aria-labelledby="sec-trener-h">
    <div class="section__hd">
      <div>
        <div class="section__n" data-i18n="sec.2.n">02 · Dla trenera</div>
        <h2 class="section__h" id="sec-trener-h" data-i18n="sec.2.h">Artefakty dydaktyczne Fazy 4</h2>
      </div>
      <p class="section__desc" data-i18n="sec.2.d">Tabela 3 × 4: wiersze = moduły (M1/M2/M3), kolumny = typ artefaktu. Scenariusze praktyczne (A3) i wytyczne dla trenera (A4) tylko w PL; quizy (A1) i ćwiczenia (A2) w czterech językach.</p>
    </div>
{trener_table_html}
  </section>

  <!-- 3. REKRUTACJA -->
  <section class="section" id="rekrutacja" aria-labelledby="sec-rekrutacja-h">
    <div class="section__hd">
      <div>
        <div class="section__n" data-i18n="sec.3.n">03 · Dla rekrutacji</div>
        <h2 class="section__h" id="sec-rekrutacja-h" data-i18n="sec.3.h">Dokumenty dla kandydatów i partnerów</h2>
      </div>
      <p class="section__desc" data-i18n="sec.3.d">Program ogólny i szczegółowy (96 lekcji) z opisami modułów i celami dydaktycznymi. Kliknij kartę: wersja językowa podąża za globalnym przełącznikiem w headerze.</p>
    </div>
    <div class="rec-grid">
{rec_cards_html}
    </div>
  </section>

  <!-- 4. O PROJEKCIE -->
  <section class="section" id="projekt" aria-labelledby="sec-proj-h">
    <div class="section__hd">
      <div>
        <div class="section__n" data-i18n="sec.4.n">04 · O projekcie</div>
        <h2 class="section__h" id="sec-proj-h" data-i18n="sec.4.h">Fundamenty lokalnej polityki migracyjnej</h2>
      </div>
      <p class="section__desc" data-i18n="sec.4.d">Kurs powstał dzięki potencjałowi budowanemu przez Fundacje SMART i EGIDA w projekcie „Budowa fundamentów pod lokalną politykę migracyjną i integracyjną" (FEO 2021-2027, Działanie 06.03). Z tego potencjału wyrastają kolejne kursy, wszystkie bezpłatne dla cudzoziemców.</p>
    </div>
    <a class="koord-card" href="projekt/index.html" data-href-pl="projekt/index.html" data-href-en="projekt/index-en.html" data-href-es="projekt/index-es.html" data-href-uk="projekt/index-uk.html">
      <div>
        <div class="koord-card__eye" data-i18n="card.projekt.eye">projekt · SMART + EGIDA · Opole</div>
        <h3 class="koord-card__title" data-i18n="card.projekt.title">Budowa fundamentów pod lokalną politykę migracyjną i integracyjną</h3>
        <p class="koord-card__desc" data-i18n="card.projekt.desc">Partnerstwo Fundacji SMART (lider) i EGIDA. Cel: rozbudowa potencjału obu organizacji do uruchomienia w Opolu ośrodka integracji cudzoziemców w modelu one-stop-shop. Budżet 500 000 zł, dofinansowanie 475 000 zł z EFS+ i budżetu państwa. Wniosek FEOP.06.03-IZ.00-0006/25.</p>
      </div>
      <div class="koord-card__arrow" aria-hidden="true">→</div>
    </a>
  </section>

  <!-- 5. DOKUMENTY KURSU -->
  <section class="section" id="dokumenty" aria-labelledby="sec-dok-h">
    <div class="section__hd">
      <div>
        <div class="section__n" data-i18n="sec.5.n">05 · Dokumenty kursu</div>
        <h2 class="section__h" id="sec-dok-h" data-i18n="sec.5.h">Pakiet dokumentów formalnych</h2>
      </div>
      <p class="section__desc" data-i18n="sec.5.d">Wszystkie dokumenty kursowe (umowa, zaświadczenia, regulamin, RODO, formularz rekrutacyjny, polityka reklamacji, umowa współorganizacji) w czterech językach (PL/EN/ES/UK) i trzech formatach (HTML do podglądu online, DOCX do edycji, PDF do druku).</p>
    </div>
    <a class="koord-card" href="dokumenty/index.html">
      <div>
        <div class="koord-card__eye" data-i18n="card.dokumenty.eye">Pakiet B · 13 typów × 4 języki × 3 formaty</div>
        <h3 class="koord-card__title" data-i18n="card.dokumenty.title">Otwórz listę dokumentów kursu</h3>
        <p class="koord-card__desc" data-i18n="card.dokumenty.desc">Umowa kursu, zaświadczenia o odbywaniu i ukończeniu Modułów oraz całego Kursu, zaświadczenia praktyki absolwenckiej, regulamin Kursu, klauzula informacyjna RODO i zgody, formularz rekrutacyjny, polityka reklamacji i odwołań, umowa współorganizacji.</p>
      </div>
      <div class="koord-card__arrow" aria-hidden="true">→</div>
    </a>
  </section>

</main>

<!-- FOOTER -->
<footer class="site-footer">
  <div class="site-footer__row">
    <p class="site-footer__disclaimer" data-i18n="footer.disclaimer_html">
      <b>Fundacja na rzecz edukacji SMART</b> (lider) w partnerstwie z <b>Fundacją pomocy prawnej EGIDA</b> realizuje projekt „Budowa fundamentów pod lokalną politykę migracyjną i integracyjną" (wniosek FEOP.06.03-IZ.00-0006/25, <b>FEO 2021-2027, Działanie 06.03: Budowanie potencjału partnerów społecznych oraz organizacji społeczeństwa obywatelskiego</b>, dofinansowanie 475 000 zł ze środków EFS+ i budżetu państwa). Celem projektu jest rozbudowa potencjału obu organizacji do uruchomienia w Opolu lokalnego ośrodka integracji cudzoziemców w modelu one-stop-shop. Kurs „Praca w tartaku" powstał jako owoc kompetencji i zasobów zbudowanych w ramach tego projektu.
    </p>
    <div class="site-footer__logos" aria-label="Partnerzy i finansowanie projektu" data-i18n-attr="aria-label:footer.logos_label">
      <span class="logo-ph logo-ph--efs" aria-label="Europejski Fundusz Społeczny Plus">
        <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <circle cx="12" cy="12" r="11" fill="#003399"/>
          <g fill="#FFCC00">
            <circle cx="12" cy="4.5" r="1"/><circle cx="17.3" cy="6.7" r="1"/><circle cx="19.5" cy="12" r="1"/>
            <circle cx="17.3" cy="17.3" r="1"/><circle cx="12" cy="19.5" r="1"/><circle cx="6.7" cy="17.3" r="1"/>
            <circle cx="4.5" cy="12" r="1"/><circle cx="6.7" cy="6.7" r="1"/>
          </g>
        </svg>
        <span>EFS+</span>
      </span>
      <span class="logo-ph logo-ph--mfipr" aria-label="Ministerstwo Funduszy i Polityki Regionalnej">
        <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <rect x="2" y="5" width="20" height="7" fill="#FFFFFF" stroke="#d9d4c5"/>
          <rect x="2" y="12" width="20" height="7" fill="#DC143C"/>
        </svg>
        <span>MFiPR</span>
      </span>
      <span class="logo-ph logo-ph--egida"><img src="assets/egida-logo-64.png" alt=""><span>Fundacja EGIDA</span></span>
    </div>
  </div>
</footer>

</div><!-- /.hub-wrap -->

<script src="assets/chrome.js?v=__CACHE_BUST__"></script>
</body>
</html>
""".format(modules_html=modules_html, decks_html=decks_html, trener_table_html=trener_table_html, rec_cards_html=rec_cards_html)

_cache_bust = str(int(time.time()))
INDEX = INDEX.replace("__CACHE_BUST__", _cache_bust)
(OUT / "index.html").write_text(INDEX, encoding="utf-8")
print("OK: index.html zapisany")

# weryfikacja
html_size = (OUT / "index.html").stat().st_size
css_size = (OUT / "assets" / "chrome.css").stat().st_size
js_size = (OUT / "assets" / "chrome.js").stat().st_size
em_count = (OUT / "index.html").read_text(encoding="utf-8").count("—")
en_count = (OUT / "index.html").read_text(encoding="utf-8").count("–")
print()
print("=== build_hub_index weryfikacja ===")
print(f"index.html: {html_size:,} B, em={em_count}, en={en_count}")
print(f"chrome.css: {css_size:,} B")
print(f"chrome.js:  {js_size:,} B")
