export const meta = {
  name: 'egida-kurs-bud-content',
  description: 'Generuje tresc kursu prac ogolnobudowlanych (kostka brukowa + BHP) PL/EN/ES: program ogolny, szczegolowy, scenariusze, dziennik',
  phases: [
    { title: 'PL' },
    { title: 'Tlumaczenia' },
  ],
}

// ============================================================
// Sciezki docelowe (Write tool zapisuje pliki bezposrednio)
// ============================================================
const BASE = 'C:/Users/mbart/Documents/EGIDA/egida-academy-tools/prace ogolnobudowlane/src'
const PARTS = BASE + '/_parts'

// ============================================================
// SZKIELET KURSU - jedyne zrodlo prawdy dla wszystkich dokumentow.
// Kazdy agent dostaje ten tekst, dzieki czemu wszystkie 4 dokumenty
// opisuja DOKLADNIE ten sam kurs (te same dni, bloki, godziny, tematy).
// ============================================================
const COURSE = `
KURS: "Przygotowanie zawodowe do prac ogolnobudowlanych (ze specjalizacja: ukladanie kostki brukowej)".
ORGANIZATOR: Fundacja pomocy prawnej EGIDA (kurs bezplatny dla cudzoziemcow legalnie przebywajacych w Polsce; powstaje z potencjalu projektu partnerstwa Fundacji SMART i EGIDA, dofinansowanego z EFS+).
ADRESACI: cudzoziemcy przybyli do Polski, bez wymaganego doswiadczenia budowlanego, rozni poziomem znajomosci jezyka polskiego. Materialy w trzech jezykach (PL/EN/ES) wspieraja nauke. Akcent: bezpieczenstwo (BHP) i praktyczne umiejetnosci.
CEL: przygotowac uczestnika do podjecia pracy pomocnika/brukarza na budowie, ze szczegolnym przygotowaniem do ukladania kostki brukowej, z silnym fundamentem BHP. Po kursie uczestnik ma szanse zatrudnienia na tej samej budowie, na ktorej odbywa kurs.

MIEJSCE I MODEL: zajecia odbywaja sie na terenie PRAWDZIWEJ, CZYNNEJ BUDOWY. Schemat dnia: blok teoretyczny rano (zaplecze/kontener socjalny lub wydzielona strefa), nastepnie OBSERWACJA na budowie jak dana partia materialu wyglada w praktyce, potem cwiczenie praktyczne pod nadzorem, na koniec krotkie omowienie. Po kazdej partii materialu kursanci obserwuja realne wykonanie na budowie.
CZAS TRWANIA: 1 miesiac = 4 tygodnie = 20 dni roboczych (poniedzialek-piatek), 6-8 godzin dziennie (przyjmij ok. 7 h zajec dziennie: ~2,5 h teorii, ~3,5 h obserwacji i cwiczen, ~0,5 h omowienia, oprocz przerw). Lacznie ok. 140 godzin.

STRUKTURA - 4 MODULY (tygodnie), 20 dni:

MODUL 1 (Tydzien 1): Wprowadzenie, BHP i podstawy budowy
- Dzien 1: Wprowadzenie do kursu i budowy. Organizacja budowy, uczestnicy procesu budowlanego i role (kierownik budowy, majster/brygadzista, brukarz, pomocnik, operator), dokumenty na budowie, regulamin i dyscyplina, podstawowy slownik budowy po polsku. Obserwacja: obchod budowy, identyfikacja stref i stanowisk.
- Dzien 2: BHP I. Podstawy prawne BHP, najczestsze zagrozenia na budowie, srodki ochrony indywidualnej ( kask, obuwie ochronne, kamizelka odblaskowa, rekawice, okulary, ochronniki sluchu, ochrona drog oddechowych ), znaki bezpieczenstwa, strefy niebezpieczne, porzadek na stanowisku. Obserwacja: prawidlowe stosowanie SOI na budowie.
- Dzien 3: BHP II. Prace szczegolnie niebezpieczne, podstawy pracy na wysokosci, zagrozenia przy wykopach, reczne prace transportowe i dzwiganie (dopuszczalne normy), prad i narzedzia, halas i pyl, pierwsza pomoc, postepowanie w razie wypadku, ewakuacja. Obserwacja: instruktaz stanowiskowy, apteczka, drogi ewakuacyjne, punkt zborny.
- Dzien 4: Materialy budowlane. Kruszywa (piasek, kliniec, tluczen, frakcje), cement, woda, beton i zaprawy, kostka brukowa betonowa (rodzaje, grubosci 6 i 8 cm, ksztalty, kolory), obrzeza i krawezniki, geowloknina. Magazynowanie, paletowanie, transport reczny i rozladunek (BHP). Obserwacja: sklad materialow, palety kostki, oznaczenia.
- Dzien 5: Narzedzia i sprzet. Narzedzia reczne (mlotek gumowy, lopata, grabie, taczka, poziomica, sznur murarski, lata, katownik), pomiarowe (miara, niwelator/lata niwelacyjna, waz wodny, niwelator laserowy), elektronarzedzia (przecinarka, szlifierka katowa), zageszczarka plytowa i ubijak. BHP narzedzi. Podstawy pomiaru i wytyczania. POWTORKA tygodnia + TEST 1. Obserwacja: praca zageszczarka.

MODUL 2 (Tydzien 2): Roboty ziemne, podbudowa i przygotowanie podloza
- Dzien 6: Rysunek i pomiar. Czytanie prostych rysunkow i projektu nawierzchni, rzedne, spadki (min. 1-2% dla odwodnienia), kierunek odplywu wody, repery, wytyczanie obrysu, palikowanie, sznury. Obserwacja: wytyczanie powierzchni.
- Dzien 7: Roboty ziemne. Zdjecie humusu, korytowanie, glebokosc koryta zalezna od konstrukcji nawierzchni, BHP wykopow (skarpy, zabezpieczenie scian, media podziemne), odwoz urobku, prace reczne i maszynowe, zageszczanie dna koryta. Obserwacja: korytowanie i niwelacja dna.
- Dzien 8: Podbudowa. Warstwy konstrukcyjne (warstwa odsaczajaca, podbudowa zasadnicza), kruszywa lamane, grubosci warstw, wbudowanie i profilowanie, zageszczanie warstwami (wskaznik zageszczenia), rola wody, geowloknina/separacja. Obserwacja: ukladanie i zageszczanie podbudowy.
- Dzien 9: Obrzeza i krawezniki. Lawa betonowa (z oporem), osadzanie kraweznika i obrzeza w linii i poziomie wedlug sznura, spoiny, luki i narozniki, betonowanie lawy. Obserwacja: osadzanie kraweznikow.
- Dzien 10: Podsypka. Rodzaje (cementowo-piaskowa ok. 1:4, piaskowa), grubosc 3-5 cm po zageszczeniu, prowadnice/rury dystansowe, sciaganie lata, rownosc, zasada nie chodzenia po gotowej podsypce. POWTORKA + TEST 2. Obserwacja: przygotowanie i sciaganie podsypki.

MODUL 3 (Tydzien 3): Ukladanie kostki brukowej (specjalizacja)
- Dzien 11: Zasady ukladania. Wzory (cegielka, jodelka 45 i 90 stopni, rzedowy), spoiny 2-5 mm, uklad "z czola" (z juz ulozonej powierzchni, by nie deptac podsypki), kierunek i linia, sznur prowadzacy, pierwszy rzad jako baza. Cwiczenie: pierwsze rzedy.
- Dzien 12: Ukladanie plaszczyzny. Utrzymanie wzoru i rownych spoin, kontrola linii i poziomu, korekta mlotkiem gumowym, mieszanie kostki z kilku palet (rozne odcienie), dylatacje, tempo pracy. Cwiczenie: ukladanie pola.
- Dzien 13: Ciecie i dopasowanie. Przecinarka stolowa i katowa, gilotyna, docinanie przy kraweznikach, studzienkach, naroznikach, trasowanie/znakowanie, BHP ciecia (pyl krzemionkowy - ciecie na mokro, ochrona oczu, sluchu i drog oddechowych, oslona tarczy). Cwiczenie: docinki.
- Dzien 14: Spadki, odwodnienie i uzbrojenie. Dopasowanie do studzienek, wpustow, wlazow, korytek liniowych, regulacja wysokosci elementow, zachowanie spadku, obrobka wokol elementow. Obserwacja i cwiczenie: obrobka studzienek.
- Dzien 15: Fugowanie i zageszczanie. Zamulanie spoin (piasek, piasek kwarcowy; ewentualnie spoiny stabilizowane), zamiatanie, zageszczanie powierzchni zageszczarka z oslona/mata gumowa (nigdy bezposrednio po kostce bez oslony), kolejnosc (fugowanie - zageszczenie - dofugowanie), pielegnacja i czystosc. POWTORKA + TEST 3. Cwiczenie: fugowanie i zageszczanie pola.

MODUL 4 (Tydzien 4): Wykonczenia, jakosc, prace uzupelniajace i zatrudnienie
- Dzien 16: Kontrola jakosci nawierzchni. Rownosc (lata 2-4 m, dopuszczalny przeswit), spadki, wzor i spoiny, brak "klawiszowania" kostek, typowe wady (zanizenia, nierownosci, zle spadki, zabrudzenia) i naprawy (przelozenie kostki). Odbior powierzchni. Cwiczenie: pomiar rownosci i spadkow.
- Dzien 17: Inne prace ogolnobudowlane. Drobne prace murarskie (zaprawa, pustak/cegla - podstawy), betonowanie drobnych elementow (obrzeza, fundamenty punktowe, stopnie - przeglad), podstawy tynkow/obrzutek (przeglad), prace porzadkowe i pomocnicze, wspolpraca z innymi brygadami. Obserwacja: wybrane prace na budowie.
- Dzien 18: Organizacja i jakosc pracy. Planowanie dnia, praca zespolowa, tempo i wydajnosc (przykladowe normy m2 na dzien), komunikacja z brygadzista, zglaszanie problemow, dbalosc o sprzet i materialy, etyka i kultura pracy na budowie, oszczednosc materialu. Obserwacja: organizacja stanowiska.
- Dzien 19: Praktyka zintegrowana. Samodzielne wykonanie fragmentu nawierzchni (od podsypki, przez ukladanie, docinki, po fugowanie) w zespole, pod nadzorem - zadanie zaliczeniowe praktyczne oceniane wedlug karty oceny.
- Dzien 20: Egzamin i zatrudnienie. Egzamin wewnetrzny (test teoretyczny + zadanie praktyczne), omowienie wynikow, sciezka zatrudnienia na tej budowie (rozmowa, warunki, stanowisko pomocnika/brukarza), formalnosci legalnej pracy cudzoziemca w Polsce (przeglad: zezwolenie na prace lub oswiadczenie, umowa, wstepne szkolenie BHP u pracodawcy, badania), wydanie zaswiadczen o ukonczeniu kursu. Zakonczenie.

OCENIANIE I ZALICZENIE: 3 testy czastkowe (po module 1, 2, 3), biezaca ocena obserwacji i cwiczen praktycznych (karty obserwacji), zadanie zaliczeniowe praktyczne (Dzien 19), egzamin koncowy teoretyczno-praktyczny (Dzien 20). Warunek ukonczenia: frekwencja, zaliczenie testow i pozytywna ocena praktyczna. Absolwent otrzymuje zaswiadczenie o ukonczeniu kursu.
KADRA I WARUNKI: trener-praktyk budowlany/brukarz z doswiadczeniem, wsparcie jezykowe/tlumaczeniowe, dostep do czynnej budowy, materialy i sprzet, SOI dla uczestnikow, zaplecze socjalne.
`

