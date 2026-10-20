(function () {
  'use strict';
  var P = window.Portal, S = P.speicher, cards = window.LERNKARTEN;
  var $ = function (id) { return document.getElementById(id); };
  var session = null, revealed = false;
  var hasSpeech = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  function dateIn(days) {
    var d = new Date(); d.setDate(d.getDate() + days);
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function key(c) { return 'lp.review.' + c.chapter + '.' + c.reviewSlug; }
  function review(c) { return S.json(key(c), null); }
  function difficult(c) { return S.get('lp.kk.' + c.chapter + '.' + c.slug) === 'schwer'; }
  function message(text) { $('meldung').textContent = text; }
  function save() {
    if (!S.setJson('lp.lernkarten.runde', session)) message('Dein Browser kann den Lernstand gerade nicht speichern. Bitte erlaube Website-Speicher.');
  }
  function stop() { if (hasSpeech) window.speechSynthesis.cancel(); }
  function speak() {
    if (!session || session.pos >= session.queue.length) return;
    stop();
    var text = revealed ? $('antwort').textContent : $('frage').textContent;
    var utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'de-DE'; utterance.rate = 0.95;
    var voice = window.speechSynthesis.getVoices().find(function (v) { return /^de/i.test(v.lang); });
    if (voice) utterance.voice = voice;
    utterance.onerror = function (e) { if (e.error !== 'canceled' && e.error !== 'interrupted') message('Vorlesen ist gerade nicht verfügbar. Prüfe die Sprachausgabe deines Geräts.'); };
    window.speechSynthesis.speak(utterance);
  }
  function pool() {
    var mode = $('modus').value, today = dateIn(0);
    return cards.map(function (c, i) { return i; }).filter(function (i) {
      var c = cards[i], r = review(c);
      return ($('kapitel').value === 'alle' || c.chapter === $('kapitel').value) &&
        (mode === 'alle' || (mode === 'schwer' ? difficult(c) : !r || r.faellig <= today));
    });
  }
  function refresh() {
    var n = pool().length;
    $('vorrat').textContent = n ? n + ' passende Karten · ' + cards.length + ' Karten insgesamt' : 'Hier ist gerade nichts offen. Wähle „Alle Karten üben“ oder ein anderes Kapitel.';
    $('start').disabled = !n;
    var saved = S.json('lp.lernkarten.runde', null);
    $('fortsetzen').hidden = !valid(saved);
  }
  function valid(s) {
    return s && s.version === 1 && Array.isArray(s.queue) && s.queue.length > 0 &&
      Number.isInteger(s.pos) && s.pos >= 0 && s.pos < s.queue.length &&
      s.queue.every(function (i) { return Number.isInteger(i) && cards[i] && s.keys && s.keys[i] === key(cards[i]); });
  }
  function show() {
    stop(); revealed = false;
    $('auswahl').hidden = true; $('abschluss').hidden = true;
    $('runde').hidden = false;
    if (session.pos >= session.queue.length) { finish(); return; }
    var c = cards[session.queue[session.pos]];
    $('zaehler').textContent = 'Karte ' + (session.pos + 1) + ' von ' + session.queue.length;
    $('fortschritt').max = session.queue.length; $('fortschritt').value = session.pos;
    $('quelle').textContent = c.title; $('quelle').href = c.file + '#' + c.section;
    $('frage').textContent = c.question; $('antwort').innerHTML = c.answer;
    // Content comes from the existing authored chapter files.
    $('antwort').querySelectorAll('button, textarea, .notiz-hook').forEach(function (e) { e.remove(); });
    $('antwort').hidden = true; $('bewertung').hidden = true;
    $('aufdecken').hidden = false; $('denkhilfe').hidden = false; $('seite').textContent = 'FRAGE';
    $('frage').focus({ preventScroll: true });
    $('karte').scrollIntoView({ block: 'start', behavior: 'instant' });
  }
  function reveal() {
    if (!session || session.pos >= session.queue.length || revealed) return;
    stop(); revealed = true;
    $('antwort').hidden = false; $('bewertung').hidden = false;
    $('aufdecken').hidden = true; $('denkhilfe').hidden = true; $('seite').textContent = 'FRAGE & ANTWORT';
    $('nochmal').focus({ preventScroll: true });
  }
  function rate(good) {
    if (!revealed) return;
    var c = cards[session.queue[session.pos]], old = review(c);
    var successes = good ? (old && old.erfolge || 0) + 1 : 0;
    var days = good ? [1, 3, 7, 14, 30, 60][Math.min(successes - 1, 5)] : 1;
    var stored = S.setJson(key(c), { erfolge: successes, zuletzt: dateIn(0), faellig: dateIn(days) });
    if (good) { S.del('lp.kk.' + c.chapter + '.' + c.slug); session.good++; }
    else if (!S.set('lp.kk.' + c.chapter + '.' + c.slug, 'schwer')) stored = false;
    if (!stored) message('Der Browser konnte deine Bewertung nicht dauerhaft speichern.');
    session.pos++; save(); show();
  }
  function finish() {
    stop(); $('runde').hidden = true; $('abschluss').hidden = false;
    $('ergebnis').textContent = session.good + ' von ' + session.queue.length + ' gewusst.';
    $('bilanz').textContent = (session.queue.length - session.good) + ' Karten zum Weiterüben. Über „Nur nochmal üben“ kannst du sie direkt wiederholen. Die nächste geplante Wiederholung ist frühestens morgen.';
    S.del('lp.lernkarten.runde'); $('weiter').focus();
  }
  var seen = {};
  cards.forEach(function (c) {
    if (seen[c.chapter]) return; seen[c.chapter] = true;
    var option = document.createElement('option'); option.value = c.chapter;
    option.textContent = P.FAECHER[c.subject].name + ' · ' + c.title;
    $('kapitel').appendChild(option);
  });
  var preferences = S.json('lp.lernkarten.auswahl', {});
  ['kapitel', 'modus', 'umfang'].forEach(function (id) {
    if (preferences[id] && Array.from($(id).options).some(function (o) { return o.value === preferences[id]; })) $(id).value = preferences[id];
    $(id).onchange = function () {
      S.setJson('lp.lernkarten.auswahl', { kapitel: $('kapitel').value, modus: $('modus').value, umfang: $('umfang').value }); refresh();
    };
  });
  $('start').onclick = function () {
    message(''); var queue = pool();
    for (var i = queue.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var tmp = queue[i]; queue[i] = queue[j]; queue[j] = tmp; }
    // Due questions first, then unseen questions; keep variety within each group.
    if ($('modus').value === 'faellig') queue.sort(function (a, b) {
      return (review(cards[a]) ? 0 : 1) - (review(cards[b]) ? 0 : 1);
    });
    var limit = Number($('umfang').value); if (limit) queue = queue.slice(0, limit);
    if (!queue.length) { refresh(); return; }
    var keys = {}; queue.forEach(function (i) { keys[i] = key(cards[i]); });
    session = { version: 1, queue: queue, keys: keys, pos: 0, good: 0 }; save(); show();
  };
  $('fortsetzen').onclick = function () { var s = S.json('lp.lernkarten.runde', null); if (valid(s)) { session = s; show(); } else refresh(); };
  function choose() { stop(); $('runde').hidden = true; $('abschluss').hidden = true; $('auswahl').hidden = false; refresh(); $('start').focus(); }
  $('beenden').onclick = choose; $('weiter').onclick = choose;
  $('aufdecken').onclick = reveal; $('gewusst').onclick = function () { rate(true); };
  $('nochmal').onclick = function () { rate(false); };
  $('vorlesen').onclick = speak; $('stopp').onclick = stop;
  if (!hasSpeech) { $('vorlesen').disabled = true; $('stopp').disabled = true; $('vorlesen').textContent = 'Vorlesen hier nicht verfügbar'; }
  $('theme').onclick = P.themeUmschalten;
  window.addEventListener('pagehide', stop);
  document.addEventListener('keydown', function (e) {
    if ($('runde').hidden || /INPUT|TEXTAREA|SELECT|BUTTON|A/.test(e.target.tagName)) return;
    if (e.code === 'Space') { e.preventDefault(); reveal(); }
  });
  refresh();
})();
