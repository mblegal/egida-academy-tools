# EGIDA Academy: tools

Narzędzia buildowe dla kursów Fundacji pomocy prawnej EGIDA. Pakiet zawodowych kursów dla cudzoziemców legalnie przebywających w Polsce, oparty na metodzie sequencyjnej (M1 / M2 / M3 + dokumenty kursowe + materiały dla trenera).

To repozytorium udostępnia **kompletny pipeline buildu kursu** od plików źródłowych Markdown / HTML do gotowego do deploy hubu online: lekcje (M1 / M2 / M3 × 4 języki), prezentacje Reveal.js, materiały trenerskie (quizy, ćwiczenia, scenariusze, wytyczne) oraz dokumenty kursowe formalne (umowy, zaświadczenia, RODO, regulamin).

Repozytorium jest gotowe do reużycia w kursach o innych zawodach, językach i materiach: wystarczy nowy katalog źródłowy o tej samej konwencji.

## Status

- **Część 1 – Pakiet B (`build_podprojekt_b.py`)**: gotowe. Pipeline 50 MD do 150 plików HTML+DOCX+PDF.
- **Część 2 – indeks dokumentów (`build_dokumenty_index()`)**: gotowe. Generuje 4 strony per język + root redirect, każda strona pokazuje 13 typów posegregowanych w 3 fazach (B1/B2/B3) z linkami do trzech formatów.
- **Część 3 – Pakiet A (Part 48)**: gotowe. Pipeline buildu kursu HTML, prezentacji i materiałów trenerskich (`build_kurs.py`, `post_process.py`, `build_hub_index.py`, `sanitize_dates.py`). Skrypty wyciągnięte z lokalnego stagingu `m-b.legal/web-hub/`, zrefaktoryzowane do portability (env vars + CLI args), templates wyciągnięte do `templates/` (chrome.js, chrome.css, egida.css, doc.html.template).
- **Część 4 – plugin Claude Code (Faza C)**: planowane. Plugin poprowadzi pracownika Fundacji przez cały proces tworzenia nowego kursu (research treści, redakcja, tłumaczenia, walidacja, deploy).

## Co to robi

Pełny pipeline kursu = 4 niezależne kroki, można uruchamiać razem albo osobno:

```
+------------------+       +-----------------+       +--------------------+
| build_kurs.py    |  -->  | post_process.py |  -->  | build_hub_index.py |
| (kursant +       |       | (chrome.js inj, |       | (index.html + chr  |
|  rekrutacja +    |       |  em-dash strip, |       |  ome.css/js z      |
|  trener z MD)    |       |  banner, lesson |       |  templates/)       |
|                  |       |   chrome)       |       |                    |
+------------------+       +-----------------+       +--------------------+

+------------------------+
| build_podprojekt_b.py  |   (Pakiet B: 50 dokumentow x 3 formaty osobno)
+------------------------+
```

### Pakiet A: lekcje + rekrutacja + materiały trenerskie

Bierze wcześniej zbudowany kurs HTML i prezentacje Reveal.js z `kurs_tartak/dist/` (`npm run build:all` w repo treści) plus materiały MD z `kurs_tartak/content/`, generuje:

```
public/$COURSE_HUB_SLUG/
├── index.html                                    # hub: PIN gate + 5 sekcji + KPI
├── assets/
│   ├── chrome.css, chrome.js                     # tokens + role-nav + lang-switch
│   ├── egida.css                                 # branding podstron
│   └── egida-logo-*.png                          # logo Fundacji
├── kursant/                                      # 6 plikow standalone
│   ├── kurs-M{1,2,3}.html                        # interaktywny kurs HTML
│   └── prezentacja-M{1,2,3}.html                 # Reveal.js
├── rekrutacja/                                   # 5 plikow renderowanych z MD
│   ├── program-ogolny.html                       # PL
│   └── program-szczegolowy-{pl,en,es,uk}.html
└── trener/M{1,2,3}/                              # 30 plikow (10 per modul)
    ├── quiz-uzupelniajacy-{pl,en,es,uk}.html
    ├── cwiczenia-teoretyczne-{pl,en,es,uk}.html
    ├── scenariusze-praktyczne.html               # PL only
    └── wytyczne-trenera.html                     # PL only
```