// ============================================================
// PODSTAWY PRAWNE BHP (zweryfikowane w IURA) - tylko te cytowac.
// ============================================================
const LEGAL = `
PODSTAWY PRAWNE BHP - cytuj WYLACZNIE ponizsze akty, nie wymyslaj innych numerow ani sygnatur:
- Ustawa z dnia 26 czerwca 1974 r. - Kodeks pracy (tekst jednolity), Dzial X "Bezpieczenstwo i higiena pracy", w szczegolnosci: art. 207 (obowiazki pracodawcy w zakresie BHP), art. 211 (podstawowy obowiazek pracownika przestrzegania przepisow i zasad BHP), art. 237(3) (zakaz dopuszczenia pracownika do pracy bez wymaganego szkolenia BHP), art. 237(6)-237(9) (srodki ochrony indywidualnej i odziez robocza).
- Rozporzadzenie Ministra Pracy i Polityki Socjalnej z dnia 26 wrzesnia 1997 r. w sprawie ogolnych przepisow bezpieczenstwa i higieny pracy (tekst jednolity).
- Rozporzadzenie Ministra Infrastruktury z dnia 6 lutego 2003 r. w sprawie bezpieczenstwa i higieny pracy podczas wykonywania robot budowlanych (Dz.U. 2003 nr 47 poz. 401) - podstawowy akt dla budowy.
- Rozporzadzenie Ministra Gospodarki z dnia 20 wrzesnia 2001 r. w sprawie bezpieczenstwa i higieny pracy podczas eksploatacji maszyn i innych urzadzen technicznych do robot ziemnych, budowlanych i drogowych (dotyczy m.in. zageszczarek).
- Rozporzadzenie Ministra Gospodarki i Pracy z dnia 27 lipca 2004 r. w sprawie szkolenia w dziedzinie bezpieczenstwa i higieny pracy (instruktaz ogolny i stanowiskowy).
- Ustawa z dnia 7 lipca 1994 r. - Prawo budowlane (m.in. rola kierownika budowy, plan bezpieczenstwa i ochrony zdrowia BIOZ - art. 21a).
Cytuj akty po nazwie i dacie. Przy odwolaniu do artykulu podawaj artykul ogolnie (np. "art. 207 Kodeksu pracy"). Nie cytuj doslownie pelnej tresci przepisow - parafrazuj obowiazki prostym jezykiem dla cudzoziemcow.
`

