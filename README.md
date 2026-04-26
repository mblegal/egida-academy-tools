# EGIDA Academy: tools

Narzędzia buildowe dla kursów Fundacji pomocy prawnej EGIDA. Pakiet zawodowych kursów dla cudzoziemców legalnie przebywających w Polsce, oparty na metodzie sequencyjnej (M1 / M2 / M3 + dokumenty kursowe + materiały dla trenera).

To repozytorium udostępnia **pipeline budowy Pakietu B** (dokumenty kursowe formalne) z plików źródłowych Markdown do produkcyjnych formatów: **HTML** (preview online), **DOCX** (do wypełnienia / edycji) i **PDF** (do druku). 50 plików MD, 4 języki (PL / EN / ES / UK), 13 typów dokumentów = **150 plików wyjściowych** na kurs.

Repozytorium jest gotowe do reużycia w kursach o innych zawodach, językach i materiach: wystarczy nowy katalog źródłowy o tej samej konwencji.

## Status

- **Część 1 (`build_podprojekt_b.py`)**: gotowe, używane produkcyjnie dla kursu „Praca w tartaku".
- **Część 2 (deploy hubowy + indeks dokumentów)**: planowane.
- **Część 3 (skill / plugin Claude Code dla pracowników Fundacji)**: planowane. Plugin poprowadzi pracownika przez cały proces tworzenia nowego kursu (research treści, redakcja, tłumaczenia, walidacja, deploy).

## Co to robi

Bierze pliki Markdown z konwencyjnej struktury katalogów:

```
$EGIDA_KURS_ROOT/$COURSE_SLUG/podprojekt-b/
├── B1/                            # rdzeń prawny
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
│   ├── pl/index.html              # web view: branding kursu, lang switch, downloads
│   ├── en/index.html
│   ├── es/index.html
│   ├── uk/index.html
│   ├── umowa-kursu-pl.docx        # edytowalny dla wypełnienia
│   ├── umowa-kursu-en.docx
│   ├── umowa-kursu-pl.pdf         # do druku, czysty layout
│   └── ...
└── ...
```

Walidator `scripts/_validate_dokumenty_dist.py` sprawdza każdy z 150 plików: zero em-dashów (preferencja stylistyczna projektu), obecność wzmianki o programie EFS+, dane rejestrowe Fundacji (KRS / NIP / REGON), polskie diakrytyki w PL, cyrylica w UK, page count ≥ 1 w PDF, integralność DOCX zip.

## Wymagania środowiskowe

| Narzędzie | Wersja | Po co |
|---|---|---|
| **Python** | 3.10+ (testowane: 3.12) | runtime skryptów |
| **Pandoc** | 3.x | konwersja MD → HTML body i MD → DOCX |
| **wkhtmltopdf** | 0.12.6+ | konwersja HTML → PDF |
| **Python deps** | `pyyaml`, `pypdf`, `markdown` | parsing frontmatter, walidacja PDF |

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

Zakładamy że masz źródła kursu pod `~/Documents/EGIDA/kurs/kurs_tartak/podprojekt-b/`. Jeśli gdzie indziej, ustaw `EGIDA_KURS_ROOT`.

```bash
git clone https://github.com/mblegal/egida-academy-tools.git
cd egida-academy-tools
pip install -r requirements.txt

# Build wszystkich 50 dokumentów × 3 formaty = 150 plików:
python build_podprojekt_b.py

# Walidacja:
python scripts/_validate_dokumenty_dist.py
```

Output trafia do `public/kurs-tartak/dokumenty/`. Otwórz `public/kurs-tartak/dokumenty/B1/umowa-kursu/pl/index.html` w przeglądarce, żeby zobaczyć podgląd.

## Konfiguracja

Zmienne środowiskowe (alternatywnie CLI args):

