/* ============================================================
   Lernportal Fachwirt Logistiksysteme – Engine
   Eine Datei für alle Seiten.

   Eine Kapitelseite braucht nur:
     <script>window.KAPITEL = {id:'kroul-0', fach:'kroul', nummer:'Kapitel 0',
                               titel:'Einführung in die Logistik', farbe:'amber'};</script>
     <script src="assets/portal.js" defer></script>
   Alles Weitere (Navigation, Status, Notizen, Fortschritt, Quiz,
   Karteikarten, Druck) baut die Engine selbst aus dem Markup.
   ============================================================ */
(function () {
  'use strict';

  /* ───────────────────────── Speicher ───────────────────────── */
  var S = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} },
    keys: function () {
      var out = [];
      try { for (var i = 0; i < localStorage.length; i++) out.push(localStorage.key(i)); } catch (e) {}
      return out;
    },
    json: function (k, fallback) {
      var v = S.get(k); if (!v) return fallback;
      try { return JSON.parse(v); } catch (e) { return fallback; }
    },
    setJson: function (k, o) { return S.set(k, JSON.stringify(o)); }
  };

  var STATUS = [
    { wert: 'behandelt',  label: 'im Unterricht dran' },
    { wert: 'verstanden', label: 'verstanden' },
    { wert: 'nochmal',    label: 'nochmal ansehen' }
  ];

  /* ─────────────────── Fächer- und Kapitelregister ─────────────────── */
  var FAECHER = {
    plab:     { name: 'Benedikt Plab',   farbe: 'blue',   thema: 'Logistische Anforderungen ermitteln, analysieren und bewerten', punkte: '30 / 20' },
    gruber:   { name: 'Christian Gruber', farbe: 'green',  thema: 'Logistische Lösungen entwickeln und planen',                    punkte: '35 / 35' },
    kroul:    { name: 'Raphael Kroul',    farbe: 'amber',  thema: 'Logistische Lösungen umsetzen, bewerten und weiterentwickeln',  punkte: '20 / 30' },
    gruchala: { name: 'Kerstin Gruchala', farbe: 'purple', thema: 'Kommunikation, Führung und Zusammenarbeit',                     punkte: '15 / 15' },
    werkzeug: { name: 'Werkzeuge',        farbe: 'teal',   thema: 'Rechnen, Formeln, Üben',                                        punkte: '' }
  };

  /* Alle Kapitel des Portals. Neue Kapitel hier ergänzen – die Startseite
     und die Kapitel-Navigation lesen ausschließlich diese Liste. */
  var KAPITEL_LISTE = [
    { id: 'plab-1',      datei: 'plab-1-logistikstruktur.html',    fach: 'plab',     nummer: '1.1',   titel: 'Logistikstruktur & Grundlagen',        desc: 'Begriff, Ziele, Wertschöpfung, Prozessmanagement, SCM, Bullwhip, Umfeld- und Systemfaktoren, Organisation.' },
    { id: 'plab-2',      datei: 'plab-2-logistiksysteme.html',     fach: 'plab',     nummer: '1.2',   titel: 'Logistiksysteme',                      desc: 'I&K-Systeme, Transport & Umschlag, Fördermittel, Verkehrsträger, Lager & Kommissionierung, Incoterms.' },
    { id: 'plab-3',      datei: 'plab-3-logistische-ablaeufe.html', fach: 'plab',    nummer: '1.3',   titel: 'Logistische Abläufe',                  desc: 'Zielbildung (SMART), Kennzahlen, Leistungsfähigkeit, Bewertungssysteme, Entwicklung.' },
    { id: 'gruber-1',    datei: 'gruber-1-konzepte.html',          fach: 'gruber',   nummer: '1.1–1.11', titel: 'Logistikkonzepte & Analysemethoden', desc: 'Logistikbereiche, Konzept, Wertschöpfung, Belieferung, Benchmarking, SWOT/GAP, Ishikawa, ABC, XYZ, Nachhaltigkeit.' },
    { id: 'gruber-2',    datei: 'gruber-2-beschaffung.html',       fach: 'gruber',   nummer: '1.12–1.23', titel: 'Beschaffung & Bedarfsermittlung',  desc: 'Beschaffungsarten, Kanban, Bedarfsarten, deterministisch/stochastisch, Mittelwerte, Glättung, Bestellverfahren, Andler.' },
    { id: 'gruber-3',    datei: 'gruber-3-lager-transport.html',   fach: 'gruber',   nummer: '1.24–1.36', titel: 'Produktion, Lager & Distribution', desc: 'Produktions-, Distributions- und Transportlogistik, Lagerarten, FIFO/LIFO, Kennzahlen, Kommissionierung, Verpackung, Entsorgung.' },
    { id: 'gruber-4',    datei: 'gruber-4-strategie.html',         fach: 'gruber',   nummer: '2.1–2.3', titel: 'Strategie, IT & Projekte',           desc: 'Visionen & Ziele, FMEA, QFD, Audits, Ausschreibung, ERP/APS, Organisationsformen, Kultur, Projektmanagement.' },
    { id: 'kroul-0',     datei: 'kroul-0-einfuehrung.html',        fach: 'kroul',    nummer: 'Kapitel 0', titel: 'Einführung in die Logistik',       desc: 'Prüfungsstruktur, Entwicklung der Logistik, Definition, 7 R, Fachdisziplinen, xPL, OPP, SCM, Bullwhip.' },
    { id: 'kroul-1',     datei: 'kroul-1-changemanagement.html',   fach: 'kroul',    nummer: 'Kapitel 1', titel: 'Veränderungsprozesse gestalten',   desc: 'Changemanagement, Kondratieff, PDCA, Arten des Wandels, Kotter, Lewin, Streich, Krüger, Widerstände.' },
    { id: 'gruchala-1',  datei: 'gruchala-1-kommunikation.html',   fach: 'gruchala', nummer: 'Kap. 1',  titel: 'Kommunikation',                      desc: 'Watzlawick, Schulz von Thun, Feedback, Moderation, Konflikte, Mobbing, Präsentation, interkulturell.' },
    { id: 'gruchala-2',  datei: 'gruchala-2-personal.html',        fach: 'gruchala', nummer: 'Kap. 2',  titel: 'Personal & Planung',                 desc: 'Handlungskompetenzen, Personalbedarf, Beschaffung, Auswahl, Personalmarketing, Employer Branding.' },
    { id: 'gruchala-3',  datei: 'gruchala-3-arbeitsrecht.html',    fach: 'gruchala', nummer: 'Kap. 3',  titel: 'Arbeitszeit & Mitbestimmung',        desc: 'Arbeitszeitgesetz, Arbeitszeitmodelle, Betriebsverfassungsgesetz, Betriebsrat.' },
    { id: 'gruchala-4',  datei: 'gruchala-4-fuehrung.html',        fach: 'gruchala', nummer: 'Kap. 4',  titel: 'Führung & Motivation',               desc: 'Führungsstile, Blake & Mouton, Hersey & Blanchard, Maslow & Co., Führungsinstrumente, Management-by, Tuckman.' },
    { id: 'gruchala-5',  datei: 'gruchala-5-ausbildung.html',      fach: 'gruchala', nummer: 'Kap. 5–7', titel: 'Ausbildung & Arbeitsschutz',        desc: 'BBiG, Lehrmethoden, Prüfung, berufliche Entwicklung, Arbeitsschutz, Gefährdungsbeurteilung, STOP-Prinzip.' },
    { id: 'mathe',       datei: 'mathe-grundlagen.html',           fach: 'werkzeug', nummer: 'Basis',   titel: 'Mathe-Grundlagen',                   desc: 'Rechenreihenfolge, Brüche, Prozent, Wurzeln, Gleichungen umstellen – von Null an erklärt.' },
    { id: 'formeln',     datei: 'formelsammlung.html',             fach: 'werkzeug', nummer: 'Referenz', titel: 'Formelsammlung',                    desc: 'Alle prüfungsrelevanten Formeln mit Bedeutung, Einheiten und Rechenbeispiel.' },
    { id: 'aufgaben',    datei: 'aufgaben.html',                   fach: 'werkzeug', nummer: 'Übung',   titel: 'Aufgaben & Lösungen',                desc: 'Prüfungstypische Rechen- und Theorieaufgaben mit vollständigem Lösungsweg.' }
  ];

  /* ───────────────────────── Helfer ───────────────────────── */
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
  function heute() { var d = new Date(); return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }); }
  function kapById(id) { for (var i = 0; i < KAPITEL_LISTE.length; i++) if (KAPITEL_LISTE[i].id === id) return KAPITEL_LISTE[i]; return null; }

  /* ───────────────────────── Theme ───────────────────────── */
  function themeAnwenden() {
    var t = S.get('lp.theme');
    if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
  }
  function themeUmschalten() {
    S.set('lp.theme', S.get('lp.theme') === 'dark' ? 'light' : 'dark');
    themeAnwenden();
  }
  themeAnwenden();

  /* ═══════════════ Fortschritt (seitenübergreifend) ═══════════════ */
  function kapitelFortschritt(kapId) {
    var idx = S.json('lp.index.' + kapId, null);
    if (!idx || !idx.sections || !idx.sections.length) return null;
    var gesamt = idx.sections.length, behandelt = 0, verstanden = 0, nochmal = 0;
    idx.sections.forEach(function (s) {
      var st = S.get('lp.status.' + kapId + '.' + s.id);
      if (st === 'verstanden') { verstanden++; behandelt++; }
      else if (st === 'behandelt') behandelt++;
      else if (st === 'nochmal') { nochmal++; behandelt++; }
    });
    return {
      gesamt: gesamt, behandelt: behandelt, verstanden: verstanden, nochmal: nochmal,
      pctBehandelt: Math.round(behandelt / gesamt * 100),
      pctVerstanden: Math.round(verstanden / gesamt * 100),
      titel: idx.titel, datei: idx.datei, sections: idx.sections
    };
  }

  function notizenZaehlen(kapId) {
    var p = 'lp.notiz.' + (kapId ? kapId + '.' : ''), n = 0;
    S.keys().forEach(function (k) { if (k.indexOf(p) === 0 && (S.get(k) || '').trim()) n++; });
    return n;
  }

  /* ═══════════════ Notizen an einen Block hängen ═══════════════ */
  function notizHook(host, kapId, slug) {
    if (!slug || host.querySelector(':scope > .notiz-hook')) return;
    var key = 'lp.notiz.' + kapId + '.' + slug;
    var metaKey = 'lp.notizmeta.' + kapId + '.' + slug;

    var wrap = el('div', 'notiz-hook');
    var btn = el('button', 'notiz-btn');
    var feld = el('textarea', 'notiz-feld');
    var meta = el('div', 'notiz-meta');
    feld.placeholder = 'Was hat der Dozent dazu gesagt? Eigenes Beispiel? Prüfungshinweis?';
    feld.setAttribute('aria-label', 'Notiz zu diesem Block');

    var vorhanden = S.get(key) || '';
    function btnText() {
      var hat = (feld.value || '').trim().length > 0;
      btn.classList.toggle('hat-inhalt', hat);
      btn.textContent = feld.classList.contains('auf')
        ? '✕ Notiz zuklappen'
        : (hat ? '📝 Notiz (' + feld.value.trim().split(/\s+/).length + ' Wörter)' : '✏ Notiz');
    }
    function metaText() {
      var t = S.get(metaKey);
      meta.textContent = t ? 'zuletzt geändert: ' + t : '';
      meta.classList.toggle('auf', !!t && feld.classList.contains('auf'));
    }

    if (vorhanden.trim()) { feld.value = vorhanden; feld.classList.add('auf'); }
    btnText(); metaText();

    btn.addEventListener('click', function () {
      feld.classList.toggle('auf');
      if (feld.classList.contains('auf')) feld.focus();
      btnText(); metaText();
    });

    var timer = null;
    feld.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        if (feld.value.trim()) { S.set(key, feld.value); S.set(metaKey, heute()); }
        else { S.del(key); S.del(metaKey); }
        btnText(); metaText();
      }, 350);
    });

    wrap.appendChild(btn); wrap.appendChild(feld); wrap.appendChild(meta);
    host.appendChild(wrap);
  }

  /* ═══════════════ Kapitelseite aufbauen ═══════════════ */
  function kapitelSeite() {
    var K = window.KAPITEL;
    var abschnitte = Array.prototype.slice.call(document.querySelectorAll('section.abschnitt'));
    if (!abschnitte.length) return;

    var fach = FAECHER[K.fach] || FAECHER.werkzeug;
    var indexEintrag = { titel: K.titel, datei: location.pathname.split('/').pop() || (kapById(K.id) || {}).datei, fach: K.fach, nummer: K.nummer, sections: [] };

    /* ---- 1. Abschnitte: Status + Notiz + Index ---- */
    abschnitte.forEach(function (sec, i) {
      if (!sec.id) sec.id = 'abschnitt-' + (i + 1);
      var h2 = sec.querySelector('.ab-kopf h2');
      var nr = sec.querySelector('.ab-nr');
      var titel = sec.dataset.titel;
      if (!titel && h2) {
        var klon = h2.cloneNode(true);
        var weg = klon.querySelector('.ab-nr');
        if (weg) weg.remove();
        titel = klon.textContent.trim();
      }
      if (!titel) titel = 'Abschnitt ' + (i + 1);
      indexEintrag.sections.push({ id: sec.id, titel: titel, nr: nr ? nr.textContent.trim() : '', gruppe: sec.dataset.gruppe || '' });

      var kopf = sec.querySelector('.ab-kopf');
      if (!kopf) return;

      var leiste = el('div', 'ab-status');
      var statusKey = 'lp.status.' + K.id + '.' + sec.id;

      STATUS.forEach(function (s) {
        var b = el('button', 'st-btn', s.label);
        b.dataset.wert = s.wert;
        if (S.get(statusKey) === s.wert) b.classList.add('an');
        b.addEventListener('click', function () {
          var neu = S.get(statusKey) === s.wert ? null : s.wert;
          if (neu) S.set(statusKey, neu); else S.del(statusKey);
          leiste.querySelectorAll('.st-btn').forEach(function (x) { x.classList.toggle('an', x.dataset.wert === neu); });
          S.setJson('lp.index.' + K.id, indexEintrag);
          navPunkteAktualisieren();
          seitenFortschritt();
        });
        leiste.appendChild(b);
      });

      var hier = el('button', 'st-hier', '📍 wir sind hier');
      hier.addEventListener('click', function () {
        var aktuell = S.get('lp.hier.' + K.id);
        if (aktuell === sec.id) { S.del('lp.hier.' + K.id); S.del('lp.hier'); }
        else {
          S.set('lp.hier.' + K.id, sec.id);
          S.setJson('lp.hier', { kapId: K.id, kapTitel: K.titel, nummer: K.nummer, sectId: sec.id, sectTitel: titel, datei: indexEintrag.datei, datum: heute() });
        }
        hierMarkieren();
        navPunkteAktualisieren();
      });
      leiste.appendChild(hier);

      kopf.insertAdjacentElement('afterend', leiste);
      notizHook(sec, K.id, 'abschnitt-' + sec.id);
    });

    S.setJson('lp.index.' + K.id, indexEintrag);

    /* ---- 2. Notizen an alle markierten Blöcke ---- */
    document.querySelectorAll('[data-notiz]').forEach(function (b) { notizHook(b, K.id, b.dataset.notiz); });

    /* ---- 3. Sidebar bauen ---- */
    sidebarBauen(K, fach, indexEintrag);

    /* ---- 4. „Wir sind hier"-Markierung ---- */
    hierMarkieren();

    /* ---- 5. Werkzeugleiste ---- */
    werkzeugleiste(K);

    /* ---- 6. Scroll-Fortschritt + aktiver Navigationspunkt ---- */
    scrollBalken();
    navBeobachten();
    seitenFortschritt();

    /* ---- 7. Interaktionen ---- */
    quizAktivieren();
    aufgabenAktivieren();
    abfragenAktivieren(K);

    function hierMarkieren() {
      var aktiv = S.get('lp.hier.' + K.id);
      abschnitte.forEach(function (sec) {
        var ist = sec.id === aktiv;
        sec.classList.toggle('ist-hier', ist);
        var b = sec.querySelector('.st-hier');
        if (b) { b.classList.toggle('an', ist); b.textContent = ist ? '📍 hier stehen wir' : '📍 wir sind hier'; }
      });
    }

    function seitenFortschritt() {
      var f = kapitelFortschritt(K.id); if (!f) return;
      var box = document.getElementById('sb-fortschritt'); if (!box) return;
      box.querySelector('.sb-track .done').style.width = (f.pctBehandelt - f.pctVerstanden) + '%';
      box.querySelector('.sb-track .got').style.width = f.pctVerstanden + '%';
      box.querySelector('.sb-zahl').textContent = f.verstanden + ' / ' + f.gesamt + ' verstanden';
    }

    function navPunkteAktualisieren() {
      var aktiv = S.get('lp.hier.' + K.id);
      document.querySelectorAll('.sb-nav a[data-sect]').forEach(function (a) {
        var st = S.get('lp.status.' + K.id + '.' + a.dataset.sect) || '';
        var d = a.querySelector('.dot');
        d.className = 'dot ' + (a.dataset.sect === aktiv ? 'hier' : st);
      });
    }
    window.__navPunkte = navPunkteAktualisieren;
    navPunkteAktualisieren();
  }

  /* ═══════════════ Sidebar ═══════════════ */
  function sidebarBauen(K, fach, idx) {
    var aside = document.querySelector('aside.sidebar');
    if (!aside) {
      aside = el('aside', 'sidebar');
      document.body.insertBefore(aside, document.body.firstChild);
      document.body.classList.add('mit-sidebar');
    }
    aside.innerHTML = '';

    var kopf = el('div', 'sb-head');
    var back = el('a', 'sb-back', '← Alle Kapitel');
    back.href = 'index.html';
    kopf.appendChild(back);
    kopf.appendChild(el('div', 'sb-fach', K.nummer + ' · ' + K.titel));
    kopf.appendChild(el('div', 'sb-dozent', fach.name + ' · ' + fach.thema));
    aside.appendChild(kopf);

    var fort = el('div', 'sb-progress'); fort.id = 'sb-fortschritt';
    var reihe = el('div', 'sb-progress-row');
    reihe.appendChild(el('span', null, 'Fortschritt'));
    reihe.appendChild(el('span', 'sb-zahl', '0 / 0'));
    var track = el('div', 'sb-track');
    track.appendChild(el('div', 'done')); track.appendChild(el('div', 'got'));
    track.querySelector('.done').style.width = '0%'; track.querySelector('.got').style.width = '0%';
    fort.appendChild(reihe); fort.appendChild(track);
    aside.appendChild(fort);

    var letzteGruppe = null, nav = null;
    idx.sections.forEach(function (s) {
      if (s.gruppe && s.gruppe !== letzteGruppe) {
        aside.appendChild(el('div', 'sb-gruppe', s.gruppe));
        nav = el('nav', 'sb-nav'); aside.appendChild(nav);
        letzteGruppe = s.gruppe;
      }
      if (!nav) { nav = el('nav', 'sb-nav'); aside.appendChild(nav); }
      var a = el('a'); a.href = '#' + s.id; a.dataset.sect = s.id;
      a.appendChild(el('span', 'dot'));
      a.appendChild(el('span', null, (s.nr && /^[\d.]+$/.test(s.nr) ? s.nr + ' ' : '') + s.titel));
      nav.appendChild(a);
    });

    var foot = el('div', 'sb-foot');
    var nz = notizenZaehlen(K.id);
    var l1 = el('a', null, '📝 Meine Notizen' + (nz ? ' (' + nz + ')' : '')); l1.href = 'notizen.html';
    var l2 = el('a', null, '🧮 Formelsammlung'); l2.href = 'formelsammlung.html';
    var l3 = el('a', null, '✍️ Aufgaben'); l3.href = 'aufgaben.html';
    foot.appendChild(l1); foot.appendChild(l2); foot.appendChild(l3);
    aside.appendChild(foot);
  }

  /* ═══════════════ Werkzeugleiste ═══════════════ */
  function werkzeugleiste(K) {
    if (document.querySelector('.werkzeuge')) return;
    var box = el('div', 'werkzeuge');

    var kk = el('button', 'wz-btn', '🃏'); kk.title = 'Karteikarten aus diesem Kapitel (Taste K)';
    kk.addEventListener('click', function () { karteikartenStarten(K); });

    var top = el('button', 'wz-btn', '↑'); top.title = 'Nach oben';
    top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

    var th = el('button', 'wz-btn', '🌓'); th.title = 'Hell / Dunkel';
    th.addEventListener('click', themeUmschalten);

    var pr = el('button', 'wz-btn', '🖨'); pr.title = 'Drucken / als PDF sichern (inkl. Notizen & Lösungen)';
    pr.addEventListener('click', function () { window.print(); });

    box.appendChild(kk); box.appendChild(th); box.appendChild(pr); box.appendChild(top);
    document.body.appendChild(box);

    document.addEventListener('keydown', function (e) {
      if (e.target.matches('textarea, input')) return;
      if (e.key === 'k' || e.key === 'K') karteikartenStarten(K);
    });
  }

  /* ═══════════════ Scrollbalken & Navigation ═══════════════ */
  function scrollBalken() {
    if (document.querySelector('.scroll-bar')) return;
    var bar = el('div', 'scroll-bar'); var fill = el('div', 'scroll-fill');
    bar.appendChild(fill); document.body.appendChild(bar);
    window.addEventListener('scroll', function () {
      var t = document.documentElement.scrollHeight - window.innerHeight;
      fill.style.width = (t > 0 ? (window.scrollY / t) * 100 : 0) + '%';
    }, { passive: true });
  }

  function navBeobachten() {
    var links = document.querySelectorAll('.sb-nav a[data-sect]');
    if (!links.length || !('IntersectionObserver' in window)) return;
    var beob = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (l) { l.classList.toggle('active', l.dataset.sect === e.target.id); });
      });
    }, { rootMargin: '-10% 0px -70% 0px' });
    document.querySelectorAll('section.abschnitt').forEach(function (s) { beob.observe(s); });
  }

  /* ═══════════════ Quiz ═══════════════ */
  function quizAktivieren() {
    document.querySelectorAll('.quiz').forEach(function (quiz) {
      var bloecke = quiz.querySelectorAll('.q-block');
      var punkte = 0, beantwortet = 0, gesamt = bloecke.length;
      bloecke.forEach(function (b, i) {
        var nr = b.querySelector('.q-nr');
        if (nr && !nr.textContent.trim()) nr.textContent = 'Frage ' + (i + 1) + ' von ' + gesamt;
        b.querySelectorAll('.q-opt').forEach(function (opt) {
          opt.addEventListener('click', function () {
            var richtig = opt.dataset.richtig === 'true';
            b.querySelectorAll('.q-opt').forEach(function (o) {
              o.disabled = true;
              if (o.dataset.richtig === 'true') o.classList.add('richtig');
            });
            if (!richtig) opt.classList.add('falsch');
            var fb = b.querySelector('.q-fb');
            if (fb) {
              fb.textContent = (richtig ? '✓ Richtig. ' : '✗ Leider falsch. ') + (fb.dataset.erklaerung || '');
              fb.className = 'q-fb zeig ' + (richtig ? 'ok' : 'nope');
            }
            if (richtig) punkte++;
            beantwortet++;
            if (beantwortet === gesamt) {
              var score = quiz.querySelector('.q-score');
              if (score) {
                score.querySelector('.z').textContent = punkte + ' / ' + gesamt;
                var t = score.querySelector('.t');
                var msg = ['Nochmal von vorn lesen – das sitzt noch nicht.', 'Grundlage steht, jetzt die Lücken schließen.', 'Solide. Ein paar Details fehlen noch.', 'Sehr gut – das kannst du.', 'Prüfungsreif.'];
                if (t) t.textContent = msg[Math.min(Math.floor(punkte / gesamt * 5), 4)];
                score.classList.add('zeig');
              }
            }
          });
        });
      });
    });
  }

  /* ═══════════════ Aufgaben/Lösungen ═══════════════ */
  function aufgabenAktivieren() {
    document.querySelectorAll('.aufgabe').forEach(function (a) {
      var btn = a.querySelector('.loesung-btn'), loesung = a.querySelector('.loesung');
      if (!btn || !loesung) return;
      btn.addEventListener('click', function () {
        var auf = loesung.classList.toggle('auf');
        btn.textContent = auf ? '▲ Lösung ausblenden' : '▼ Lösung anzeigen';
      });
      if (!btn.textContent.trim()) btn.textContent = '▼ Lösung anzeigen';
    });
  }

  /* ═══════════════ Selbstabfragen ═══════════════ */
  function abfragenAktivieren(K) {
    document.querySelectorAll('.abfrage-liste').forEach(function (liste) {
      var kopf = liste.querySelector('.abfrage-kopf');
      if (!kopf) return;
      if (!kopf.querySelector('button')) {
        var b = el('button', null, 'alle aufklappen');
        b.addEventListener('click', function () {
          var offen = liste.querySelectorAll('details.abfrage[open]').length > 0;
          liste.querySelectorAll('details.abfrage').forEach(function (d) { d.open = !offen; });
          b.textContent = offen ? 'alle aufklappen' : 'alle zuklappen';
        });
        kopf.appendChild(b);
      }
    });
  }

  /* ═══════════════ Karteikarten ═══════════════ */
  function karteikartenSammeln() {
    var karten = [];
    document.querySelectorAll('details.abfrage').forEach(function (d) {
      var s = d.querySelector('summary'), a = d.querySelector('.antwort');
      if (!s || !a) return;
      var sec = d.closest('section.abschnitt');
      karten.push({ frage: s.textContent.trim(), antwort: a.innerHTML, sect: sec ? sec.id : '', slug: d.dataset.kk || s.textContent.trim().slice(0, 60) });
    });
    return karten;
  }

  function karteikartenStarten(K) {
    var alle = karteikartenSammeln();
    if (!alle.length) { alert('In diesem Kapitel sind noch keine Selbstabfragen hinterlegt.'); return; }
    // Schwer markierte Karten zuerst, Rest gemischt
    var schwer = [], rest = [];
    alle.forEach(function (k) {
      (S.get('lp.kk.' + K.id + '.' + k.slug) === 'schwer' ? schwer : rest).push(k);
    });
    for (var i = rest.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = rest[i]; rest[i] = rest[j]; rest[j] = t; }
    var stapel = schwer.concat(rest), pos = 0, gewusst = 0;

    var ov = document.querySelector('.kk-overlay');
    if (!ov) { ov = el('div', 'kk-overlay'); ov.innerHTML = '<div class="kk-box"></div>'; document.body.appendChild(ov); }
    var box = ov.querySelector('.kk-box');
    ov.classList.add('auf');

    function zeige() {
      if (pos >= stapel.length) {
        box.innerHTML = '<div class="kk-zaehler"><span>Durchlauf beendet</span></div>' +
          '<div class="kk-frage">' + gewusst + ' von ' + stapel.length + ' gewusst</div>' +
          '<div class="kk-aktionen"><button class="primaer" data-akt="neu">Nochmal</button><button class="zu" data-akt="zu">Schließen</button></div>';
        return;
      }
      var k = stapel[pos];
      box.innerHTML =
        '<div class="kk-zaehler"><span>Karte ' + (pos + 1) + ' von ' + stapel.length + '</span><span>' + esc(K.nummer) + '</span></div>' +
        '<div class="kk-frage">' + esc(k.frage) + '</div>' +
        '<div class="kk-antwort">' + k.antwort + '</div>' +
        '<div class="kk-aktionen"><button class="primaer" data-akt="zeigen">Antwort zeigen</button>' +
        '<button class="zu" data-akt="zu">Schließen</button></div>';
    }

    box.onclick = function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var akt = b.dataset.akt, k = stapel[pos];
      if (akt === 'zu') { ov.classList.remove('auf'); return; }
      if (akt === 'neu') { pos = 0; gewusst = 0; zeige(); return; }
      if (akt === 'zeigen') {
        box.querySelector('.kk-antwort').classList.add('auf');
        box.querySelector('.kk-aktionen').innerHTML =
          '<button class="gut" data-akt="gut">Gewusst</button>' +
          '<button class="schlecht" data-akt="schwer">Nochmal üben</button>' +
          '<button class="zu" data-akt="zu">Schließen</button>';
        return;
      }
      if (akt === 'gut') { S.del('lp.kk.' + K.id + '.' + k.slug); gewusst++; pos++; zeige(); return; }
      if (akt === 'schwer') { S.set('lp.kk.' + K.id + '.' + k.slug, 'schwer'); pos++; zeige(); return; }
    };
    ov.onclick = function (e) { if (e.target === ov) ov.classList.remove('auf'); };
    document.addEventListener('keydown', function esc2(e) {
      if (e.key === 'Escape') { ov.classList.remove('auf'); document.removeEventListener('keydown', esc2); }
    });
    zeige();
  }

  /* ═══════════════ Export / Import / Migration ═══════════════ */
  function alleDaten() {
    var d = { version: 2, portal: 'fachwirt-logistiksysteme', exportiert: new Date().toISOString(), eintraege: {} };
    S.keys().forEach(function (k) {
      if (k.indexOf('lp.') === 0 || k.indexOf('kapitel_') === 0 || k.indexOf('kap1_') === 0 ||
          k.indexOf('kommunikation_') === 0 || k.indexOf('aufgaben_') === 0 || k.indexOf('formelsammlung_') === 0) {
        d.eintraege[k] = S.get(k);
      }
    });
    return d;
  }
  function exportieren() {
    var d = alleDaten(), n = Object.keys(d.eintraege).length;
    if (!n) { alert('Es sind noch keine Notizen oder Lernstände gespeichert.'); return; }
    var blob = new Blob([JSON.stringify(d, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = 'lernportal-sicherung-' + new Date().toISOString().slice(0, 10) + '.json';
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    return n;
  }
  function importieren(text) {
    var d = JSON.parse(text);
    var eintraege = d.eintraege || d.notizen;
    if (!eintraege) throw new Error('Datei enthält keine erkennbaren Daten.');
    var n = 0;
    Object.keys(eintraege).forEach(function (k) { if (S.set(k, eintraege[k])) n++; });
    return n;
  }

  /* Alte Notizen (Positions-IDs der ersten Portalversion) einsammeln */
  function altNotizen() {
    var out = [];
    S.keys().forEach(function (k) {
      if (k.indexOf('lp.') === 0) return;
      var v = S.get(k);
      if (v && v.trim() && /^(kapitel_|kap1_|kommunikation_|aufgaben_|formelsammlung_)/.test(k)) out.push({ key: k, text: v });
    });
    return out;
  }

  /* ═══════════════ Startseite ═══════════════ */
  function startSeite() {
    var wrap = document.getElementById('portal-inhalt');
    if (!wrap) return;

    /* Banner: wo stehen wir gerade */
    var hier = S.json('lp.hier', null);
    var bannerBox = document.getElementById('hier-banner');
    if (bannerBox) {
      if (hier) {
        bannerBox.innerHTML =
          '<span class="hb-label">Aktueller Unterrichtsstand</span>' +
          '<span class="hb-text">' + esc(hier.nummer + ' · ' + hier.kapTitel) + ' → ' + esc(hier.sectTitel) + '</span>' +
          '<a href="' + esc(hier.datei) + '#' + esc(hier.sectId) + '">Dorthin springen →</a>';
        bannerBox.style.display = 'flex';
      } else {
        bannerBox.innerHTML = '<span class="hb-label">Aktueller Unterrichtsstand</span>' +
          '<span class="hb-text">Noch nicht gesetzt – im Kapitel auf „📍 wir sind hier" tippen.</span>';
        bannerBox.style.display = 'flex';
      }
    }

    /* Kennzahlen */
    var gesamtAb = 0, gesamtBeh = 0, gesamtVer = 0, gesamtNoch = 0, offeneKap = 0;
    KAPITEL_LISTE.forEach(function (k) {
      var f = kapitelFortschritt(k.id);
      if (!f) { offeneKap++; return; }
      gesamtAb += f.gesamt; gesamtBeh += f.behandelt; gesamtVer += f.verstanden; gesamtNoch += f.nochmal;
    });
    var stats = document.getElementById('portal-stats');
    if (stats) {
      stats.innerHTML =
        stat(gesamtAb ? Math.round(gesamtVer / gesamtAb * 100) + '%' : '–', 'verstanden') +
        stat(gesamtAb ? Math.round(gesamtBeh / gesamtAb * 100) + '%' : '–', 'im Unterricht behandelt') +
        stat(gesamtNoch || '0', 'zum Wiederholen markiert') +
        stat(notizenZaehlen(''), 'eigene Notizen');
    }
    function stat(z, l) { return '<div class="stat"><div class="s-zahl">' + z + '</div><div class="s-label">' + l + '</div></div>'; }

    /* Kapitel nach Fach */
    var html = '';
    var reihenfolge = ['plab', 'gruber', 'kroul', 'gruchala', 'werkzeug'];
    reihenfolge.forEach(function (fachId) {
      var f = FAECHER[fachId];
      var kaps = KAPITEL_LISTE.filter(function (k) { return k.fach === fachId; });
      if (!kaps.length) return;
      html += '<div class="fach-block"><div class="fach-kopf">' +
        '<span class="fach-punkt" style="background:var(--' + f.farbe + ')"></span>' +
        '<span class="fach-name" style="color:var(--' + f.farbe + ')">' + esc(f.name) + '</span>' +
        '<span class="fach-thema">' + esc(f.thema) + '</span>' +
        (f.punkte ? '<span class="fach-punkte">' + esc(f.punkte) + ' Pkt.</span>' : '') +
        '</div><div class="kapitel-grid">';
      kaps.forEach(function (k) {
        var fo = kapitelFortschritt(k.id);
        html += '<a class="kapitel-karte ' + f.farbe + '" href="' + esc(k.datei) + '">' +
          '<span class="kk-nr">' + esc(k.nummer) + '</span>' +
          '<span class="kk-titel">' + esc(k.titel) + '</span>' +
          '<span class="kk-desc">' + esc(k.desc) + '</span>' +
          '<span class="kk-fort"><span class="kk-track">' +
            '<span class="done" style="width:' + (fo ? fo.pctBehandelt - fo.pctVerstanden : 0) + '%"></span>' +
            '<span class="got" style="width:' + (fo ? fo.pctVerstanden : 0) + '%"></span>' +
          '</span><span class="kk-fort-txt"><span>' +
            (fo ? fo.verstanden + ' / ' + fo.gesamt + ' Abschnitte verstanden' : 'noch nicht geöffnet') +
          '</span>' + (fo && fo.nochmal ? '<span style="color:var(--red)">' + fo.nochmal + '× wiederholen</span>' : '') +
          '</span></span></a>';
      });
      html += '</div></div>';
    });
    wrap.innerHTML = html;

    /* Lernplan: was ist offen */
    var plan = document.getElementById('lernplan');
    if (plan) {
      var noch = [], nichtBeh = [];
      KAPITEL_LISTE.forEach(function (k) {
        var f = kapitelFortschritt(k.id); if (!f) return;
        f.sections.forEach(function (s) {
          var st = S.get('lp.status.' + k.id + '.' + s.id);
          if (st === 'nochmal') noch.push({ k: k, s: s });
          else if (st === 'behandelt') nichtBeh.push({ k: k, s: s });
        });
      });
      var p = '';
      if (noch.length) {
        p += '<h3>Zum Wiederholen markiert (' + noch.length + ')</h3><ul>';
        noch.forEach(function (x) { p += '<li><a class="link" href="' + esc(x.k.datei) + '#' + esc(x.s.id) + '">' + esc(x.k.titel) + ' → ' + esc(x.s.titel) + '</a></li>'; });
        p += '</ul>';
      }
      if (nichtBeh.length) {
        p += '<h3>Im Unterricht dran gewesen, aber noch nicht als verstanden markiert (' + nichtBeh.length + ')</h3><ul>';
        nichtBeh.slice(0, 40).forEach(function (x) { p += '<li><a class="link" href="' + esc(x.k.datei) + '#' + esc(x.s.id) + '">' + esc(x.k.titel) + ' → ' + esc(x.s.titel) + '</a></li>'; });
        if (nichtBeh.length > 40) p += '<li class="hinweis-klein">… und ' + (nichtBeh.length - 40) + ' weitere</li>';
        p += '</ul>';
      }
      if (!p) p = '<p class="hinweis-klein">Sobald du in den Kapiteln Abschnitte als „im Unterricht dran“ oder „nochmal ansehen“ markierst, entsteht hier automatisch dein Lernplan.</p>';
      plan.innerHTML = p;
    }
  }

  /* ═══════════════ Öffentliche Schnittstelle ═══════════════ */
  window.Portal = {
    FAECHER: FAECHER,
    KAPITEL_LISTE: KAPITEL_LISTE,
    fortschritt: kapitelFortschritt,
    notizenZaehlen: notizenZaehlen,
    exportieren: exportieren,
    importieren: importieren,
    altNotizen: altNotizen,
    alleDaten: alleDaten,
    themeUmschalten: themeUmschalten,
    speicher: S,
    esc: esc
  };

  /* ═══════════════ Start ═══════════════ */
  function start() {
    if (window.KAPITEL) kapitelSeite();
    startSeite();
    if (typeof window.seiteFertig === 'function') window.seiteFertig();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