// ============================================================
// STYL - twarde reguly dla kazdego agenta.
// ============================================================
const STYLE = (lang) => `
TWARDE REGULY STYLU (bezwzglednie przestrzegaj):
1. JEZYK: pisz w jezyku "${lang}". ${lang === 'pl' ? 'Uzywaj POPRAWNYCH polskich znakow diakrytycznych (a-ogonek, c-kreska, e-ogonek, l-kreska, n, o-kreska, s, z-kreska, z-kropka) we WSZYSTKICH slowach. To wymog twardy.' : ''}${lang === 'es' ? 'Uzywaj POPRAWNEJ ortografii hiszpanskiej: akcenty (a/e/i/o/u z akcentem), litera n z tylda, znaki ? i ! odwrocone na poczatku pytan/wykrzyknien. To wymog twardy.' : ''}${lang === 'en' ? 'Use correct, natural professional English.' : ''}
2. ZAKAZ EM DASH: nigdzie nie uzywaj znaku dlugiej pauzy (em dash). Zamiast niego stosuj zwykly lacznik (hyphen) ze spacjami, przecinek, dwukropek, srednik lub nawias. Liczba wystapien em dash w pliku musi byc rowna ZERO.
3. LICZBY DZIESIETNE: ${lang === 'en' ? 'kropka dziesietna (np. 1.5%, 0.25 m).' : 'przecinek dziesietny (np. 1,5%, 0,25 m).'} Zakresy zapisuj lacznikiem bez spacji (np. 2-5 mm, 6-8 h).
4. ODBIORCA: cudzoziemcy rozpoczynajacy prace na polskiej budowie. Pisz jasno, konkretnie, profesjonalnie, ale przystepnie. Unikaj zargonu bez wyjasnienia.
5. ${lang === 'pl' ? 'Wprowadzaj kluczowe polskie slownictwo budowlane z krotkim wyjasnieniem.' : 'PRZY KLUCZOWYM SLOWNICTWIE PODAWAJ POLSKI TERMIN W NAWIASIE, np. "compaction plate (PL: zageszczarka)", bo na budowie polecenia padaja po polsku - uczestnik musi rozpoznac polskie slowo.'}
6. FORMAT: czysty Markdown. Zacznij od jednego naglowka pierwszego poziomu "# <Tytul dokumentu>", potem tresc z naglowkami "##"/"###", listami i TABELAMI Markdown tam gdzie poprawiaja czytelnosc. Bez bloku YAML, bez komentarzy, bez tekstu spoza dokumentu.
7. SPOJNOSC: trzymaj sie DOKLADNIE struktury kursu (te same dni, tematy, godziny). Nie zmieniaj liczby dni ani tematow.
`

