/* ============================================================
   EGIDA - Kurs prac ogólnobudowlanych : chrome.js
   PIN gate (6 cyfr, SHA-256) + lang switch PL/EN/ES + i18n hubu
   ============================================================ */
(function () {
  'use strict';

  var LS_PIN = 'egida-bud-pin';
  var LS_LANG = 'egida-bud-lang';
  var SUPPORTED = ['pl', 'en', 'es'];
  var PIN_LEN = 6;
  // SHA-256 PIN-u (684133). Plaintext nie wystepuje w kodzie.
  var PIN_HASH = 'ec3f369d7a75504a5a1b70c1e3fbf58e6552fe636493610e9c75bc7b1f7beb00';
  var MAX_ATTEMPTS = 6;

  // ---------- compact SHA-256 (dziala na file://, http, https) ----------
  // Stale K i H zapisane na sztywno (zweryfikowane wektorem NIST "abc").
  function sha256(ascii) {
    function rr(n, x) { return (x >>> n) | (x << (32 - n)); }
    var K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    var H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    var bytes = [], i, cc;
    for (i = 0; i < ascii.length; i++) {
      cc = ascii.charCodeAt(i);
      if (cc < 128) bytes.push(cc);
      else if (cc < 2048) bytes.push(192|(cc>>6),128|(cc&63));
      else bytes.push(224|(cc>>12),128|((cc>>6)&63),128|(cc&63));
    }
    var l = bytes.length; bytes.push(0x80);
    while (bytes.length % 64 !== 56) bytes.push(0);
    var bitLen = l * 8;
    for (i = 7; i >= 0; i--) bytes.push((Math.floor(bitLen / Math.pow(2, i*8))) & 0xff);
    var w = new Int32Array(64);
    for (var off = 0; off < bytes.length; off += 64) {
      for (i = 0; i < 16; i++) w[i] = (bytes[off+i*4]<<24)|(bytes[off+i*4+1]<<16)|(bytes[off+i*4+2]<<8)|(bytes[off+i*4+3]);
      for (i = 16; i < 64; i++) {
        var s0 = rr(7,w[i-15])^rr(18,w[i-15])^(w[i-15]>>>3);
        var s1 = rr(17,w[i-2])^rr(19,w[i-2])^(w[i-2]>>>10);
        w[i] = (w[i-16]+s0+w[i-7]+s1)|0;
      }
      var a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
      for (i = 0; i < 64; i++) {
        var S1=rr(6,e)^rr(11,e)^rr(25,e), ch=(e&f)^(~e&g), t1=(h+S1+ch+K[i]+w[i])|0;
        var S0=rr(2,a)^rr(13,a)^rr(22,a), maj=(a&b)^(a&c)^(b&c), t2=(S0+maj)|0;
        h=g;g=f;f=e;e=(d+t1)|0;d=c;c=b;b=a;a=(t1+t2)|0;
      }
      H[0]=(H[0]+a)|0;H[1]=(H[1]+b)|0;H[2]=(H[2]+c)|0;H[3]=(H[3]+d)|0;H[4]=(H[4]+e)|0;H[5]=(H[5]+f)|0;H[6]=(H[6]+g)|0;H[7]=(H[7]+h)|0;
    }
    var r=''; for (i=0;i<8;i++){var hx=(H[i]>>>0).toString(16); r+='00000000'.slice(hx.length)+hx;}
    return r;
  }

  // ============================================================
  // I18N hubu (PL/EN/ES)
  // ============================================================
  var I18N = {
    pl: {
      'pin.eyebrow': 'Dostęp PIN',
      'pin.title_html': 'Kurs prac ogólnobudowlanych<br><em>Fundacja EGIDA</em>',
      'pin.lead': 'Materiały kursu są chronione kodem PIN. Wprowadź 6-cyfrowy kod otrzymany od organizatora.',
      'pin.footnote_html': 'Kurs „Przygotowanie zawodowe do prac ogólnobudowlanych" - Fundacja EGIDA.<br>Kod jest zapamiętywany w przeglądarce do końca sesji.',
      'hdr.eyebrow': 'Fundacja EGIDA - kurs zawodowy',
      'hdr.name_html': 'Prace <em>ogólnobudowlane</em>',
      'hdr.skip': 'Przejdź do treści',
      'hdr.pin_state': 'Dostęp aktywny',
      'lang.label': 'Język',
      'hero.eyebrow': 'Kurs zawodowy - 4 tygodnie - na czynnej budowie - bezpłatnie',
      'hero.title_html': 'Przygotowanie zawodowe do <em>prac ogólnobudowlanych</em>',
      'hero.sub': 'ze specjalizacją: układanie kostki brukowej',
      'hero.lead': 'Kurs dla cudzoziemców przybyłych do Polski. Cztery tygodnie nauki na terenie prawdziwej budowy: teoria, obserwacja realnego wykonania i ćwiczenia pod nadzorem. Silny nacisk na bezpieczeństwo i higienę pracy (BHP). Po ukończeniu - szansa zatrudnienia na tej samej budowie.',
      'fact.weeks': '<b>4 tygodnie</b> - 20 dni - ok. 140 h',
      'fact.site': '<b>Na czynnej budowie</b> - teoria + praktyka',
      'fact.langs': '<b>3 języki</b> - PL / EN / ES',
      'fact.bhp': '<b>BHP</b> - bezpieczeństwo na pierwszym miejscu',
      'fact.job': '<b>Ścieżka zatrudnienia</b> po kursie',
      'docs.heading': 'Dokumenty kursu',
      'docs.sub': 'Każdy dokument dostępny w trzech językach (PL / EN / ES) i trzech formatach: podgląd online (HTML), plik do edycji (DOCX) i plik do druku (PDF).',
      'doc.ogolny.eye': 'Dokument 1',
      'doc.ogolny.title': 'Program ogólny',
      'doc.ogolny.desc': 'Cele kursu, sylwetka absolwenta, struktura czterech modułów, metodyka, warunki realizacji, zasady BHP, ocenianie i ścieżka zatrudnienia.',
      'doc.szczegolowy.eye': 'Dokument 2',
      'doc.szczegolowy.title': 'Program szczegółowy',
      'doc.szczegolowy.desc': 'Rozkład dzień po dniu dla wszystkich 20 dni: cele, treści teoretyczne, zakres obserwacji na budowie, efekty uczenia się i kluczowe słownictwo.',
      'doc.scen.eye': 'Dokument 3',
      'doc.scen.title': 'Scenariusze bloków zajęć',
      'doc.scen.desc': 'Szczegółowe scenariusze 20 bloków zajęć: przebieg minutowy, pokaz, obserwacja, ćwiczenie, BHP, metody, ocena, słownictwo i wskazówki dla trenera.',
      'doc.dziennik.eye': 'Dokument 4',
      'doc.dziennik.title': 'Dziennik kursu',
      'doc.dziennik.desc': 'Dokument formalny do prowadzenia kursu: lista uczestników, dziennik zajęć, rejestr obecności, rejestr szkoleń BHP, rejestr ocen i potwierdzenie ukończenia.',
      'strip.title': 'Bezpieczeństwo i praktyka na pierwszym miejscu',
      'strip.body': 'Program łączy wiedzę teoretyczną z natychmiastową obserwacją wykonania na prawdziwej budowie. Blok BHP oparto na aktualnych przepisach (Kodeks pracy Dział X, rozporządzenie w sprawie BHP przy robotach budowlanych z 2003 r. i przepisy powiązane).',
      'footer.disclaimer_html': '<b>Fundacja pomocy prawnej EGIDA</b> realizuje bezpłatne kursy zawodowe dla cudzoziemców legalnie przebywających w Polsce. Kurs powstał z potencjału budowanego w partnerstwie Fundacji na rzecz edukacji SMART (lider) i Fundacji EGIDA w projekcie współfinansowanym ze środków Europejskiego Funduszu Społecznego Plus (EFS+) i budżetu państwa.',
    },
    en: {
      'pin.eyebrow': 'PIN access',
      'pin.title_html': 'General construction course<br><em>EGIDA Foundation</em>',
      'pin.lead': 'Course materials are protected by a PIN. Enter the 6-digit code received from the organiser.',
      'pin.footnote_html': 'Course „Vocational preparation for general construction work" - EGIDA Foundation.<br>The code is stored in your browser for the current session.',
      'hdr.eyebrow': 'EGIDA Foundation - vocational course',
      'hdr.name_html': 'General <em>construction work</em>',
      'hdr.skip': 'Skip to content',
      'hdr.pin_state': 'Access active',
      'lang.label': 'Language',
      'hero.eyebrow': 'Vocational course - 4 weeks - on a live building site - free of charge',
      'hero.title_html': 'Vocational preparation for <em>general construction work</em>',
      'hero.sub': 'specialisation: paving-stone laying',
      'hero.lead': 'A course for foreigners who have come to Poland. Four weeks of learning on a real building site: theory, observation of real work and supervised practice. Strong focus on occupational health and safety (OSH). After completion: a chance of employment on the same site.',
      'fact.weeks': '<b>4 weeks</b> - 20 days - approx. 140 h',
      'fact.site': '<b>On a live site</b> - theory + practice',
      'fact.langs': '<b>3 languages</b> - PL / EN / ES',
      'fact.bhp': '<b>OSH</b> - safety first',
      'fact.job': '<b>Employment pathway</b> after the course',
      'docs.heading': 'Course documents',
      'docs.sub': 'Each document is available in three languages (PL / EN / ES) and three formats: online preview (HTML), editable file (DOCX) and printable file (PDF).',
      'doc.ogolny.eye': 'Document 1',
      'doc.ogolny.title': 'General programme',
      'doc.ogolny.desc': 'Course goals, graduate profile, four-module structure, methodology, delivery conditions, OSH rules, assessment and employment pathway.',
      'doc.szczegolowy.eye': 'Document 2',
      'doc.szczegolowy.title': 'Detailed programme',
      'doc.szczegolowy.desc': 'A day-by-day plan for all 20 days: objectives, theory content, scope of on-site observation, learning outcomes and key vocabulary.',
      'doc.scen.eye': 'Document 3',
      'doc.scen.title': 'Lesson-block scenarios',
      'doc.scen.desc': 'Detailed scenarios for 20 lesson blocks: minute-by-minute run, demonstration, observation, practice, OSH, methods, assessment, vocabulary and trainer tips.',
      'doc.dziennik.eye': 'Document 4',
      'doc.dziennik.title': 'Course journal',
      'doc.dziennik.desc': 'A formal record for running the course: participant list, class log, attendance register, OSH training register, grades register and completion confirmation.',
      'strip.title': 'Safety and practice come first',
      'strip.body': 'The programme combines theory with immediate observation of real work on a building site. The OSH block is based on current regulations (Labour Code Chapter X, the 2003 regulation on OSH during construction works and related provisions).',
      'footer.disclaimer_html': '<b>The EGIDA Foundation for Legal Aid</b> runs free vocational courses for foreigners legally residing in Poland. The course grew from capacity built in partnership between the SMART Foundation for Education (lead) and the EGIDA Foundation in a project co-financed by the European Social Fund Plus (ESF+) and the state budget.',
    },
    es: {
      'pin.eyebrow': 'Acceso PIN',
      'pin.title_html': 'Curso de construcción general<br><em>Fundación EGIDA</em>',
      'pin.lead': 'Los materiales del curso están protegidos por un código PIN. Introduce el código de 6 cifras recibido del organizador.',
      'pin.footnote_html': 'Curso «Preparación profesional para trabajos generales de construcción» - Fundación EGIDA.<br>El código se guarda en el navegador durante la sesión.',
      'hdr.eyebrow': 'Fundación EGIDA - curso profesional',
      'hdr.name_html': 'Trabajos <em>de construcción</em>',
      'hdr.skip': 'Saltar al contenido',
      'hdr.pin_state': 'Acceso activo',
      'lang.label': 'Idioma',
      'hero.eyebrow': 'Curso profesional - 4 semanas - en una obra activa - gratuito',
      'hero.title_html': 'Preparación profesional para <em>trabajos de construcción</em>',
      'hero.sub': 'especialidad: colocación de adoquines',
      'hero.lead': 'Un curso para personas extranjeras llegadas a Polonia. Cuatro semanas de aprendizaje en una obra real: teoría, observación del trabajo real y práctica supervisada. Fuerte énfasis en la seguridad y salud en el trabajo (SST). Al finalizar: posibilidad de empleo en la misma obra.',
      'fact.weeks': '<b>4 semanas</b> - 20 días - aprox. 140 h',
      'fact.site': '<b>En obra activa</b> - teoría + práctica',
      'fact.langs': '<b>3 idiomas</b> - PL / EN / ES',
      'fact.bhp': '<b>SST</b> - la seguridad primero',
      'fact.job': '<b>Vía de empleo</b> tras el curso',
      'docs.heading': 'Documentos del curso',
      'docs.sub': 'Cada documento está disponible en tres idiomas (PL / EN / ES) y tres formatos: vista en línea (HTML), archivo editable (DOCX) y archivo para imprimir (PDF).',
      'doc.ogolny.eye': 'Documento 1',
      'doc.ogolny.title': 'Programa general',
      'doc.ogolny.desc': 'Objetivos del curso, perfil del egresado, estructura de cuatro módulos, metodología, condiciones de ejecución, normas de SST, evaluación y vía de empleo.',
      'doc.szczegolowy.eye': 'Documento 2',
      'doc.szczegolowy.title': 'Programa detallado',
      'doc.szczegolowy.desc': 'Plan día a día para los 20 días: objetivos, contenidos teóricos, alcance de la observación en obra, resultados de aprendizaje y vocabulario clave.',
      'doc.scen.eye': 'Documento 3',
      'doc.scen.title': 'Escenarios de los bloques de clase',
      'doc.scen.desc': 'Escenarios detallados de 20 bloques de clase: desarrollo minuto a minuto, demostración, observación, práctica, SST, métodos, evaluación, vocabulario y consejos para el formador.',
      'doc.dziennik.eye': 'Documento 4',
      'doc.dziennik.title': 'Diario del curso',
      'doc.dziennik.desc': 'Documento formal para llevar el curso: lista de participantes, registro de clases, registro de asistencia, registro de formación en SST, registro de notas y confirmación de finalización.',
      'strip.title': 'La seguridad y la práctica son lo primero',
      'strip.body': 'El programa combina la teoría con la observación inmediata del trabajo real en obra. El bloque de SST se basa en la normativa vigente (Código del Trabajo, Capítulo X, el reglamento de 2003 sobre SST en obras de construcción y disposiciones relacionadas).',
      'footer.disclaimer_html': '<b>La Fundación de asistencia jurídica EGIDA</b> ofrece cursos profesionales gratuitos para personas extranjeras que residen legalmente en Polonia. El curso nació del potencial construido en asociación entre la Fundación SMART para la educación (líder) y la Fundación EGIDA en un proyecto cofinanciado por el Fondo Social Europeo Plus (FSE+) y el presupuesto del Estado.',
    },
  };

  function applyI18n(lang) {
    var d = I18N[lang] || I18N.pl;
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var k = el.dataset.i18n; if (!d[k]) return;
      if (k.indexOf('_html') >= 0 || d[k].indexOf('<') >= 0) el.innerHTML = d[k]; else el.textContent = d[k];
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      el.dataset.i18nAttr.split(',').forEach(function (p) {
        var x = p.split(':'); if (x.length === 2 && d[x[1].trim()]) el.setAttribute(x[0].trim(), d[x[1].trim()]);
      });
    });
  }

  // ============================================================
  // PIN GATE
  // ============================================================
  function initPinGate() {
    var root = document.getElementById('pin-screen');
    if (!root) return;
    if (isUnlocked()) { unlock(); return; }
    var fields = root.querySelectorAll('.pin-fields input');
    var msg = root.querySelector('.pin-msg');
    var attempts = 0;
    setTimeout(function () { fields[0] && fields[0].focus(); }, 30);
    fields.forEach(function (input, idx) {
      input.addEventListener('input', function (e) {
        var v = (e.target.value || '').replace(/\D/g, '').slice(0, 1);
        e.target.value = v;
        if (v && idx < fields.length - 1) fields[idx + 1].focus();
        check();
      });
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !e.target.value && idx > 0) { fields[idx - 1].focus(); fields[idx - 1].value = ''; e.preventDefault(); }
      });
      input.addEventListener('paste', function (e) {
        e.preventDefault();
        var data = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '').slice(0, PIN_LEN);
        for (var i = 0; i < data.length && i < fields.length; i++) fields[i].value = data[i];
        (fields[data.length] || fields[fields.length - 1]).focus();
        check();
      });
    });
    function check() {
      var val = Array.prototype.map.call(fields, function (f) { return f.value; }).join('');
      if (val.length !== PIN_LEN) return;
      if (sha256(val) === PIN_HASH) {
        try { localStorage.setItem(LS_PIN, '1'); } catch (e) {}
        unlock();
      } else {
        attempts++;
        fields.forEach(function (f) { f.classList.add('error'); });
        if (msg) { msg.classList.add('err'); msg.textContent = pinErrMsg(MAX_ATTEMPTS - attempts); }
        if (attempts >= MAX_ATTEMPTS) {
          fields.forEach(function (f) { f.disabled = true; });
          if (msg) msg.textContent = pinLockMsg();
        } else {
          setTimeout(function () {
            fields.forEach(function (f) { f.value = ''; f.classList.remove('error'); });
            if (msg) { msg.classList.remove('err'); msg.textContent = ''; }
            fields[0].focus();
          }, 1100);
        }
      }
    }
  }
  function pinErrMsg(left) {
    var l = getLang();
    if (l === 'en') return 'Incorrect code. Attempts left: ' + left;
    if (l === 'es') return 'Código incorrecto. Intentos restantes: ' + left;
    return 'Nieprawidłowy kod. Pozostało prób: ' + left;
  }
  function pinLockMsg() {
    var l = getLang();
    if (l === 'en') return 'Too many attempts. Refresh the page.';
    if (l === 'es') return 'Demasiados intentos. Actualiza la página.';
    return 'Przekroczono liczbę prób. Odśwież stronę.';
  }
  function unlock() {
    var s = document.getElementById('pin-screen'); if (s) s.remove();
    document.body.classList.remove('hub-locked');
  }
  function isUnlocked() { try { return localStorage.getItem(LS_PIN) === '1'; } catch (e) { return false; } }

  // ============================================================
  // LANG SWITCH
  // ============================================================
  function getLang() {
    try { var s = localStorage.getItem(LS_LANG); if (s && SUPPORTED.indexOf(s) >= 0) return s; } catch (e) {}
    var n = (navigator.language || 'pl').toLowerCase().split('-')[0];
    return SUPPORTED.indexOf(n) >= 0 ? n : 'pl';
  }
  function setLang(lang) {
    if (SUPPORTED.indexOf(lang) < 0) return;
    try { localStorage.setItem(LS_LANG, lang); } catch (e) {}
    applyLang(lang);
  }
  function applyLang(lang) {
    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      b.classList.toggle('on', b.dataset.lang === lang);
      b.setAttribute('aria-pressed', b.dataset.lang === lang ? 'true' : 'false');
    });
    document.querySelectorAll('.langrow').forEach(function (r) {
      r.classList.toggle('is-active', r.dataset.lang === lang);
    });
    document.documentElement.lang = lang;
    applyI18n(lang);
  }
  function initLangSwitch() {
    var hubSwitch = document.querySelector('.lang-switch');
    if (hubSwitch) {
      document.querySelectorAll('.lang-switch button').forEach(function (b) {
        b.addEventListener('click', function () { setLang(b.dataset.lang); });
      });
      applyLang(getLang());
    }
    document.querySelectorAll('.doc-lang-switch a[data-lang]').forEach(function (a) {
      a.addEventListener('click', function () {
        try { localStorage.setItem(LS_LANG, a.dataset.lang); } catch (e) {}
      });
    });
  }

  // ============================================================
  // BOOT
  // ============================================================
  function boot() { initPinGate(); initLangSwitch(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