### Pakiet B: dokumenty kursowe formalne

Bierze pliki Markdown z konwencyjnej struktury katalogów:

```
$EGIDA_KURS_ROOT/$COURSE_SLUG/podprojekt-b/
├── B1/                            # rdzen prawny
│   ├── umowa-kursu/{pl,en,es,uk}.md
│   ├── zaswiadczenie-odbywania/{pl,en,es,uk}.md
│   └── ...
├── B2/                            # dokumenty kursanta
│   ├── regulamin-kursu/{pl,en,es,uk}.md
│   └── ...
└── B3/                            # polityki i back-office
    ├── polityka-reklamacji/{pl,en,es,uk}.md
    └── ...
```

Generuje 3 formaty per plik:

```
public/$COURSE_HUB_SLUG/dokumenty/
├── B1/umowa-kursu/
│   ├── pl/index.html              # web view: branding, lang switch, downloads
│   ├── en/index.html
│   ├── es/index.html
│   ├── uk/index.html
│   ├── umowa-kursu-pl.docx        # edytowalny do wypelnienia
│   ├── umowa-kursu-en.docx
│   ├── umowa-kursu-pl.pdf         # do druku, czysty layout
│   └── ...
└── ...
```

### Walidacja

Dwa walidatory:
- `scripts/_validate_kurs_dist.py` – Pakiet A (struktura katalogów, obecność plików, em-dash=0, chrome.js / banner / lesson-chrome wstrzyknięte).
- `scripts/_validate_dokumenty_dist.py` – Pakiet B (em-dash=0, EFS+ marker per język, KRS / NIP / REGON, diakrytyki PL, cyrylica UK, integralność DOCX / PDF).

## Wymagania środowiskowe

| Narzędzie | Wersja | Po co |
|---|---|---|
| **Python** | 3.10+ (testowane: 3.12) | runtime skryptów |
| **Pandoc** | 3.x | konwersja MD → HTML body i MD → DOCX (Pakiet B) |
| **wkhtmltopdf** | 0.12.6+ | konwersja HTML → PDF (Pakiet B) |
| **Node.js** | 20+ | npm run build:* w repo treści (Pakiet A źródło) |
| **Python deps** | `pyyaml`, `pypdf`, `markdown` | parsing frontmatter, walidacja PDF, render MD |

Instalacja per OS:

### Windows

```cmd
winget install --id JohnMacFarlane.Pandoc
winget install --id wkhtmltopdf.wkhtmltox
pip install --user pyyaml pypdf markdown
```

### macOS

```bash
brew install pandoc wkhtmltopdf
pip install pyyaml pypdf markdown
```

### Linux (Debian / Ubuntu)

```bash
sudo apt install pandoc wkhtmltopdf
pip install pyyaml pypdf markdown
```

> **Uwaga**: `wkhtmltopdf` to projekt w stanie maintenance only. Działa stabilnie, ale jeśli w przyszłości pojawi się migracja, alternatywą jest WeasyPrint (wymaga GTK runtime na Windows).

## Quick start

Zakładamy że masz źródła kursu pod `~/Documents/EGIDA/kurs/kurs_tartak/`. Jeśli gdzie indziej, ustaw `EGIDA_KURS_ROOT`.

```bash
git clone https://github.com/mblegal/egida-academy-tools.git
cd egida-academy-tools
pip install -r requirements.txt
```

### Pełny build kursu (Pakiet A + B)

```bash
# Pakiet A: kursant + rekrutacja + trener
python build_kurs.py
python post_process.py
python build_hub_index.py
python scripts/_validate_kurs_dist.py

# Pakiet B: dokumenty formalne
python build_podprojekt_b.py
python scripts/_validate_dokumenty_dist.py
```

Output trafia do `public/kurs-tartak/`. Otwórz `public/kurs-tartak/index.html` w przeglądarce, żeby zobaczyć podgląd hubu (PIN: koordynator kursu).

### Tylko Pakiet A (np. po regeneracji `dist/`)

```bash
python build_kurs.py && python post_process.py && python build_hub_index.py
```