// ============================================================
// Definicje jednostek tresci (PL) - kazda to osobny plik/agent.
// ============================================================
const TITLES = {
  ogolny: { pl: 'Program ogolny kursu', en: 'General course programme', es: 'Programa general del curso' },
  szczegolowy: { pl: 'Program szczegolowy kursu', en: 'Detailed course programme', es: 'Programa detallado del curso' },
  dziennik: { pl: 'Dziennik kursu', en: 'Course journal', es: 'Diario del curso' },
  scen: { pl: 'Scenariusze blokow zajec', en: 'Lesson-block scenarios', es: 'Escenarios de los bloques de clase' },
}

function plPrompt(spec) {
  return `Jestes metodykiem ksztalcenia zawodowego i praktykiem budowlanym. Tworzysz OBSZERNE, profesjonalne materialy kursu.

${STYLE('pl')}

OPIS KURSU (zrodlo prawdy, trzymaj sie go scisle):
${COURSE}

${spec.useLegal ? LEGAL : ''}

ZADANIE: napisz dokument "${spec.title}" w jezyku polskim.
${spec.brief}

Dokument ma byc obszerny, konkretny i gotowy do uzytku. Zacznij od "# ${spec.title}".

Zapisz GOTOWY dokument Markdown do pliku (uzyj narzedzia Write) DOKLADNIE pod sciezka:
${spec.path}

Po zapisaniu zwroc krotki status (NIE wklejaj tresci dokumentu).`
}

