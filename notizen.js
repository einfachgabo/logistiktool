// ============================================================
//  notizen.js – Zentrale Notiz-Logik für das Logistik-Lernportal
//  Einmal hochladen, nie wieder anfassen.
// ============================================================

// Alle bekannten Seiten-Prefixe
const NOTIZ_PREFIXES = {
  'kapitel_gruber_1_2_':          'Kapitel Gruber',
  'kapitel_gruchala_':            'Kapitel Gruchala',
  'kapitel_kroul_0_':             'Kapitel Kroul',
  'kapitel_kroul_1_':             'Kapitel Kroul 1',
  'kapitel_plab_':                'Kapitel Plab',
  'kapitel_0_einfuehrung_':       'Kapitel 0 – Einführung',
  'kap1_1_logistische_ablaeufe_': 'Kap. 1.1 – Logistische Abläufe',
  'kapitel_1_1_':                 'Kapitel 1.1 – Logistische Lösungen',
  'kapitel_1_2_logistiksysteme_': 'Kapitel 1.2 – Logistiksysteme',
  'kommunikation_fuehrung_':      'Kommunikation & Führung',
  'aufgaben_':                    'Aufgaben',
  'formelsammlung_':              'Formelsammlung',
};

function notizGetAll() {
  const result = {};
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    const val = localStorage.getItem(key);
    if (val && val.trim()) result[key] = val;
  }
  return result;
}

function notizExport() {
  const all = notizGetAll();
  const count = Object.keys(all).length;
  if (count === 0) { notizStatus('Keine Notizen vorhanden.', 'error'); return; }
  const data = JSON.stringify({ version: 1, exported: new Date().toISOString(), notizen: all }, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'lernportal_notizen_' + new Date().toISOString().slice(0, 10) + '.json';
  a.click();
  URL.revokeObjectURL(url);
  notizStatus('✓ ' + count + ' Notizen exportiert!', 'success');
}

function notizImport(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(ev) {
    try {
      const data = JSON.parse(ev.target.result);
      if (!data.notizen) throw new Error('Ungültiges Format');
      let count = 0;
      for (const [key, val] of Object.entries(data.notizen)) {
        localStorage.setItem(key, val);
        count++;
      }
      notizStatus('✓ ' + count + ' Notizen importiert! Seite wird neu geladen...', 'success');
      setTimeout(() => location.reload(), 1500);
    } catch(err) {
      notizStatus('Fehler: ' + err.message, 'error');
    }
  };
  reader.readAsText(file);
  e.target.value = '';
}

function notizStatus(msg, type) {
  const el = document.getElementById('notiz-status');
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  el.style.background = type === 'success' ? '#d4edda' : '#f8d7da';
  el.style.color = type === 'success' ? '#155724' : '#721c24';
  setTimeout(() => el.style.display = 'none', 3000);
}

// HTML-Snippet das in jede Sidebar eingefügt wird
function notizInsertSidebarButtons() {
  const sidebar = document.querySelector('.sidebar, aside, #sidebar');
  if (!sidebar) return;
  const div = document.createElement('div');
  div.style.cssText = 'margin-top:1rem;display:flex;flex-direction:column;gap:0.4rem;';
  div.innerHTML = `
    <button onclick="notizExport()" style="font-size:12px;padding:0.4rem 0.7rem;background:#2d6a4f;color:#fff;border:none;border-radius:6px;cursor:pointer;text-align:left;">⬇ Notizen exportieren</button>
    <label style="font-size:12px;padding:0.4rem 0.7rem;background:none;color:#2d6a4f;border:1px solid #2d6a4f;border-radius:6px;cursor:pointer;text-align:left;">
      ⬆ Notizen importieren
      <input type="file" accept=".json" onchange="notizImport(event)" style="display:none">
    </label>
    <div id="notiz-status" style="font-size:11px;padding:0.3rem 0.5rem;border-radius:4px;display:none;margin-top:0.2rem;"></div>
  `;
  sidebar.appendChild(div);
}

document.addEventListener('DOMContentLoaded', notizInsertSidebarButtons);