Skrypty są **idempotentne**: rebuild nadpisuje output, można uruchamiać dowolną liczbę razy.

## Konfiguracja

Zmienne środowiskowe (alternatywnie CLI args):

| Env var | CLI arg | Default | Opis |
|---|---|---|---|
| `EGIDA_KURS_ROOT` | (brak) | `~/Documents/EGIDA/kurs` | Katalog zawierający subkatalogi kursów |
| `COURSE_SLUG` | `--course-slug` | `kurs_tartak` | Subdirectory w `EGIDA_KURS_ROOT` |
| `COURSE_HUB_SLUG` | `--course-hub-slug` | `COURSE_SLUG` z `_` zamienionym na `-` | Slug w URL hubu |
| (brak) | `--course-source` | `EGIDA_KURS_ROOT/COURSE_SLUG` | Pełna ścieżka (override env vars) |
| `EGIDA_OUT_DIR` | `--output` | `<repo>/public` | Katalog output (rodzic dla `<slug>/`) |
| `WKHTMLTOPDF_PATH` | (brak) | autodetekcja PATH lub Windows default | Pełna ścieżka do wkhtmltopdf |
| `PANDOC_PATH` | (brak) | `pandoc` | Pełna ścieżka do pandoc |
| `FORCE_REBUILD` | (brak) | `0` | `1` wymusza rebuild Pakietu B (mtime ignorowany) |

Buduj tylko wybrane fazy lub dokumenty Pakietu B:

```bash
python build_podprojekt_b.py --phase B1
python build_podprojekt_b.py --only umowa-kursu regulamin-kursu
```

## Struktura repo

```
egida-academy-tools/
├── README.md                              # ten plik
├── LICENSE                                # MIT
├── requirements.txt                       # pyyaml, pypdf, markdown
├── .gitignore                             # public/, *.tar.gz, __pycache__
│
├── build_kurs.py                          # Pakiet A: kursant + rekrutacja + trener
├── post_process.py                        # Pakiet A: chrome.js / banner / lesson-chrome / em-dash
├── build_hub_index.py                     # Pakiet A: index.html + chrome.css/js z templates
├── sanitize_dates.py                      # Pakiet A: usuwa konkretne daty cykli z MD source
├── build_podprojekt_b.py                  # Pakiet B: pipeline 50 MD do HTML+DOCX+PDF
│
├── templates/                             # source-of-truth (NIE assets/)
│   ├── chrome.js                          # role-nav, lang-switch, pin-gate, progress bars
│   ├── chrome.css                         # design tokens (paleta wood/craft) + layouts
│   ├── egida.css                          # branding podstron renderowanych z MD
│   └── doc.html.template                  # template DOC (Python format string)
│
├── assets/                                # logo Fundacji (kopiowane do output)
│   └── egida-logo-*.png
│
└── scripts/
    ├── _validate_kurs_dist.py             # walidator Pakietu A
    └── _validate_dokumenty_dist.py        # walidator Pakietu B
```

## Konwencja źródeł (Pakiet B)

Każdy plik MD zaczyna się od YAML frontmatter z metadata:

```yaml
---
typ: umowa
dokument: umowa o przeprowadzenie kursu praktycznego
kurs: Praca w tartaku
podprojekt: B
faza: B1
język: pl
wersja: 1.0
stan-na: 2026-04-26
podstawa-prawna:
  - Ustawa z dnia 24 kwietnia 2003 r. o działalności pożytku publicznego...
strony: Fundacja EGIDA, Przedsiębiorca, Kursant
---

(treść Markdown poniżej)
```

Polskie klucze YAML są wspierane (pandoc 3.x je rozumie). Frontmatter służy do generowania nagłówka HTML i metadanych DOCX, sam tekst frontmatter nie pojawia się w treści dokumentu.

## Konwencja stylistyczna