function trPrompt(spec, lang) {
  const langName = lang === 'en' ? 'angielski (English)' : 'hiszpanski (espanol)'
  return `Jestes profesjonalnym tlumaczem specjalizujacym sie w tekstach technicznych i szkoleniowych (budownictwo, BHP).

${STYLE(lang)}

ZADANIE: przetlumacz na ${langName} dokument zrodlowy z pliku polskiego. Najpierw przeczytaj (Read) plik zrodlowy:
${spec.src}

Przetlumacz CALOSC wiernie i kompletnie (nie skracaj, nie pomijaj tabel ani wierszy). Zachowaj strukture Markdown, naglowki, tabele i listy 1:1. Tytul "# ..." przetlumacz na "${TITLES[spec.doc][lang]}". Terminologie budowlana i BHP tlumacz fachowo i spojnie. Pamietaj o regule 5 stylu: kluczowe terminy techniczne podawaj z polskim odpowiednikiem w nawiasie (PL: ...), bo polecenia na budowie padaja po polsku.

Zapisz GOTOWE tlumaczenie (Write) DOKLADNIE pod sciezka:
${spec.out}

Po zapisaniu zwroc krotki status (NIE wklejaj tresci).`
}

const STATUS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    file: { type: 'string', description: 'sciezka zapisanego pliku' },
    words: { type: 'integer', description: 'przyblizona liczba slow' },
    em_dashes: { type: 'integer', description: 'liczba znakow em dash w pliku (powinno byc 0)' },
    ok: { type: 'boolean' },
  },
  required: ['file', 'words', 'em_dashes', 'ok'],
}

