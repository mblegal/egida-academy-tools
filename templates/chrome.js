/* ============================================================
   Kurs tartakowy EGIDA: chrome.js
   PIN gate + globalny lang switch + role-nav IntersectionObserver
   ============================================================ */
(function () {
  'use strict';

  var LS_PIN = 'egida-kurs-pin';
  var LS_LANG = 'egida-kurs-lang';
  var SUPPORTED_LANGS = ['pl', 'en', 'es', 'uk'];
  var PIN_CORRECT = '7301';
  var MAX_ATTEMPTS = 5;

  // ============================================================
  // I18N, slowniki UI hubu dla PL/EN/ES/UK
  // ============================================================
  var I18N = {
    pl: {
      'pin.eyebrow': 'Dostęp PIN',
      'pin.title_html': 'Kurs tartakowy<br><em>Fundacja EGIDA</em>',
      'pin.lead': 'Materiały kursu są chronione kodem PIN. Wprowadź 4-cyfrowy kod otrzymany od koordynatora kursu.',
      'pin.footnote_html': 'Materiały kursu „Praca w tartaku" · Fundacja EGIDA.<br>Kod jest zapamiętywany w przeglądarce do końca sesji.',
      'hdr.eyebrow': 'Fundacja EGIDA',
      'hdr.name_html': 'Praca <em>w tartaku</em>',
      'hdr.pin_state': 'Dostęp aktywny',
      'hdr.skip_link': 'Przejdź do treści',
      'lang.label': 'Język treści',
      'role.nav_label': 'Wybierz swoją rolę',
      'role.1': 'Kursant',
      'role.2': 'Trener',
      'role.3': 'Rekrutacja',
      'role.4': 'O projekcie',
      'role.5': 'Dokumenty',
      'hero.eyebrow': 'Kurs zawodowy · 12 tygodni · 4 języki · bezpłatnie',
      'hero.title_html': 'Zawód operatora tartaku <em>w 12 tygodni</em>',
      'hero.lead': 'Trzy moduły: pomocnik → młodszy operator → operator samodzielny z elementami nadzoru. Materiały w polskim, angielskim, hiszpańskim i ukraińskim: dla kursanta, trenera, rekrutera i koordynatora.',
      'kpi.1.l': 'lekcji × 4 języki',
      'kpi.1.ctx': 'Trzy moduły po 32 lekcje (2h każda). PL/EN/ES/UK.',
      'kpi.2.l': 'artefaktów trenera',
      'kpi.2.ctx': 'Quizy, ćwiczenia, scenariusze, wytyczne × M1/M2/M3.',
      'kpi.3.l': 'materiałów rekrutacji',
      'kpi.3.ctx': 'Program ogólny i szczegółowy × 4 języki.',
      'kpi.4.l': 'słów produkcyjnych',
      'kpi.4.ctx': 'Efekt potencjału budowanego w projekcie SMART + EGIDA.',
      'kpi.5.l': 'typów dokumentów',
      'kpi.5.ctx': 'Pakiet B: umowy, zaświadczenia, regulaminy, RODO, formularz, polityka reklamacji × 4 języki × 3 formaty.',
      'sec.1.n': '01 · Dla kursanta',
      'sec.1.h': 'Trzy moduły po cztery tygodnie',
      'sec.1.d': 'Dwa formaty: interaktywny kurs HTML do samodzielnej nauki oraz prezentacja Reveal.js do projekcji w sali dydaktycznej.',
      'sec.1.mode1': 'Do samodzielnej nauki · 3 moduły · 12 tygodni',
      'sec.1.mode2': 'Do projekcji w sali',
      'sec.2.n': '02 · Dla trenera',
      'sec.2.h': 'Artefakty dydaktyczne Fazy 4',
      'sec.2.d': 'Tabela 3 × 4: wiersze = moduły (M1/M2/M3), kolumny = typ artefaktu. Scenariusze praktyczne (A3) i wytyczne dla trenera (A4) tylko w PL; quizy (A1) i ćwiczenia (A2) w czterech językach.',
      'sec.3.n': '03 · Dla rekrutacji',
      'sec.3.h': 'Dokumenty dla kandydatów i partnerów',
      'sec.3.d': 'Program ogólny i szczegółowy (96 lekcji) z opisami modułów i celami dydaktycznymi. Kliknij kartę: wersja językowa podąża za globalnym przełącznikiem w headerze.',
      'sec.4.n': '04 · O projekcie',
      'sec.4.h': 'Fundamenty lokalnej polityki migracyjnej',
      'sec.4.d': 'Kurs powstał dzięki potencjałowi budowanemu przez Fundacje SMART i EGIDA w projekcie „Budowa fundamentów pod lokalną politykę migracyjną i integracyjną" (FEO 2021-2027, Działanie 06.03). Z tego potencjału wyrastają kolejne kursy, wszystkie bezpłatne dla cudzoziemców.',
      'sec.5.n': '05 · Dokumenty kursu',
      'sec.5.h': 'Pakiet dokumentów formalnych',
      'sec.5.d': 'Wszystkie dokumenty kursowe (umowa, zaświadczenia, regulamin, RODO, formularz rekrutacyjny, polityka reklamacji, umowa współorganizacji) w czterech językach (PL/EN/ES/UK) i trzech formatach (HTML do podglądu online, DOCX do edycji, PDF do druku).',
      'sec.5.cta': 'Otwórz listę dokumentów →',
      'tbl.corner': 'Moduł × typ',
      'pin.fields_label': 'Pole 4-cyfrowego kodu PIN',
      // karty kursanta, moduły interaktywne
      'card.kursant.M1.eye': 'Moduł 01 · Pomocnik',
      'card.kursant.M1.title': 'BHP, drewno, rytm dnia',
      'card.kursant.M1.bullets_html': '<li>BHP i ŚOI w tartaku</li><li>gatunki drewna, narzędzia ręczne</li><li>stanowisko, rytm zmiany, komunikacja</li>',
      'card.kursant.M1.time': '4 tyg. · ~32 h',
      'card.kursant.M1.size': '3,3 MB',
      'card.kursant.M2.eye': 'Moduł 02 · Młodszy operator',
      'card.kursant.M2.title': 'Pilarka taśmowa, trak pionowy',
      'card.kursant.M2.bullets_html': '<li>obsługa pilarki taśmowej i traka</li><li>dokumenty techniczne, karta stanowiska</li><li>usterki, raportowanie</li>',
      'card.kursant.M2.time': '4 tyg. · ~32 h',
      'card.kursant.M2.size': '3,5 MB',
      'card.kursant.M3.eye': 'Moduł 03 · Samodzielny',
      'card.kursant.M3.title': 'Koordynacja zmiany, audyty',
      'card.kursant.M3.bullets_html': '<li>prowadzenie zmiany 8 h, nadzór nad 2-4 M2</li><li>reklamacje klienta, KC art. 556-563</li><li>audyty FSC, ISO 9001</li>',
      'card.kursant.M3.time': '4 tyg. · ~32 h',
      'card.kursant.M3.size': '6,5 MB',
      // karty kursanta, prezentacje Reveal.js
      'card.kursant.D1.eye': 'Prezentacja M1 · Reveal.js',
      'card.kursant.D1.title': 'Slajdy M1 (Reveal.js)',
      'card.kursant.D1.time': '163 sekcji',
      'card.kursant.D1.size': '2,8 MB',
      'card.kursant.D2.eye': 'Prezentacja M2 · Reveal.js',
      'card.kursant.D2.title': 'Slajdy M2 (Reveal.js)',
      'card.kursant.D2.time': '163 sekcji',
      'card.kursant.D2.size': '2,7 MB',
      'card.kursant.D3.eye': 'Prezentacja M3 · Reveal.js',
      'card.kursant.D3.title': 'Slajdy M3 (Reveal.js)',
      'card.kursant.D3.time': '147 sekcji',
      'card.kursant.D3.size': '4,4 MB',
      // tabela trenera, nazwy kolumn (artefakty)
      'card.trener.col.A1.name': 'Quiz uzupełniający',
      'card.trener.col.A2.name': 'Ćwiczenia teoretyczne',
      'card.trener.col.A3.name': 'Scenariusze praktyczne',
      'card.trener.col.A4.name': 'Wytyczne dla trenera',
      // tabela trenera, opisy wierszy (moduły)
      'card.trener.row.M1.desc': 'BHP, drewno, rytm dnia',
      'card.trener.row.M2.desc': 'Pilarka, trak, usterki',
      'card.trener.row.M3.desc': 'Koordynacja, reklamacje, FSC',
      // karty rekrutacja
      'card.rekrutacja.D1.eye': 'D1 · program ogólny',
      'card.rekrutacja.D1.title': 'Program ogólny kursu',
      'card.rekrutacja.D1.desc': 'Jednostronicowy dokument z tabelami modułów, artefaktów i harmonogramu cyklu 2026/2027.',
      'card.rekrutacja.D1.meta': '1 468 słów · tabele · tylko PL',
      'card.rekrutacja.D2.eye': 'D2 · program szczegółowy',
      'card.rekrutacja.D2.title': 'Program szczegółowy 96 lekcji',
      'card.rekrutacja.D2.desc': 'Każda lekcja: tytuł, czas, cel dydaktyczny, 5-8 kluczowych terminów polskich.',
      'card.rekrutacja.D2.meta': '~6-7 tys. słów',
      // karta projektu
      'card.projekt.eye': 'projekt · SMART + EGIDA · Opole',
      'card.projekt.title': 'Budowa fundamentów pod lokalną politykę migracyjną i integracyjną',
      'card.projekt.desc': 'Partnerstwo Fundacji SMART (lider) i EGIDA. Cel: rozbudowa potencjału obu organizacji do uruchomienia w Opolu ośrodka integracji cudzoziemców w modelu one-stop-shop. Budżet 500 000 zł, dofinansowanie 475 000 zł z EFS+ i budżetu państwa. Wniosek FEOP.06.03-IZ.00-0006/25.',
      'card.dokumenty.eye': 'Pakiet B · 13 typów × 4 języki × 3 formaty',
      'card.dokumenty.title': 'Otwórz listę dokumentów kursu',
      'card.dokumenty.desc': 'Umowa kursu, zaświadczenia o odbywaniu i ukończeniu Modułów oraz całego Kursu, zaświadczenia praktyki absolwenckiej, regulamin Kursu, klauzula informacyjna RODO i zgody, formularz rekrutacyjny, polityka reklamacji i odwołań, umowa współorganizacji.',
      // stopka
      'footer.logos_label': 'Partnerzy i finansowanie projektu',
      'footer.disclaimer_html': '<b>Fundacja na rzecz edukacji SMART</b> (lider) w partnerstwie z <b>Fundacją pomocy prawnej EGIDA</b> realizuje projekt „Budowa fundamentów pod lokalną politykę migracyjną i integracyjną" (wniosek FEOP.06.03-IZ.00-0006/25, <b>FEO 2021-2027, Działanie 06.03: Budowanie potencjału partnerów społecznych oraz organizacji społeczeństwa obywatelskiego</b>, dofinansowanie 475 000 zł ze środków EFS+ i budżetu państwa). Celem projektu jest rozbudowa potencjału obu organizacji do uruchomienia w Opolu lokalnego ośrodka integracji cudzoziemców w modelu one-stop-shop. Kurs „Praca w tartaku" powstał jako owoc kompetencji i zasobów zbudowanych w ramach tego projektu.'
    },
    en: {
      'pin.eyebrow': 'PIN access',
      'pin.title_html': 'Sawmill course<br><em>EGIDA Foundation</em>',
      'pin.lead': 'Course materials are protected by a PIN. Enter the 4-digit code received from the course coordinator.',
      'pin.footnote_html': 'Course „Work in a Sawmill" · EGIDA Foundation.<br>The code is stored in your browser for the current session.',
      'hdr.eyebrow': 'EGIDA Foundation',
      'hdr.name_html': 'Work <em>in a sawmill</em>',
      'hdr.pin_state': 'Access active',
      'hdr.skip_link': 'Skip to content',
      'lang.label': 'Content language',
      'role.nav_label': 'Choose your role',
      'role.1': 'Trainee',
      'role.2': 'Trainer',
      'role.3': 'Recruitment',
      'role.4': 'About the project',
      'role.5': 'Documents',
      'hero.eyebrow': 'Vocational course · 12 weeks · 4 languages · free',
      'hero.title_html': 'Become a sawmill operator <em>in 12 weeks</em>',
      'hero.lead': 'Three modules: helper → junior operator → autonomous operator with supervisory elements. Materials in Polish, English, Spanish and Ukrainian: for trainee, trainer, recruiter and coordinator.',
      'kpi.1.l': 'lessons x 4 languages',
      'kpi.1.ctx': 'Three modules, 32 lessons each (2h). PL/EN/ES/UK.',
      'kpi.2.l': 'trainer artefacts',
      'kpi.2.ctx': 'Quizzes, exercises, role-plays, guides x M1/M2/M3.',
      'kpi.3.l': 'recruitment materials',
      'kpi.3.ctx': 'General programme and detailed programme x 4 languages.',
      'kpi.4.l': 'production words',
      'kpi.4.ctx': 'Fruit of the capacity built in the SMART + EGIDA project.',
      'kpi.5.l': 'document types',
      'kpi.5.ctx': 'Package B: agreements, certificates, regulations, GDPR, application form, complaints policy x 4 languages x 3 formats.',
      'sec.1.n': '01 · For the trainee',
      'sec.1.h': 'Three modules, four weeks each',
      'sec.1.d': 'Two formats: interactive HTML course for self-study and Reveal.js presentation for classroom projection.',
      'sec.1.mode1': 'For self-study · 3 modules · 12 weeks',
      'sec.1.mode2': 'For classroom projection',
      'sec.2.n': '02 · For the trainer',
      'sec.2.h': 'Phase 4 didactic artefacts',
      'sec.2.d': 'Table 3 x 4: rows = modules (M1/M2/M3), columns = artefact type. Practical role-plays (A3) and guides for trainers (A4) in Polish only; quizzes (A1) and exercises (A2) in four languages.',
      'sec.3.n': '03 · For recruitment',
      'sec.3.h': 'Documents for candidates and partners',
      'sec.3.d': 'General programme and detailed programme (96 lessons) with module descriptions and learning objectives. Click a card; the language version follows the global switch in the header.',
      'sec.4.n': '04 · About the project',
      'sec.4.h': 'Foundations of local migration policy',
      'sec.4.d': 'The course grew out of the capacity built by the SMART and EGIDA Foundations in the project „Foundations for a local migration and integration policy" (FEO 2021-2027, Measure 06.03). From that capacity further courses keep emerging, all free of charge for foreign nationals.',
      'sec.5.n': '05 · Course documents',
      'sec.5.h': 'Formal documents package',
      'sec.5.d': 'All course documents (agreement, certificates, regulations, GDPR, application form, complaints policy, co-organization agreement) in four languages (PL/EN/ES/UK) and three formats (HTML for online preview, editable DOCX, printable PDF).',
      'sec.5.cta': 'Open document list ->',
      'tbl.corner': 'Module x type',
      'pin.fields_label': '4-digit PIN code field',
      // trainee cards, interactive modules
      'card.kursant.M1.eye': 'Module 01 · Helper',
      'card.kursant.M1.title': 'OSH, wood, daily rhythm',
      'card.kursant.M1.bullets_html': '<li>OSH and PPE in the sawmill</li><li>wood species, hand tools</li><li>workstation, shift rhythm, communication</li>',
      'card.kursant.M1.time': '4 weeks · ~32 h',
      'card.kursant.M1.size': '3.3 MB',
      'card.kursant.M2.eye': 'Module 02 · Junior operator',
      'card.kursant.M2.title': 'Band saw, vertical frame saw',
      'card.kursant.M2.bullets_html': '<li>operating the band saw and frame saw</li><li>technical documents, workstation card</li><li>faults, reporting</li>',
      'card.kursant.M2.time': '4 weeks · ~32 h',
      'card.kursant.M2.size': '3.5 MB',
      'card.kursant.M3.eye': 'Module 03 · Autonomous',
      'card.kursant.M3.title': 'Shift coordination, audits',
      'card.kursant.M3.bullets_html': '<li>running an 8 h shift, supervising 2-4 M2</li><li>customer complaints, Polish Civil Code art. 556-563</li><li>FSC, ISO 9001 audits</li>',
      'card.kursant.M3.time': '4 weeks · ~32 h',
      'card.kursant.M3.size': '6.5 MB',
      // trainee cards, Reveal.js decks
      'card.kursant.D1.eye': 'Presentation M1 · Reveal.js',
      'card.kursant.D1.title': 'Slides M1 (Reveal.js)',
      'card.kursant.D1.time': '163 sections',
      'card.kursant.D1.size': '2.8 MB',
      'card.kursant.D2.eye': 'Presentation M2 · Reveal.js',
      'card.kursant.D2.title': 'Slides M2 (Reveal.js)',
      'card.kursant.D2.time': '163 sections',
      'card.kursant.D2.size': '2.7 MB',
      'card.kursant.D3.eye': 'Presentation M3 · Reveal.js',
      'card.kursant.D3.title': 'Slides M3 (Reveal.js)',
      'card.kursant.D3.time': '147 sections',
      'card.kursant.D3.size': '4.4 MB',
      // trainer table, column names (artefacts)
      'card.trener.col.A1.name': 'Supplementary quiz',
      'card.trener.col.A2.name': 'Theoretical exercises',
      'card.trener.col.A3.name': 'Practical role-plays',
      'card.trener.col.A4.name': 'Guides for trainers',
      // trainer table, row descriptions (modules)
      'card.trener.row.M1.desc': 'OSH, wood, daily rhythm',
      'card.trener.row.M2.desc': 'Band saw, frame saw, faults',
      'card.trener.row.M3.desc': 'Coordination, complaints, FSC',
      // recruitment cards
      'card.rekrutacja.D1.eye': 'D1 · general programme',
      'card.rekrutacja.D1.title': 'General course programme',
      'card.rekrutacja.D1.desc': 'Single-page document with module, artefact and 2026/2027 schedule tables.',
      'card.rekrutacja.D1.meta': '1,468 words · tables · Polish only',
      'card.rekrutacja.D2.eye': 'D2 · detailed programme',
      'card.rekrutacja.D2.title': 'Detailed programme of 96 lessons',
      'card.rekrutacja.D2.desc': 'Each lesson: title, time, learning objective, 5-8 key Polish terms.',
      'card.rekrutacja.D2.meta': '~6-7 thousand words',
      // project card
      'card.projekt.eye': 'project · SMART + EGIDA · Opole',
      'card.projekt.title': 'Foundations for a local migration and integration policy',
      'card.projekt.desc': 'Partnership of the SMART Foundation (lead) and EGIDA. Goal: build the capacity of both organisations to launch a one-stop-shop centre for the integration of foreigners in Opole. Budget PLN 500,000, co-financing PLN 475,000 from ESF+ and the state budget. Application FEOP.06.03-IZ.00-0006/25.',
      'card.dokumenty.eye': 'Package B · 13 types x 4 languages x 3 formats',
      'card.dokumenty.title': 'Open course documents list',
      'card.dokumenty.desc': 'Course agreement, certificates of attendance and completion of Modules and the whole Course, graduate apprenticeship certificates, course regulations, GDPR information notice and consents, application form, complaints and appeals policy, co-organization agreement.',
      // footer
      'footer.logos_label': 'Project partners and funding',
      'footer.disclaimer_html': '<b>SMART Foundation for Education</b> (lead) in partnership with the <b>EGIDA Foundation for Legal Aid</b> implements the project „Foundations for a local migration and integration policy" (application FEOP.06.03-IZ.00-0006/25, <b>FEO 2021-2027, Measure 06.03: Building the capacity of social partners and civil-society organisations</b>, co-financing PLN 475,000 from ESF+ and the state budget). The project goal is to build the capacity of both organisations to launch a one-stop-shop centre for the integration of foreigners in Opole. The course „Work in a Sawmill" emerged as a fruit of the competences and resources built within this project.'
    },
    es: {
      'pin.eyebrow': 'Acceso PIN',
      'pin.title_html': 'Curso del aserradero<br><em>Fundación EGIDA</em>',
      'pin.lead': 'Los materiales del curso están protegidos por un código PIN. Introduce el código de 4 dígitos recibido del coordinador del curso.',
      'pin.footnote_html': 'Materiales del curso «Trabajo en un aserradero» · Fundación EGIDA.<br>El código se guarda en el navegador durante la sesión.',
      'hdr.eyebrow': 'Fundación EGIDA',
      'hdr.name_html': 'Trabajo <em>en un aserradero</em>',
      'hdr.pin_state': 'Acceso activo',
      'hdr.skip_link': 'Saltar al contenido',
      'lang.label': 'Idioma del contenido',
      'role.nav_label': 'Elige tu rol',
      'role.1': 'Alumno',
      'role.2': 'Formador',
      'role.3': 'Reclutamiento',
      'role.4': 'Sobre el proyecto',
      'role.5': 'Documentos',
      'hero.eyebrow': 'Curso profesional · 12 semanas · 4 idiomas · gratuito',
      'hero.title_html': 'Operador de aserradero <em>en 12 semanas</em>',
      'hero.lead': 'Tres módulos: ayudante → operador junior → operador autónomo con elementos de supervisión. Materiales en polaco, inglés, español y ucraniano: para el alumno, el formador, el reclutador y el coordinador.',
      'kpi.1.l': 'lecciones × 4 idiomas',
      'kpi.1.ctx': 'Tres módulos de 32 lecciones (2h cada una). PL/EN/ES/UK.',
      'kpi.2.l': 'artefactos del formador',
      'kpi.2.ctx': 'Quizzes, ejercicios, dramatizaciones, guías × M1/M2/M3.',
      'kpi.3.l': 'materiales de reclutamiento',
      'kpi.3.ctx': 'Programa general y detallado × 4 idiomas.',
      'kpi.4.l': 'palabras de producción',
      'kpi.4.ctx': 'Fruto del potencial construido en el proyecto SMART + EGIDA.',
      'kpi.5.l': 'tipos de documentos',
      'kpi.5.ctx': 'Paquete B: contratos, certificados, reglamentos, RGPD, formulario de admisión, política de reclamaciones × 4 idiomas × 3 formatos.',
      'sec.1.n': '01 · Para el alumno',
      'sec.1.h': 'Tres módulos de cuatro semanas',
      'sec.1.d': 'Dos formatos: curso HTML interactivo para el autoestudio y presentación Reveal.js para proyectar en el aula.',
      'sec.1.mode1': 'Para autoestudio · 3 módulos · 12 semanas',
      'sec.1.mode2': 'Para proyectar en el aula',
      'sec.2.n': '02 · Para el formador',
      'sec.2.h': 'Artefactos didácticos de la Fase 4',
      'sec.2.d': 'Tabla 3 × 4: filas = módulos (M1/M2/M3), columnas = tipo de artefacto. Dramatizaciones prácticas (A3) y guías para formadores (A4) solo en polaco; quizzes (A1) y ejercicios (A2) en cuatro idiomas.',
      'sec.3.n': '03 · Para reclutamiento',
      'sec.3.h': 'Documentos para candidatos y socios',
      'sec.3.d': 'Programa general y programa detallado (96 lecciones) con descripciones de módulos y objetivos didácticos. Pulsa una tarjeta; la versión lingüística sigue el selector global del header.',
      'sec.4.n': '04 · Sobre el proyecto',
      'sec.4.h': 'Fundamentos de la política local de migración',
      'sec.4.d': 'El curso nació gracias al potencial construido por las Fundaciones SMART y EGIDA en el proyecto «Construcción de fundamentos para una política local de migración e integración» (FEO 2021-2027, Acción 06.03). De ese potencial nacen más cursos, todos gratuitos para personas extranjeras.',
      'sec.5.n': '05 · Documentos del curso',
      'sec.5.h': 'Paquete de documentos formales',
      'sec.5.d': 'Todos los documentos del curso (contrato, certificados, reglamento, RGPD, formulario de admisión, política de reclamaciones, contrato de coorganización) en cuatro idiomas (PL/EN/ES/UK) y tres formatos (HTML para vista en línea, DOCX editable, PDF imprimible).',
      'sec.5.cta': 'Abrir lista de documentos →',
      'tbl.corner': 'Módulo × tipo',
      'pin.fields_label': 'Campo del código PIN de 4 cifras',
      // tarjetas del alumno, módulos interactivos
      'card.kursant.M1.eye': 'Módulo 01 · Ayudante',
      'card.kursant.M1.title': 'PRL, madera, ritmo del día',
      'card.kursant.M1.bullets_html': '<li>PRL y EPI en el aserradero</li><li>especies de madera, herramientas manuales</li><li>puesto, ritmo del turno, comunicación</li>',
      'card.kursant.M1.time': '4 sem. · ~32 h',
      'card.kursant.M1.size': '3,3 MB',
      'card.kursant.M2.eye': 'Módulo 02 · Operador junior',
      'card.kursant.M2.title': 'Sierra de cinta, sierra alternativa vertical',
      'card.kursant.M2.bullets_html': '<li>manejo de la sierra de cinta y de la alternativa</li><li>documentos técnicos, ficha del puesto</li><li>averías, notificación</li>',
      'card.kursant.M2.time': '4 sem. · ~32 h',
      'card.kursant.M2.size': '3,5 MB',
      'card.kursant.M3.eye': 'Módulo 03 · Autónomo',
      'card.kursant.M3.title': 'Coordinación de turno, auditorías',
      'card.kursant.M3.bullets_html': '<li>conducción del turno de 8 h, supervisión de 2-4 M2</li><li>reclamaciones del cliente, Código Civil polaco art. 556-563</li><li>auditorías FSC, ISO 9001</li>',
      'card.kursant.M3.time': '4 sem. · ~32 h',
      'card.kursant.M3.size': '6,5 MB',
      // tarjetas del alumno, presentaciones Reveal.js
      'card.kursant.D1.eye': 'Presentación M1 · Reveal.js',
      'card.kursant.D1.title': 'Diapositivas M1 (Reveal.js)',
      'card.kursant.D1.time': '163 secciones',
      'card.kursant.D1.size': '2,8 MB',
      'card.kursant.D2.eye': 'Presentación M2 · Reveal.js',
      'card.kursant.D2.title': 'Diapositivas M2 (Reveal.js)',
      'card.kursant.D2.time': '163 secciones',
      'card.kursant.D2.size': '2,7 MB',
      'card.kursant.D3.eye': 'Presentación M3 · Reveal.js',
      'card.kursant.D3.title': 'Diapositivas M3 (Reveal.js)',
      'card.kursant.D3.time': '147 secciones',
      'card.kursant.D3.size': '4,4 MB',
      // tabla del formador, nombres de columnas (artefactos)
      'card.trener.col.A1.name': 'Quiz complementario',
      'card.trener.col.A2.name': 'Ejercicios teóricos',
      'card.trener.col.A3.name': 'Dramatizaciones prácticas',
      'card.trener.col.A4.name': 'Guías para formadores',
      // tabla del formador, descripciones de filas (módulos)
      'card.trener.row.M1.desc': 'PRL, madera, ritmo del día',
      'card.trener.row.M2.desc': 'Sierra de cinta, alternativa, averías',
      'card.trener.row.M3.desc': 'Coordinación, reclamaciones, FSC',
      // tarjetas de reclutamiento
      'card.rekrutacja.D1.eye': 'D1 · programa general',
      'card.rekrutacja.D1.title': 'Programa general del curso',
      'card.rekrutacja.D1.desc': 'Documento de una página con tablas de módulos, artefactos y calendario del ciclo 2026/2027.',
      'card.rekrutacja.D1.meta': '1 468 palabras · tablas · solo PL',
      'card.rekrutacja.D2.eye': 'D2 · programa detallado',
      'card.rekrutacja.D2.title': 'Programa detallado de 96 lecciones',
      'card.rekrutacja.D2.desc': 'Cada lección: título, tiempo, objetivo didáctico, 5-8 términos polacos clave.',
      'card.rekrutacja.D2.meta': '~6-7 mil palabras',
      // tarjeta del proyecto
      'card.projekt.eye': 'proyecto · SMART + EGIDA · Opole',
      'card.projekt.title': 'Construcción de fundamentos para una política local de migración e integración',
      'card.projekt.desc': 'Asociación de la Fundación SMART (líder) y EGIDA. Objetivo: ampliar la capacidad de ambas organizaciones para poner en marcha en Opole un centro de integración de personas extranjeras en modelo one-stop-shop. Presupuesto 500 000 PLN, cofinanciación de 475 000 PLN del FSE+ y del presupuesto del Estado. Solicitud FEOP.06.03-IZ.00-0006/25.',
      'card.dokumenty.eye': 'Paquete B · 13 tipos × 4 idiomas × 3 formatos',
      'card.dokumenty.title': 'Abrir lista de documentos del curso',
      'card.dokumenty.desc': 'Contrato del curso, certificados de asistencia y finalización de Módulos y del Curso completo, certificados de prácticas de graduado, reglamento del Curso, cláusula informativa RGPD y consentimientos, formulario de admisión, política de reclamaciones y apelaciones, contrato de coorganización.',
      // pie de página
      'footer.logos_label': 'Socios y financiación del proyecto',
      'footer.disclaimer_html': 'La <b>Fundación SMART para la educación</b> (líder), en asociación con la <b>Fundación de asistencia jurídica EGIDA</b>, ejecuta el proyecto «Construcción de fundamentos para una política local de migración e integración» (solicitud FEOP.06.03-IZ.00-0006/25, <b>FEO 2021-2027, Acción 06.03: Construcción de la capacidad de los interlocutores sociales y de las organizaciones de la sociedad civil</b>, cofinanciación de 475 000 PLN del FSE+ y del presupuesto del Estado). El objetivo del proyecto es ampliar la capacidad de ambas organizaciones para poner en marcha en Opole un centro local de integración de personas extranjeras en modelo one-stop-shop. El curso «Trabajo en un aserradero» nació como fruto de las competencias y los recursos construidos en el marco de este proyecto.'
    },
    uk: {
      'pin.eyebrow': 'Доступ PIN',
      'pin.title_html': 'Курс лісопилки<br><em>Фонд EGIDA</em>',
      'pin.lead': 'Матеріали курсу захищені PIN-кодом. Введіть 4-значний код, отриманий від координатора курсу.',
      'pin.footnote_html': 'Матеріали курсу «Робота на лісопилці» · Фонд EGIDA.<br>Код зберігається у браузері до кінця сесії.',
      'hdr.eyebrow': 'Фонд EGIDA',
      'hdr.name_html': 'Робота <em>на лісопилці</em>',
      'hdr.pin_state': 'Доступ активний',
      'hdr.skip_link': 'Перейти до змісту',
      'lang.label': 'Мова змісту',
      'role.nav_label': 'Обери свою роль',
      'role.1': 'Курсант',
      'role.2': 'Тренер',
      'role.3': 'Рекрутація',
      'role.4': 'Про проєкт',
      'role.5': 'Документи',
      'hero.eyebrow': 'Професійний курс · 12 тижнів · 4 мови · безкоштовно',
      'hero.title_html': 'Професія оператора лісопилки <em>за 12 тижнів</em>',
      'hero.lead': 'Три модулі: помічник → молодший оператор → самостійний оператор з елементами нагляду. Матеріали польською, англійською, іспанською та українською: для курсанта, тренера, рекрутера й координатора.',
      'kpi.1.l': 'уроків × 4 мови',
      'kpi.1.ctx': 'Три модулі по 32 уроки (по 2 год). PL/EN/ES/UK.',
      'kpi.2.l': 'артефактів тренера',
      'kpi.2.ctx': 'Тести, вправи, сценарії, настанови × M1/M2/M3.',
      'kpi.3.l': 'матеріалів рекрутації',
      'kpi.3.ctx': 'Загальна та детальна програма × 4 мови.',
      'kpi.4.l': 'виробничих слів',
      'kpi.4.ctx': 'Результат потенціалу, побудованого у проєкті SMART + EGIDA.',
      'kpi.5.l': 'типів документів',
      'kpi.5.ctx': 'Пакет Б: договори, свідоцтва, регламенти, GDPR, анкета кандидата, політика розгляду скарг × 4 мови × 3 формати.',
      'sec.1.n': '01 · Для курсанта',
      'sec.1.h': 'Три модулі по чотири тижні',
      'sec.1.d': 'Два формати: інтерактивний курс HTML для самостійного вивчення та презентація Reveal.js для проєкції в навчальному класі.',
      'sec.1.mode1': 'Для самостійного вивчення · 3 модулі · 12 тижнів',
      'sec.1.mode2': 'Для проєкції в класі',
      'sec.2.n': '02 · Для тренера',
      'sec.2.h': 'Дидактичні артефакти Фази 4',
      'sec.2.d': 'Таблиця 3 × 4: рядки = модулі (M1/M2/M3), стовпці = тип артефакту. Практичні сценарії (A3) та настанови для тренера (A4) тільки польською; тести (A1) і вправи (A2) чотирма мовами.',
      'sec.3.n': '03 · Для рекрутації',
      'sec.3.h': 'Документи для кандидатів і партнерів',
      'sec.3.d': 'Загальна та детальна програма (96 уроків) з описами модулів і дидактичними цілями. Натисни картку; мовна версія йде за глобальним перемикачем у заголовку.',
      'sec.4.n': '04 · Про проєкт',
      'sec.4.h': 'Фундаменти локальної міграційної політики',
      'sec.4.d': 'Курс виріс з потенціалу, побудованого Фондами SMART і EGIDA у проєкті «Побудова фундаментів локальної міграційної та інтеграційної політики» (FEO 2021-2027, Дія 06.03). З цього потенціалу постають подальші курси, усі безкоштовні для іноземців.',
      'sec.5.n': '05 · Документи курсу',
      'sec.5.h': 'Пакет формальних документів',
      'sec.5.d': 'Усі документи курсу (договір, свідоцтва, регламент, GDPR, анкета кандидата, політика розгляду скарг, договір співорганізації) у чотирьох мовах (PL/EN/ES/UK) і трьох форматах (HTML для онлайн-перегляду, DOCX для редагування, PDF для друку).',
      'sec.5.cta': 'Відкрити список документів →',
      'tbl.corner': 'Модуль × тип',
      'pin.fields_label': 'Поле 4-значного PIN-коду',
      // картки курсанта, інтерактивні модулі
      'card.kursant.M1.eye': 'Модуль 01 · Помічник',
      'card.kursant.M1.title': 'ОП, деревина, ритм дня',
      'card.kursant.M1.bullets_html': '<li>охорона праці та ЗІЗ на лісопилці</li><li>породи деревини, ручні інструменти</li><li>робоче місце, ритм зміни, комунікація</li>',
      'card.kursant.M1.time': '4 тиж. · ~32 год',
      'card.kursant.M1.size': '3,3 МБ',
      'card.kursant.M2.eye': 'Модуль 02 · Молодший оператор',
      'card.kursant.M2.title': 'Стрічкова пилка, вертикальна пилорама',
      'card.kursant.M2.bullets_html': '<li>робота зі стрічковою пилкою та пилорамою</li><li>технічна документація, картка робочого місця</li><li>несправності, звітування</li>',
      'card.kursant.M2.time': '4 тиж. · ~32 год',
      'card.kursant.M2.size': '3,5 МБ',
      'card.kursant.M3.eye': 'Модуль 03 · Самостійний',
      'card.kursant.M3.title': 'Координація зміни, аудити',
      'card.kursant.M3.bullets_html': '<li>ведення зміни 8 год, нагляд за 2-4 М2</li><li>рекламації клієнтів, ст. 556-563 ЦК Польщі</li><li>аудити FSC, ISO 9001</li>',
      'card.kursant.M3.time': '4 тиж. · ~32 год',
      'card.kursant.M3.size': '6,5 МБ',
      // картки курсанта, презентації Reveal.js
      'card.kursant.D1.eye': 'Презентація M1 · Reveal.js',
      'card.kursant.D1.title': 'Слайди M1 (Reveal.js)',
      'card.kursant.D1.time': '163 секцій',
      'card.kursant.D1.size': '2,8 МБ',
      'card.kursant.D2.eye': 'Презентація M2 · Reveal.js',
      'card.kursant.D2.title': 'Слайди M2 (Reveal.js)',
      'card.kursant.D2.time': '163 секцій',
      'card.kursant.D2.size': '2,7 МБ',
      'card.kursant.D3.eye': 'Презентація M3 · Reveal.js',
      'card.kursant.D3.title': 'Слайди M3 (Reveal.js)',
      'card.kursant.D3.time': '147 секцій',
      'card.kursant.D3.size': '4,4 МБ',
      // таблиця тренера, назви стовпців (артефакти)
      'card.trener.col.A1.name': 'Додатковий тест',
      'card.trener.col.A2.name': 'Теоретичні вправи',
      'card.trener.col.A3.name': 'Практичні сценарії',
      'card.trener.col.A4.name': 'Настанови для тренера',
      // таблиця тренера, описи рядків (модулі)
      'card.trener.row.M1.desc': 'ОП, деревина, ритм дня',
      'card.trener.row.M2.desc': 'Пилка, пилорама, несправності',
      'card.trener.row.M3.desc': 'Координація, рекламації, FSC',
      // картки рекрутації
      'card.rekrutacja.D1.eye': 'D1 · загальна програма',
      'card.rekrutacja.D1.title': 'Загальна програма курсу',
      'card.rekrutacja.D1.desc': 'Односторінковий документ із таблицями модулів, артефактів і графіка циклу 2026/2027.',
      'card.rekrutacja.D1.meta': '1 468 слів · таблиці · тільки PL',
      'card.rekrutacja.D2.eye': 'D2 · детальна програма',
      'card.rekrutacja.D2.title': 'Детальна програма 96 уроків',
      'card.rekrutacja.D2.desc': 'Кожен урок: назва, час, дидактична мета, 5-8 ключових польських термінів.',
      'card.rekrutacja.D2.meta': '~6-7 тис. слів',
      // картка проєкту
      'card.projekt.eye': 'проєкт · SMART + EGIDA · Ополе',
      'card.projekt.title': 'Побудова фундаментів локальної міграційної та інтеграційної політики',
      'card.projekt.desc': 'Партнерство Фонду SMART (лідер) і EGIDA. Мета: розширення потенціалу обох організацій для запуску в Ополі осередку інтеграції іноземців у моделі one-stop-shop. Бюджет 500 000 злотих, співфінансування 475 000 злотих з ESF+ та державного бюджету. Заявка FEOP.06.03-IZ.00-0006/25.',
      'card.dokumenty.eye': 'Пакет Б · 13 типів × 4 мови × 3 формати',
      'card.dokumenty.title': 'Відкрити список документів курсу',
      'card.dokumenty.desc': 'Договір курсу, свідоцтва про відвідування та завершення Модулів і всього Курсу, свідоцтва випускницької практики, регламент Курсу, інформаційна клаузула GDPR та згоди, анкета кандидата, політика розгляду скарг та апеляцій, договір співорганізації.',
      // підвал
      'footer.logos_label': 'Партнери та фінансування проєкту',
      'footer.disclaimer_html': '<b>Фонд освіти SMART</b> (лідер) у партнерстві з <b>Фондом правової допомоги EGIDA</b> реалізує проєкт «Побудова фундаментів локальної міграційної та інтеграційної політики» (заявка FEOP.06.03-IZ.00-0006/25, <b>FEO 2021-2027, Дія 06.03: Розбудова потенціалу соціальних партнерів та організацій громадянського суспільства</b>, співфінансування 475 000 злотих з ESF+ та державного бюджету). Мета проєкту: розширення потенціалу обох організацій для запуску в Ополі локального осередку інтеграції іноземців у моделі one-stop-shop. Курс «Робота на лісопилці» постав як плід компетенцій та ресурсів, побудованих у межах цього проєкту.'
    }
  };

  function applyI18n(lang) {
    var dict = I18N[lang] || I18N.pl;
    document.querySelectorAll('[data-i18n]').forEach(function(el) {
      var key = el.dataset.i18n;
      if (!dict[key]) return;
      if (key.endsWith('_html')) el.innerHTML = dict[key];
      else el.textContent = dict[key];
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function(el) {
      // data-i18n-attr="aria-label:key,title:key2"
      var pairs = el.dataset.i18nAttr.split(',');
      pairs.forEach(function(p) {
        var parts = p.split(':');
        if (parts.length === 2 && dict[parts[1]]) {
          el.setAttribute(parts[0].trim(), dict[parts[1].trim()]);
        }
      });
    });
  }

  // ============================================================
  // PIN GATE, 4 pola input, auto-advance, localStorage persystencja
  // ============================================================
  function initPinGate(root) {
    if (!root) return;
    var fields = root.querySelectorAll('.pin-fields input');
    var msg = root.querySelector('.pin-msg');
    var attempts = 0;

    // auto-focus pierwszego pola
    setTimeout(function () { fields[0] && fields[0].focus(); }, 10);

    fields.forEach(function (input, idx) {
      input.addEventListener('input', function (e) {
        var v = (e.target.value || '').replace(/\D/g, '').slice(0, 1);
        e.target.value = v;
        if (v && idx < fields.length - 1) {
          fields[idx + 1].focus();
        }
        checkComplete();
      });
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !e.target.value && idx > 0) {
          fields[idx - 1].focus();
          fields[idx - 1].value = '';
          e.preventDefault();
        }
        if (e.key === 'ArrowLeft' && idx > 0) fields[idx - 1].focus();
        if (e.key === 'ArrowRight' && idx < fields.length - 1) fields[idx + 1].focus();
      });
      input.addEventListener('paste', function (e) {
        e.preventDefault();
        var data = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '').slice(0, 4);
        for (var i = 0; i < data.length && i < fields.length; i++) {
          fields[i].value = data[i];
        }
        (fields[data.length] || fields[fields.length - 1]).focus();
        checkComplete();
      });
    });

    function checkComplete() {
      var val = Array.prototype.map.call(fields, function (f) { return f.value; }).join('');
      if (val.length !== 4) return;
      if (val === PIN_CORRECT) {
        try { localStorage.setItem(LS_PIN, '1'); } catch (e) {}
        unlock();
      } else {
        attempts++;
        fields.forEach(function (f) { f.classList.add('error'); });
        if (msg) { msg.classList.add('err'); msg.textContent = 'Nieprawidłowy kod. Pozostało prób: ' + (MAX_ATTEMPTS - attempts); }
        if (attempts >= MAX_ATTEMPTS) {
          fields.forEach(function (f) { f.disabled = true; });
          if (msg) msg.textContent = 'Przekroczono liczbę prób. Odśwież stronę.';
        } else {
          setTimeout(function () {
            fields.forEach(function (f) { f.value = ''; f.classList.remove('error'); });
            if (msg) { msg.classList.remove('err'); msg.textContent = ''; }
            fields[0].focus();
          }, 1200);
        }
      }
    }
  }

  function unlock() {
    var screen = document.getElementById('pin-screen');
    if (screen) screen.remove();
    document.body.classList.remove('hub-locked');
    window.dispatchEvent(new CustomEvent('egida:unlocked'));
  }

  function isUnlocked() {
    try { return localStorage.getItem(LS_PIN) === '1'; } catch (e) { return false; }
  }

  // ============================================================
  // LANG SWITCH, globalny, localStorage, rewrite linkow data-href-*
  // ============================================================
  function getLang() {
    try {
      var saved = localStorage.getItem(LS_LANG);
      if (saved && SUPPORTED_LANGS.indexOf(saved) >= 0) return saved;
    } catch (e) {}
    // browser preferred
    var nav = (navigator.language || 'pl').toLowerCase().split('-')[0];
    if (SUPPORTED_LANGS.indexOf(nav) >= 0) return nav;
    return 'pl';
  }

  function setLang(lang) {
    if (SUPPORTED_LANGS.indexOf(lang) < 0) return;
    try { localStorage.setItem(LS_LANG, lang); } catch (e) {}
    applyLang(lang);
    showLangToast(lang);
    window.dispatchEvent(new CustomEvent('egida:lang-changed', { detail: { lang: lang } }));
  }

  function showLangToast(lang) {
    var names = { pl: 'Polski', en: 'English', es: 'Español', uk: 'Українська' };
    var msgs = {
      pl: 'Wybrano język: ' + names[lang] + '. Dokument zmieni się po kliknięciu karty.',
      en: 'Language selected: ' + names[lang] + '. The document will switch when you click a tile.',
      es: 'Idioma elegido: ' + names[lang] + '. El documento cambiará al hacer clic en la tarjeta.',
      uk: 'Обрано мову: ' + names[lang] + '. Документ зміниться після натискання картки.'
    };
    var msg = msgs[lang] || msgs.pl;
    var old = document.getElementById('egida-lang-toast');
    if (old) old.remove();
    var t = document.createElement('div');
    t.id = 'egida-lang-toast';
    t.setAttribute('role', 'status');
    t.setAttribute('aria-live', 'polite');
    t.textContent = msg;
    t.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%) translateY(-20px);' +
      'background:rgba(28,27,23,0.96);color:#fbfaf6;padding:12px 22px;border-radius:3px;' +
      'border:1px solid rgba(122,59,26,0.5);font-family:Inter,system-ui,sans-serif;font-size:14px;' +
      'box-shadow:0 4px 20px rgba(28,27,23,0.28);z-index:10000;opacity:0;' +
      'transition:opacity 0.2s, transform 0.2s;max-width:calc(100vw - 40px);text-align:center';
    document.body.appendChild(t);
    requestAnimationFrame(function() {
      t.style.opacity = '1';
      t.style.transform = 'translateX(-50%) translateY(0)';
    });
    setTimeout(function() {
      t.style.opacity = '0';
      t.style.transform = 'translateX(-50%) translateY(-20px)';
      setTimeout(function() { t.remove(); }, 220);
    }, 3400);
  }

  function applyLang(lang) {
    // 1) aktywny button w lang-switch
    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      b.classList.toggle('on', b.dataset.lang === lang);
      b.setAttribute('aria-pressed', b.dataset.lang === lang ? 'true' : 'false');
    });
    // 2) rewrite linkow z data-href-*
    document.querySelectorAll('[data-href-pl], [data-href-en], [data-href-es], [data-href-uk]').forEach(function (a) {
      var href = a.dataset['href' + lang.charAt(0).toUpperCase() + lang.slice(1)];
      if (!href) {
        // fallback: jesli brak jezyka - uzyj PL
        href = a.dataset.hrefPl;
      }
      if (href) {
        a.href = href;
        // aktualizuj aria-label na podstawie lang
        var baseLabel = a.dataset.labelBase || a.textContent.trim();
        a.dataset.labelBase = baseLabel;
        a.setAttribute('aria-label', baseLabel + ', wersja ' + langName(lang));
        a.setAttribute('hreflang', lang);
      }
    });
    // 3) html lang hint
    document.documentElement.lang = lang;
    // 4) i18n UI strings
    applyI18n(lang);
    // 5) re-render module progress with translated labels
    if (typeof renderModuleProgress === 'function') renderModuleProgress();
  }

  function langName(code) {
    return { pl: 'polska', en: 'angielska', es: 'hiszpańska', uk: 'ukraińska' }[code] || code;
  }

  function initLangSwitch() {
    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      b.addEventListener('click', function () { setLang(b.dataset.lang); });
    });
    // doc-lang-switch (na podstronach): zapisz wybor zanim przejdziesz do innej wersji
    document.querySelectorAll('.doc-lang-switch a[data-lang]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var lang = a.dataset.lang;
        try { localStorage.setItem(LS_LANG, lang); } catch (ex) {}
        // Jesli link prowadzi do # (current page), nie nawiguj, tylko pokaz toast
        if (a.getAttribute('href') === '#') {
          e.preventDefault();
          showLangToast(lang);
        }
      });
    });
    applyLang(getLang());
  }

  // ============================================================
  // ROLE NAV, IntersectionObserver podswietlajacy aktualna sekcje
  // ============================================================
  function initRoleNav() {
    var links = document.querySelectorAll('.role-nav a[href^="#"]');
    if (!links.length) return;
    var map = {};
    links.forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      map[id] = a;
      a.addEventListener('click', function (e) {
        // smooth scroll + active state
        var tgt = document.getElementById(id);
        if (tgt) {
          e.preventDefault();
          tgt.scrollIntoView({ behavior: 'smooth', block: 'start' });
          history.replaceState(null, '', '#' + id);
        }
      });
    });

    if ('IntersectionObserver' in window) {
      var headerH = 140; // sticky header + role-nav
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            Object.values(map).forEach(function (a) { a.classList.remove('active'); a.removeAttribute('aria-current'); });
            if (map[e.target.id]) {
              map[e.target.id].classList.add('active');
              map[e.target.id].setAttribute('aria-current', 'location');
            }
          }
        });
      }, { rootMargin: '-' + headerH + 'px 0px -50% 0px', threshold: 0 });

      Object.keys(map).forEach(function (id) {
        var el = document.getElementById(id);
        if (el) obs.observe(el);
      });
    }
  }

  // ============================================================
  // BOOT
  // ============================================================
  // initToc, spis tresci dla dlugich podstron (>=4 naglowki h2/h3)
  // Desktop >=1180px: sticky right column w grid layout doc-wrap
  // Mobile <1180px: FAB w prawym dolnym rogu + drawer
  // ============================================================
  var TOC_CSS = [
    '@media (min-width: 1180px) {',
    '  .doc-wrap.with-toc {',
    '    max-width: 1200px;',
    '    display: grid;',
    '    grid-template-columns: minmax(0, 1fr) 240px;',
    '    column-gap: 2.4rem;',
    '    align-items: start;',
    '  }',
    '  .doc-wrap.with-toc .doc-header,',
    '  .doc-wrap.with-toc .doc-footer { grid-column: 1 / -1; }',
    '  .doc-wrap.with-toc .doc-content { grid-column: 1; min-width: 0; }',
    '  .toc {',
    '    grid-column: 2;',
    '    position: sticky;',
    '    top: 1.5rem;',
    '    max-height: calc(100vh - 3rem);',
    '    overflow-y: auto;',
    '    padding: 1rem 1.1rem 1rem 0.4rem;',
    '    border-left: 1px solid rgba(28, 27, 23, 0.12);',
    '    font-family: \'Inter\', -apple-system, system-ui, sans-serif;',
    '    font-size: 13px;',
    '    line-height: 1.5;',
    '  }',
    '  .toc__title {',
    '    font-size: 11px;',
    '    text-transform: uppercase;',
    '    letter-spacing: 0.08em;',
    '    color: rgba(28, 27, 23, 0.55);',
    '    margin: 0 0 0.6rem 0.8rem;',
    '    font-weight: 600;',
    '  }',
    '  .toc__list { list-style: none; margin: 0; padding: 0; }',
    '  .toc__list li { margin: 0; }',
    '  .toc__list a {',
    '    display: block;',
    '    padding: 0.3rem 0 0.3rem 0.8rem;',
    '    color: rgba(28, 27, 23, 0.7);',
    '    text-decoration: none;',
    '    border-left: 2px solid transparent;',
    '    margin-left: -1px;',
    '    transition: color 0.12s, border-color 0.12s;',
    '  }',
    '  .toc__list a:hover { color: #7a3b1a; }',
    '  .toc__list a.active {',
    '    color: #1c1b17;',
    '    border-left-color: #7a3b1a;',
    '    font-weight: 500;',
    '  }',
    '  .toc__list .toc-h3 a { padding-left: 1.6rem; font-size: 12px; }',
    '  .toc-fab, .toc-drawer { display: none !important; }',
    '}',
    '@media (max-width: 1179px) {',
    '  .toc { display: none; }',
    '  .toc-fab {',
    '    position: fixed;',
    '    bottom: 1.4rem;',
    '    right: 1.4rem;',
    '    z-index: 99998;',
    '    width: 48px; height: 48px;',
    '    border: 0; border-radius: 50%;',
    '    background: #1c1b17; color: #fbfaf6;',
    '    font-size: 20px; cursor: pointer;',
    '    box-shadow: 0 2px 12px rgba(0,0,0,0.18);',
    '    display: flex; align-items: center; justify-content: center;',
    '    font-family: \'Inter\', system-ui, sans-serif;',
    '  }',
    '  .toc-fab:hover, .toc-fab:focus-visible { background: #7a3b1a; outline: 2px solid #fbfaf6; outline-offset: 2px; }',
    '  .toc-drawer {',
    '    position: fixed;',
    '    inset: 0;',
    '    z-index: 99997;',
    '    background: rgba(28, 27, 23, 0.55);',
    '    display: none;',
    '    align-items: flex-end;',
    '  }',
    '  .toc-drawer.open { display: flex; }',
    '  .toc-drawer__panel {',
    '    background: #fbfaf6;',
    '    width: 100%;',
    '    max-height: 70vh;',
    '    overflow-y: auto;',
    '    padding: 1.4rem 1.4rem 2rem;',
    '    border-radius: 12px 12px 0 0;',
    '    font-family: \'Inter\', system-ui, sans-serif;',
    '  }',
    '  .toc-drawer__title {',
    '    font-size: 12px;',
    '    text-transform: uppercase;',
    '    letter-spacing: 0.08em;',
    '    color: rgba(28, 27, 23, 0.55);',
    '    margin: 0 0 0.8rem;',
    '    font-weight: 600;',
    '  }',
    '  .toc-drawer__list { list-style: none; margin: 0; padding: 0; }',
    '  .toc-drawer__list li { margin: 0; }',
    '  .toc-drawer__list a {',
    '    display: block;',
    '    padding: 0.7rem 0;',
    '    color: #1c1b17;',
    '    text-decoration: none;',
    '    border-bottom: 1px solid rgba(28, 27, 23, 0.08);',
    '    font-size: 15px;',
    '  }',
    '  .toc-drawer__list .toc-h3 a {',
    '    padding-left: 1.2rem;',
    '    font-size: 14px;',
    '    color: rgba(28, 27, 23, 0.75);',
    '  }',
    '}',
    'html { scroll-behavior: smooth; }',
    '.doc-content :is(h2, h3)[id] { scroll-margin-top: 1rem; }'
  ].join('\n');

  var TOC_LABELS = {
    pl: 'Spis treści',
    en: 'Table of contents',
    es: 'Tabla de contenidos',
    uk: 'Зміст'
  };

  function escTocHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function initToc() {
    var docContent = document.querySelector('main.doc-content');
    if (!docContent) return;
    var headings = docContent.querySelectorAll('h2, h3');
    if (headings.length < 4) return;

    // czyta oryginalny lang z atrybutu HTML zachowanego przez initLangSwitch
    // (initLangSwitch nadpisuje document.documentElement.lang globalnym z LS,
    //  ale zachowuje pageLang dla podstron multi-lang)
    var lang = (window.__egidaPageLang || document.documentElement.lang || 'pl').toLowerCase();
    var label = TOC_LABELS[lang] || TOC_LABELS.pl;

    // generate ids + collect items
    var items = [];
    var h2Index = 0, h3Index = 0;
    for (var i = 0; i < headings.length; i++) {
      var h = headings[i];
      var tag = h.tagName.toLowerCase();
      if (tag === 'h2') { h2Index++; h3Index = 0; }
      else { h3Index++; }
      if (!h.id) {
        h.id = tag === 'h2' ? 'toc-h2-' + h2Index : 'toc-h3-' + h2Index + '-' + h3Index;
      }
      items.push({ tag: tag, id: h.id, text: h.textContent.trim() });
    }

    // inject style
    if (!document.getElementById('egida-toc-style')) {
      var style = document.createElement('style');
      style.id = 'egida-toc-style';
      style.textContent = TOC_CSS;
      document.head.appendChild(style);
    }

    function buildListHtml(itemClass) {
      var html = '';
      for (var i = 0; i < items.length; i++) {
        var it = items[i];
        html += '<li class="toc-' + it.tag + '"><a href="#' + it.id + '">' + escTocHtml(it.text) + '</a></li>';
      }
      return html;
    }

    // desktop sidebar
    var aside = document.createElement('aside');
    aside.className = 'toc';
    aside.setAttribute('aria-label', label);
    aside.innerHTML = '<p class="toc__title">' + escTocHtml(label) + '</p><ol class="toc__list">' + buildListHtml() + '</ol>';

    var docWrap = document.querySelector('.doc-wrap');
    if (!docWrap) return;
    docWrap.classList.add('with-toc');
    var footer = docWrap.querySelector('.doc-footer');
    if (footer) docWrap.insertBefore(aside, footer);
    else docWrap.appendChild(aside);

    // mobile FAB + drawer
    var fab = document.createElement('button');
    fab.className = 'toc-fab';
    fab.type = 'button';
    fab.setAttribute('aria-label', label);
    fab.innerHTML = '&#9776;'; // ☰
    document.body.appendChild(fab);

    var drawer = document.createElement('div');
    drawer.className = 'toc-drawer';
    drawer.setAttribute('role', 'dialog');
    drawer.setAttribute('aria-label', label);
    drawer.innerHTML = '<div class="toc-drawer__panel"><p class="toc-drawer__title">' + escTocHtml(label) + '</p><ol class="toc-drawer__list">' + buildListHtml() + '</ol></div>';
    document.body.appendChild(drawer);

    fab.addEventListener('click', function () { drawer.classList.add('open'); });
    drawer.addEventListener('click', function (e) {
      if (e.target === drawer || (e.target.tagName === 'A')) {
        drawer.classList.remove('open');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('open')) drawer.classList.remove('open');
    });

    // scroll-spy
    var byId = {};
    aside.querySelectorAll('a').forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      (byId[id] = byId[id] || []).push(a);
    });
    drawer.querySelectorAll('a').forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      (byId[id] = byId[id] || []).push(a);
    });

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.id;
          Object.keys(byId).forEach(function (k) {
            byId[k].forEach(function (a) { a.classList.remove('active'); });
          });
          if (byId[id]) byId[id].forEach(function (a) { a.classList.add('active'); });
        });
      }, { rootMargin: '-10% 0px -70% 0px' });
      headings.forEach(function (h) { observer.observe(h); });
    }
  }

  // ============================================================
  // MODULE PROGRESS: paski w kafelkach Kursanta (M1/M2/M3)
  // Schema LS klucza: 'egida-progress:M1' = JSON {"completed": N, "total": M}
  // Brak klucza = "Nie rozpoczęto". Generator standalone kursu może updateować klucz
  // emitując event po zaliczeniu lekcji/quizu (placeholder, dorobi się w P3.13 pełnym).
  // ============================================================
  var PROGRESS_LABELS = {
    pl: { notStarted: 'Nie rozpoczęto', inProgress: '{c} z {t} lekcji', done: 'Moduł ukończony' },
    en: { notStarted: 'Not started',    inProgress: '{c} of {t} lessons', done: 'Module completed' },
    es: { notStarted: 'No iniciado',    inProgress: '{c} de {t} lecciones', done: 'Módulo completado' },
    uk: { notStarted: 'Не розпочато',   inProgress: '{c} з {t} уроків',   done: 'Модуль завершено' }
  };

  function renderModuleProgress() {
    var lang = (typeof getLang === 'function' ? getLang() : 'pl');
    var labels = PROGRESS_LABELS[lang] || PROGRESS_LABELS.pl;
    document.querySelectorAll('[data-progress-module]').forEach(function (el) {
      var moduleKey = el.dataset.progressModule;
      var pct = 0;
      var state = 'not-started';
      var text = labels.notStarted;
      try {
        var raw = localStorage.getItem('egida-progress:' + moduleKey);
        if (raw) {
          var data = JSON.parse(raw);
          var c = parseInt(data.completed, 10) || 0;
          var t = parseInt(data.total, 10) || 0;
          if (t > 0 && c > 0) {
            pct = Math.min(100, Math.round((c / t) * 100));
            if (c >= t) {
              state = 'done';
              text = labels.done;
            } else {
              state = 'in-progress';
              text = labels.inProgress.replace('{c}', c).replace('{t}', t);
            }
          }
        }
      } catch (e) { /* malformed JSON, treat as not started */ }
      el.dataset.state = state;
      el.innerHTML = '<div class="mp-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pct + '"><div class="mp-fill" style="width:' + pct + '%"></div></div><span class="mp-text">' + text + '</span>';
    });
  }

  // ============================================================
  function boot() {
    var onIndex = !!document.getElementById('pin-screen');
    // zapisz oryginalny lang strony PRZED tym jak initLangSwitch go nadpisze
    // (chrome.js synchronizuje document.documentElement.lang z globalnym LS,
    //  ale dla initToc potrzebny jest lang konkretnej podstrony)
    window.__egidaPageLang = document.documentElement.lang || 'pl';

    if (onIndex) {
      if (isUnlocked()) {
        unlock();
      } else {
        document.body.classList.add('hub-locked');
        initPinGate(document.getElementById('pin-screen'));
      }
    } else {
      // podstrona, jesli PIN nie wpisany, redirect do hubu
      if (!isUnlocked()) {
        var depth = (location.pathname.match(/\/kurs-tartak\/(.+)/) || ['', ''])[1].split('/').filter(Boolean).length;
        var back = '';
        for (var i = 0; i < depth; i++) back += '../';
        back += 'index.html';
        location.replace(back);
        return;
      }
    }

    initLangSwitch();
    initRoleNav();
    initToc();
    renderModuleProgress();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