- **Bez em-dashów** (znak długiej pauzy, kod Unicode `U+2014`). Stosuj półpauzę (`–`, `U+2013`), przecinek, dwukropek lub nawias. Walidator wymusza `em-dash count = 0` w outputach HTML, DOCX i PDF.
- **Polskie diakrytyki obowiązkowe**: ą, ć, ę, ł, ń, ó, ś, ź, ż (i wielkie odpowiedniki). Walidator weryfikuje obecność.
- **Liczby dziesiętne**: w PL/ES/UK przecinek (0,25%), w EN kropka (0.25%).
- **Język ukraiński**: cyrylica. Walidator sprawdza obecność.

## Edycja templates

`templates/chrome.js`, `templates/chrome.css`, `templates/egida.css`, `templates/doc.html.template` to **source-of-truth**. Pliki `public/$slug/assets/*` są **regenerowane** przy każdym uruchomieniu skryptów buildowych – bezpośrednie edycje w `public/` są tracone.

Lekcja Part 47: gdy chcesz zmienić zachowanie chrome.js (np. dodać klucz i18n), edytuj `templates/chrome.js`, potem `python build_hub_index.py`.

## Dodawanie dokumentu do istniejącego kursu (Pakiet B)

1. Utwórz katalog `$EGIDA_KURS_ROOT/$COURSE_SLUG/podprojekt-b/{B1|B2|B3}/{nowy-slug}/`.
2. Dodaj pliki `pl.md`, `en.md`, `es.md`, `uk.md` z frontmatter i treścią.
3. Dopisz wpis w `build_podprojekt_b.py`:
   - `DOC_LABELS[nowy-slug] = {"pl": "...", "en": "...", "es": "...", "uk": "..."}`
   - `DOCS.append(("B1", "nowy-slug", ["pl", "en", "es", "uk"]))`
4. `python build_podprojekt_b.py --only nowy-slug`
5. `python scripts/_validate_dokumenty_dist.py`

## Dodawanie nowego kursu (inny zawód / temat)

1. Utwórz katalog `$EGIDA_KURS_ROOT/{nowy_kurs_slug}/` z tą samą strukturą co `kurs_tartak`:
   - `content/M{1,2,3}/lessons/` (treść lekcji × 4 jęz)
   - `content/M{1,2,3}/artifacts/` (materiały trenerskie)
   - `content/materialy-pomocnicze/` (programy, prospekty)
   - `podprojekt-b/B{1,2,3}/` (dokumenty formalne)
   - `dist/` (artefakty `npm run build:all`)
2. Dostosuj treść do nowego zawodu.
3. `python build_kurs.py --course-slug nowy_kurs_slug`
4. `python post_process.py --course-hub-slug nowy-kurs-slug`
5. `python build_hub_index.py --course-hub-slug nowy-kurs-slug`
6. `python build_podprojekt_b.py --course-slug nowy_kurs_slug`

> **Faza C (przyszłość)**: skill / plugin Claude Code automatyzuje kroki 1-2 (research treści zawodu, redakcja, tłumaczenia trzech języków na podstawie polskiego oryginału, walidacja).

## Deploy

To repozytorium **nie zawiera** infrastruktury deploy (Dockerfile, nginx.conf, sekrety). Lokalnie generuje statyczne pliki w `public/`. Deploy do produkcji jest zewnętrznym procesem zależnym od infrastruktury organizacji:

- **Fundacja EGIDA / m-b.legal**: tar+ssh do `prezentacje.m-b.legal/kurs-tartak/` (kontener Docker `web-hub` na VPS).
- **Inne organizacje**: dowolny static hosting (GitHub Pages, Netlify, Cloudflare Pages, S3+CloudFront, własny nginx).

## Licencja

[MIT License](LICENSE): można używać, modyfikować i dystrybuować. Atrybucja do Fundacji pomocy prawnej EGIDA mile widziana.

## Powiązane projekty

- **Treść kursu Praca w tartaku** (Pakiet A: 96 lekcji × 4 języki, prezentacje, materiały trenera): [`mblegal/egida-kurs-tartak`](https://github.com/mblegal/egida-kurs-tartak) (PUBLIC).
- **Hub online**: `prezentacje.m-b.legal/kurs-tartak/` (chronione PIN, deploy z tego repo).

## Autorzy

Fundacja pomocy prawnej EGIDA, Opole. Współpraca: kancelaria Michał Bartosiński (m-b.legal).