// Jednostki: ogolny, szczegolowy, dziennik (pojedyncze pliki) + scenariusze w 4 czesciach.
const UNITS = [
  {
    id: 'ogolny', doc: 'ogolny', kind: 'doc', useLegal: true,
    title: TITLES.ogolny.pl, path: BASE + '/program-ogolny/pl.md',
    src: BASE + '/program-ogolny/pl.md',
    brief: `Zakres: (1) tytul i krotki opis kursu; (2) adresaci i wymagania wstepne; (3) cel glowny i cele szczegolowe; (4) sylwetka absolwenta jako efekty uczenia sie w podziale na WIEDZE, UMIEJETNOSCI i KOMPETENCJE SPOLECZNE; (5) struktura kursu - 4 moduly/tygodnie w TABELI (modul, tytul, zakres, liczba dni, orientacyjne godziny); (6) wymiar godzinowy (20 dni, ~7 h/dzien, ~140 h); (7) metodyka (teoria + obserwacja na czynnej budowie + cwiczenia pod nadzorem, uczenie przez dzialanie, wsparcie wielojezyczne); (8) warunki realizacji (budowa, sprzet, SOI, kadra); (9) zasady BHP na kursie z podstawami prawnymi; (10) system oceniania i warunki zaliczenia; (11) dokumentacja kursu; (12) sciezka zatrudnienia na budowie po kursie; (13) krotka informacja o organizatorze (Fundacja EGIDA) i finansowaniu (projekt SMART+EGIDA, EFS+). Tabela zbiorcza harmonogramu 20 dni z tematami. Cel objetosci: solidny, wielostronicowy dokument.`,
  },
  {
    id: 'szczegolowy', doc: 'szczegolowy', kind: 'doc', useLegal: true,
    title: TITLES.szczegolowy.pl, path: BASE + '/program-szczegolowy/pl.md',
    src: BASE + '/program-szczegolowy/pl.md',
    brief: `Program szczegolowy DZIEN PO DNIU dla wszystkich 20 dni. Podziel na 4 moduly (tygodnie); kazdy modul poprzedz krotkim wstepem (cel modulu). Dla KAZDEGO z 20 dni podaj: numer i tytul dnia; orientacyjny czas; cele dydaktyczne dnia; tresci teoretyczne (lista zagadnien); zakres obserwacji praktycznej na budowie; cwiczenie praktyczne; efekty uczenia sie dnia; 6-10 kluczowych terminow po polsku (z bardzo krotkim wyjasnieniem). Zaznacz dni z testami (5,10,15) i egzaminem (20). Na koncu sekcja: system oceniania, warunki zaliczenia, wykaz testow i egzaminu. Uzyj tabel lub czytelnych sekcji per dzien. To ma byc najobszerniejszy z dokumentow opisowych.`,
  },
  {
    id: 'dziennik', doc: 'dziennik', kind: 'doc', useLegal: false,
    title: TITLES.dziennik.pl, path: BASE + '/dziennik-kursu/pl.md',
    src: BASE + '/dziennik-kursu/pl.md',
    brief: `Dziennik kursu jako DOKUMENT FORMALNY / SZABLON do wypelniania (z pustymi polami i przykladowymi wierszami oznaczonymi jako przyklad). Zawrzyj: (1) strona tytulowa (nazwa kursu, organizator Fundacja EGIDA, miejsce - budowa, termin, prowadzacy, koordynator) - jako pola do wypelnienia; (2) dane organizacyjne kursu; (3) LISTA UCZESTNIKOW - tabela (lp, imie i nazwisko, kraj pochodzenia, jezyk kontaktu, nr dokumentu/identyfikator, podpis); (4) DZIENNIK ZAJEC - tabela na 20 wierszy (lp, data, dzien tygodnia, modul, temat/blok, liczba godzin, forma: teoria/obserwacja/cwiczenie, prowadzacy, podpis) - wypelnij kolumny modul/temat zgodnie ze szkieletem dla 20 dni, reszte zostaw do wpisania; (5) REJESTR OBECNOSCI - tabela uczestnicy x 20 dni (siatka do zaznaczania); (6) REJESTR SZKOLEN I INSTRUKTAZY BHP - tabela (data, zakres instruktazu, prowadzacy, podpis uczestnika) z odwolaniem do podstaw prawnych; (7) REJESTR OBSERWACJI I CWICZEN PRAKTYCZNYCH (data, zakres, ocena/uwagi); (8) REJESTR TESTOW I OCEN (test 1/2/3, zadanie praktyczne D19, egzamin D20); (9) REJESTR UWAG I ZDARZEN; (10) POTWIERDZENIE UKONCZENIA i wydania zaswiadczen. Dokument praktyczny, gotowy do druku i wypelnienia.`,
  },
]

// Scenariusze - 4 czesci (tygodnie). Kazda czesc = 5 dni.
const WEEKS = [
  { n: 1, days: 'dni 1-5 (Modul 1: Wprowadzenie, BHP, podstawy budowy)' },
  { n: 2, days: 'dni 6-10 (Modul 2: Roboty ziemne, podbudowa, podloze)' },
  { n: 3, days: 'dni 11-15 (Modul 3: Ukladanie kostki brukowej)' },
  { n: 4, days: 'dni 16-20 (Modul 4: Wykonczenia, jakosc, prace uzupelniajace, zatrudnienie)' },
]