| Env var | CLI arg | Default | Opis |
|---|---|---|---|
| `EGIDA_KURS_ROOT` | (brak) | `~/Documents/EGIDA/kurs` | Katalog zawierający subkatalogi kursów |
| `COURSE_SLUG` | `--course-slug` | `kurs_tartak` | Subdirectory w `EGIDA_KURS_ROOT` |
| `COURSE_HUB_SLUG` | (brak) | `COURSE_SLUG` z `_` zamienionym na `-` | Slug w URL hubu |
| (brak) | `--course-source` | `EGIDA_KURS_ROOT/COURSE_SLUG` | Pełna ścieżka do katalogu kursu (override env vars) |
| `WKHTMLTOPDF_PATH` | (brak) | autodetekcja PATH lub Windows default | Pełna ścieżka do wkhtmltopdf |
| `PANDOC_PATH` | (brak) | `pandoc` | Pełna ścieżka do pandoc |
| `FORCE_REBUILD` | (brak) | `0` | `1` wymusza rebuild nawet gdy mtime output > input |

Buduj tylko wybrane fazy lub dokumenty:

```bash
python build_podprojekt_b.py --phase B1
python build_podprojekt_b.py --only umowa-kursu regulamin-kursu
```

## Konwencja źródeł

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

- **Bez em-dashów** (znak długiej pauzy, kod Unicode `U+2014`). Stosuj półpauzę (`–`, `U+2013`), przecinek, dwukropek lub nawias. Walidator wymusza `em-dash count = 0` w outputach HTML i DOCX.
- **Polskie diakrytyki obowiązkowe**: ą, ć, ę, ł, ń, ó, ś, ź, ż (i wielkie odpowiedniki). Walidator weryfikuje obecność.
- **Liczby dziesiętne**: w PL/ES/UK przecinek (0,25%), w EN kropka (0.25%).
- **Język ukraiński**: cyrylica. Walidator sprawdza obecność.

## Dodawanie dokumentu do istniejącego kursu

1. Utwórz katalog `$EGIDA_KURS_ROOT/$COURSE_SLUG/podprojekt-b/{B1|B2|B3}/{nowy-slug}/`.
2. Dodaj pliki `pl.md`, `en.md`, `es.md`, `uk.md` z frontmatter i treścią.
3. Dopisz wpis w `build_podprojekt_b.py`:
   - `DOC_LABELS[nowy-slug] = {"pl": "...", "en": "...", "es": "...", "uk": "..."}`
   - `DOCS.append(("B1", "nowy-slug", ["pl", "en", "es", "uk"]))`
4. `python build_podprojekt_b.py --only nowy-slug`
5. `python scripts/_validate_dokumenty_dist.py`

## Dodawanie nowego kursu (inny zawód / temat)

1. Utwórz katalog `$EGIDA_KURS_ROOT/{nowy_kurs_slug}/podprojekt-b/` z analogiczną strukturą do `kurs_tartak`.
2. Skopiuj 50 plików MD jako wzór, dostosuj treść do nowego zawodu (modyfikuj wzmianki o module M1/M2/M3, kompetencjach, zakresie BHP).
3. `python build_podprojekt_b.py --course-slug nowy_kurs_slug`

> **Faza C (przyszłość)**: skill / plugin Claude Code automatyzuje kroki 1-2 (research treści zawodu, redakcja, tłumaczenia trzech języków na podstawie polskiego oryginału, walidacja).

## Roadmap

- **Część 2**: deploy hubowy (indeks `dokumenty/index.html`, integracja z chrome.js, deploy via tar+ssh).
- **Część 3**: portacja istniejących skryptów buildowych Pakietu A (kurs HTML M1/M2/M3) do tego repo + refaktor portability (env vars / CLI args zamiast hardcoded paths).
- **Część 4**: skill / plugin Claude Code dla pracowników Fundacji EGIDA, automatyzujący cały workflow tworzenia nowego kursu.

## Licencja

[MIT License](LICENSE): można używać, modyfikować i dystrybuować. Atrybucja do Fundacji pomocy prawnej EGIDA mile widziana.

## Powiązane projekty

- **Treść kursu Praca w tartaku** (Pakiet A: lekcje, prezentacje, materiały trenera): repozytorium prywatne.
- **Pakiet B (50 dokumentów MD)**: repozytorium prywatne.
- **Hub online**: `prezentacje.m-b.legal/kurs-tartak/` (chronione PIN).

## Autorzy

Fundacja pomocy prawnej EGIDA, Opole. Współpraca: kancelaria Michał Bartosiński (m-b.legal).
