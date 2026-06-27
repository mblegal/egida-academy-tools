export const meta = {
  name: 'egida-bud-diacritics',
  description: 'Przywraca poprawne polskie znaki diakrytyczne w plikach PL (szczegolowy, dziennik, scenariusze w1-w4) bez zmiany tresci',
  phases: [{ title: 'Diakrytyka' }],
}

const BASE = 'C:/Users/mbart/Documents/EGIDA/egida-academy-tools/prace ogolnobudowlane/src'

const FILES = [
  BASE + '/program-szczegolowy/pl.md',
  BASE + '/dziennik-kursu/pl.md',
  BASE + '/_parts/scen-pl-w1.md',
  BASE + '/_parts/scen-pl-w2.md',
  BASE + '/_parts/scen-pl-w3.md',
  BASE + '/_parts/scen-pl-w4.md',
]

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    file: { type: 'string' },
    dia_per_1k_letters: { type: 'number', description: 'gestosc diakrytykow na 1000 liter (cel >40)' },
    em_dashes: { type: 'integer' },
    lines_unchanged: { type: 'boolean', description: 'czy liczba linii i struktura zachowane' },
    ok: { type: 'boolean' },
  },
  required: ['file', 'dia_per_1k_letters', 'em_dashes', 'lines_unchanged', 'ok'],
}

function prompt(path) {
  return `Jestes korektorem jezyka polskiego. Twoje JEDYNE zadanie: dodac POPRAWNE polskie znaki diakrytyczne do istniejacego tekstu, NIC innego nie zmieniajac.

KROK 1: Przeczytaj (Read) plik:
${path}

KROK 2: Przepisz tekst dodajac wszystkie brakujace polskie znaki diakrytyczne: a z ogonkiem, c z kreska, e z ogonkiem, l z kreska, n z kreska, o z kreska, s z kreska, z z kreska, z z kropka (oraz wielkie litery). Popraw KAZDE slowo, ktore tego wymaga (np. "ogolnobudowlanych" -> z diakrytyka, "dzien" -> z diakrytyka, "cwiczenie" -> z diakrytyka, "bezpieczenstwo" -> z diakrytyka, "narzedzia" -> z diakrytyka, "wiedza/umiejetnosci" -> z diakrytyka, "SOI" -> "SOI" zapisz jako srodki ochrony indywidualnej skrot z S z kreska). Zadbaj tez o poprawna polska gramatyke ortografii (tylko znaki diakrytyczne, bez zmiany form).

BEZWZGLEDNE ZASADY ZACHOWANIA TRESCI:
- NIE zmieniaj struktury Markdown: te same naglowki (te same poziomy #, ## , ###, ####), te same tabele (wszystkie wiersze i kolumny), listy, pola do wypelnienia (kropki), liczby, zakresy (np. 2-5 mm), godziny (np. 6-8 h), procenty.
- NIE dodawaj, nie usuwaj, nie przestawiaj ani nie przeredagowuj zdan. Ta sama liczba akapitow, wierszy tabel i pozycji list.
- NIE tlumacz. Terminy angielskie/lacinskie, nazwy wlasne, skroty (BHP, EFS+, DOCX, PDF, ISO) zostaw bez zmian.
- ZERO znakow em dash (dlugiej pauzy). Jesli wystepuja, zamien na " - " (zwykly lacznik). Liczby dziesietne z przecinkiem.
- Zmieniasz WYLACZNIE litery na ich diakrytyczne odpowiedniki tam, gdzie wymaga tego poprawna polszczyzna.

KROK 3: Zapisz (Write) poprawiony tekst pod DOKLADNIE ta sama sciezka (nadpisz):
${path}

KROK 4: Zwroc status: sciezka, gestosc diakrytykow na 1000 liter (policz znaki a/c/e/l/n/o/s/z diakrytyczne podzielone przez liczbe liter * 1000; cel ponad 40), liczba em dash (ma byc 0), czy liczba linii i struktura zachowane (true/false), ok.`
}

const results = await parallel(FILES.map((f) => () =>
  agent(prompt(f), { label: 'dia:' + f.split('/').pop(), phase: 'Diakrytyka', schema: SCHEMA, agentType: 'general-purpose', effort: 'high' })
))

return { results: results.filter(Boolean) }