for (const w of WEEKS) {
  UNITS.push({
    id: 'scen-w' + w.n, doc: 'scen', kind: 'scen', week: w.n, useLegal: w.n === 1,
    title: TITLES.scen.pl + ' - Tydzien ' + w.n,
    path: PARTS + '/scen-pl-w' + w.n + '.md',
    src: PARTS + '/scen-pl-w' + w.n + '.md',
    brief: `Napisz SCENARIUSZE ZAJEC dla ${w.days}. Dla KAZDEGO z 5 dni tego tygodnia stworz pelny, szczegolowy scenariusz bloku zajec.

STRUKTURA NAGLOWKOW - PRZESTRZEGAJ BEZWZGLEDNIE (dokumenty 4 tygodni musza miec identyczna hierarchie):
- Pierwszy wiersz pliku: "# ${TITLES.scen.pl} - Tydzien ${w.n}" (jedyny naglowek poziomu 1).
- Opcjonalny krotki wstep: "## Wprowadzenie do tygodnia ${w.n}"${w.n === 1 ? ' oraz "## Jak czytac scenariusze" i "## Standardowy rytm dnia"' : ''}.
- Kazdy dzien zaczyna sie naglowkiem poziomu DRUGIEGO: "## Dzien X: <temat>".
- Podsekcje kazdego dnia zawsze na poziomie TRZECIM "###", w tej kolejnosci: "### Naglowek bloku" (dzien, modul, temat, czas, miejsce), "### Cele (wiedza, umiejetnosci, postawy)", "### Materialy, narzedzia i SOI", "### Zagadnienia BHP", "### Przebieg zajec", "### Metody dydaktyczne", "### Sprawdzenie i ocena", "### Slownictwo kluczowe", "### Wskazowki dla trenera (grupa wielojezyczna)", "### Czeste bledy i jak ich unikac".
- ZAKAZ: nie uzywaj "#" poza pierwszym wierszem; nie uzywaj "####" ani glebszych. Tylko "##" (dni i wstep) oraz "###" (podsekcje).

TRESC kazdej podsekcji: NAGLOWEK BLOKU (dzien, tydzien/modul, temat, czas trwania ok. 7 h, miejsce: czynna budowa); CELE; MATERIALY/NARZEDZIA/SOI; BHP dla bloku; PRZEBIEG ZAJEC jako tabela lub lista z czasem i krokami: (1) rozgrzewka jezykowa i powtorka, (2) wprowadzenie teoretyczne, (3) pokaz/demonstracja trenera, (4) obserwacja realnego wykonania na budowie, (5) cwiczenie praktyczne pod nadzorem, (6) omowienie bledow i podsumowanie; METODY; SPRAWDZENIE I OCENA; SLOWNICTWO KLUCZOWE (polskie terminy + krotkie wyjasnienie); WSKAZOWKI DLA TRENERA przy grupie wielojezycznej; CZESTE BLEDY. Dni 5,10,15 obejmuja tez test czastkowy, dzien 19 zadanie zaliczeniowe praktyczne, dzien 20 egzamin koncowy - uwzglednij to. Scenariusze maja byc obszerne i praktyczne.`,
  })
}

// ============================================================
// PIPELINE: dla kazdej jednostki najpierw PL (zapis pliku),
// potem rownolegle tlumaczenia EN i ES (czytaja PL, zapisuja plik).
// pipeline() nie ma bariery: scen-w1 tlumaczy sie gdy scen-w3 dopiero powstaje.
// ============================================================
const results = await pipeline(
  UNITS,
  (u) => agent(plPrompt(u), {
    label: 'PL:' + u.id, phase: 'PL', schema: STATUS_SCHEMA,
    agentType: 'general-purpose', effort: 'high',
  }),
  (plStatus, u) => parallel(['en', 'es'].map((lang) => () => {
    const out = u.kind === 'scen'
      ? PARTS + '/scen-' + lang + '-w' + u.week + '.md'
      : BASE + '/' + (u.doc === 'ogolny' ? 'program-ogolny' : u.doc === 'szczegolowy' ? 'program-szczegolowy' : 'dziennik-kursu') + '/' + lang + '.md'
    return agent(trPrompt({ doc: u.doc, src: u.src, out }, lang), {
      label: lang.toUpperCase() + ':' + u.id, phase: 'Tlumaczenia', schema: STATUS_SCHEMA,
      agentType: 'general-purpose',
    }).then((s) => ({ unit: u.id, lang, status: s }))
  }))
)

// Raport: dla kazdej jednostki tlumaczenia (stage2 = [{en},{es}]).
return {
  note: 'Pliki zapisane bezposrednio na dysku przez agentow.',
  units: UNITS.map((u) => u.id),
  translations: results,
}
