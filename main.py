from flask import Flask, request, jsonify, render_template_string, Response, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML)

HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>My App Launcher</title>
  <meta name="description" content="Single-file HTML dashboard to launch web apps and trigger webhooks." />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Compact scrollbar for result panes */
    .thin-scrollbar::-webkit-scrollbar { height: 6px; width: 6px; }
    .thin-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 999px; }
  </style>
</head>
<body class="bg-slate-50 text-slate-900">
  <div class="max-w-7xl mx-auto px-4 py-8">
    <header class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">App Launcher</h1>
        <p class="text-slate-600">Click to open your apps or trigger endpoints. No backend required.</p>
      </div>
      <div class="flex items-center gap-2">
        <input id="authToken" type="password" placeholder="Auth/Bearer token (optional)" class="px-3 py-2 rounded-xl border border-slate-300 bg-white text-sm w-64"/>
        <button id="saveTokenBtn" class="px-3 py-2 rounded-xl bg-slate-800 text-white text-sm hover:bg-slate-900">Save</button>
      </div>
    </header>

    <!-- Controls -->
    <section class="mt-6 flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
      <div class="flex items-center gap-3">
        <div class="relative">
          <input id="searchInput" type="search" placeholder="Search apps…" class="pl-9 pr-3 py-2 rounded-xl border border-slate-300 bg-white text-sm w-72"/>
          <span class="absolute left-3 top-2.5 text-slate-400">🔎</span>
        </div>
        <select id="categoryFilter" class="px-3 py-2 rounded-xl border border-slate-300 bg-white text-sm">
          <option value="">All categories</option>
        </select>
        <label class="flex items-center gap-2 text-sm text-slate-600"><input id="showFavoritesOnly" type="checkbox" class="rounded"/> Favorites</label>
      </div>
      <details class="bg-white border border-slate-200 rounded-2xl p-4 w-full md:w-auto">
        <summary class="cursor-pointer font-medium">How to add apps</summary>
        <div class="mt-3 text-sm text-slate-700 space-y-2">
          <p>Edit the <code>apps</code> array inside this file. Each app supports:</p>
          <pre class="bg-slate-50 p-3 rounded-xl overflow-x-auto text-xs">{
  id: "statusPanel",
  name: "Status Panel",
  description: "Open dashboard",
  icon: "📊",                 // any emoji
  category: "Monitoring",
  type: "url",                // "url" | "endpoint"
  url: "https://example.com"  // opens in a new tab
}
// or trigger an HTTP endpoint (POST/GET)
{
  id: "sync",
  name: "Nightly Sync",
  description: "Kick off a sync job",
  icon: "🔁",
  category: "Jobs",
  type: "endpoint",
  method: "POST",             // or GET
  url: "https://api.example.com/jobs/sync",
  headers: { "X-Key": "{{token}}" }, // optional; {{token}} replaced with saved token
  body: { "force": true }     // optional JSON body for POST
}</pre>
          <p><strong>Notes:</strong> This page can only open URLs or call HTTP endpoints your apps expose. Running local files/CLI from a plain HTML page isn’t possible without a backend or a custom protocol.</p>
          <p>If your endpoint is on another origin, make sure it enables CORS for your domain.</p>
        </div>
      </details>
    </section>

    <!-- App grid -->
    <section class="mt-6">
      <div id="appsGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"></div>
    </section>

  </div>

  <template id="cardTemplate">
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm p-5 flex flex-col">
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="text-2xl" data-icon>📦</div>
          <div>
            <h2 class="text-lg font-semibold" data-name>App Name</h2>
            <div class="text-xs text-slate-500 mt-0.5" data-meta>Category · Type</div>
          </div>
        </div>
        <button title="Toggle favorite" class="favoriteBtn text-xl" aria-pressed="false">☆</button>
      </div>
      <p class="text-slate-600 mt-3 text-sm" data-description></p>

      <div class="mt-4 flex items-center gap-2">
        <button class="runBtn px-3 py-2 rounded-xl bg-blue-600 text-white text-sm hover:bg-blue-700">Run</button>
        <a class="openBtn px-3 py-2 rounded-xl border border-slate-300 text-sm hidden" target="_blank">Open</a>
        <span class="inline-flex items-center text-xs px-2 py-1 rounded-full bg-slate-100 border border-slate-200" data-type>type</span>
      </div>

      <div class="mt-4 hidden" data-resultWrap>
        <div class="text-xs text-slate-500 mb-1">Last result</div>
        <pre class="bg-slate-50 p-3 rounded-xl border border-slate-200 overflow-auto thin-scrollbar text-xs max-h-48" data-result>(no output yet)</pre>
      </div>
    </div>
  </template>

  <script>
    // ==========================
    // 1) Configure your apps here
    // ==========================
    const apps = [
      {
        id: "statusPanel",
        name: "Waiting Queue",
        description: "Open the queue dashboard.",
        icon: "📊",
        category: "API - Requests",
        type: "url",
        url: "/workspaces/didactic-waddle/scripts/web-applicationv2"
      },
      {
        id: "docs",
        name: "Docs Portal",
        description: "Internal docs site.",
        icon: "📚",
        category: "Knowledge",
        type: "url",
        url: "https://example.com/docs"
      },
      {
        id: "syncJob",
        name: "Sync Job Trigger",
        description: "POST to start nightly sync (idempotent).",
        icon: "🔁",
        category: "Jobs",
        type: "endpoint",
        method: "POST",
        url: "https://api.example.com/jobs/sync",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer {{token}}" },
        body: { "force": true }
      },
      {
        id: "rebuildIndex",
        name: "Rebuild Search Index",
        description: "GET endpoint to kick off a reindex.",
        icon: "🧰",
        category: "Maintenance",
        type: "endpoint",
        method: "GET",
        url: "https://api.example.com/admin/reindex",
        headers: { "Authorization": "Bearer {{token}}" }
      }
    ];

    // ==========================
    // 2) State & helpers
    // ==========================
    const appsGrid = document.getElementById('appsGrid');
    const cardTemplate = document.getElementById('cardTemplate');
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const showFavoritesOnly = document.getElementById('showFavoritesOnly');
    const authTokenInput = document.getElementById('authToken');
    const saveTokenBtn = document.getElementById('saveTokenBtn');

    const FAVORITES_KEY = 'appLauncherFavorites';
    const TOKEN_KEY = 'appLauncherAuthToken';

    const getFavorites = () => new Set(JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'));
    const setFavorites = (set) => localStorage.setItem(FAVORITES_KEY, JSON.stringify([...set]));

    const getToken = () => localStorage.getItem(TOKEN_KEY) || '';
    const setToken = (val) => localStorage.setItem(TOKEN_KEY, val || '');

    function interpolateHeaders(headers, token) {
      if (!headers) return {};
      const out = {};
      for (const [k, v] of Object.entries(headers)) {
        out[k] = String(v).replaceAll('{{token}}', token);
      }
      return out;
    }

    function matchesFilter(app, q, cat, favOnly, favs) {
      const text = (app.name + ' ' + (app.description||'') + ' ' + (app.category||'') + ' ' + app.type).toLowerCase();
      const okText = !q || text.includes(q.toLowerCase());
      const okCat  = !cat || (app.category || '') === cat;
      const okFav  = !favOnly || favs.has(app.id);
      return okText && okCat && okFav;
    }

    function renderCategoryOptions() {
      const cats = [...new Set(apps.map(a => a.category).filter(Boolean))].sort();
      for (const c of cats) {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        categoryFilter.appendChild(opt);
      }
    }

    function renderGrid() {
      const q = searchInput.value.trim();
      const cat = categoryFilter.value;
      const favOnly = showFavoritesOnly.checked;
      const favs = getFavorites();

      appsGrid.innerHTML = '';
      const filtered = apps.filter(a => matchesFilter(a, q, cat, favOnly, favs));

      for (const app of filtered) {
        const node = cardTemplate.content.firstElementChild.cloneNode(true);
        node.querySelector('[data-icon]').textContent = app.icon || '📦';
        node.querySelector('[data-name]').textContent = app.name;
        node.querySelector('[data-description]').textContent = app.description || '';
        node.querySelector('[data-meta]').textContent = `${app.category || 'General'} · ${app.type}`;
        node.querySelector('[data-type]').textContent = app.type;

        // Favorite state
        const favBtn = node.querySelector('.favoriteBtn');
        const favsNow = getFavorites();
        const isFav = favsNow.has(app.id);
        favBtn.textContent = isFav ? '★' : '☆';
        favBtn.setAttribute('aria-pressed', isFav ? 'true' : 'false');
        favBtn.addEventListener('click', () => {
          const set = getFavorites();
          if (set.has(app.id)) set.delete(app.id); else set.add(app.id);
          setFavorites(set);
          renderGrid();
        });

        // Buttons
        const runBtn = node.querySelector('.runBtn');
        const openBtn = node.querySelector('.openBtn');
        const resultWrap = node.querySelector('[data-resultWrap]');
        const resultPre = node.querySelector('[data-result]');

        if (app.type === 'url') {
          openBtn.classList.remove('hidden');
          openBtn.href = app.url;
          openBtn.textContent = 'Open in new tab';
          runBtn.textContent = 'Copy link';
          runBtn.addEventListener('click', async () => {
            try {
              await navigator.clipboard.writeText(app.url);
              runBtn.textContent = 'Copied!';
              setTimeout(() => runBtn.textContent = 'Copy link', 1200);
            } catch {
              alert(app.url);
            }
          });
        } else if (app.type === 'endpoint') {
          runBtn.addEventListener('click', async () => {
            const token = getToken();
            const headers = interpolateHeaders(app.headers, token);
            const method = (app.method || 'POST').toUpperCase();
            const init = { method, headers: headers || {} };
            if (method !== 'GET' && app.body !== undefined) {
              if (!init.headers['Content-Type']) init.headers['Content-Type'] = 'application/json';
              init.body = JSON.stringify(app.body);
            }

            resultWrap.classList.remove('hidden');
            resultPre.textContent = 'Running…';

            let resText = '';
            try {
              const res = await fetch(app.url, init);
              const ct = res.headers.get('content-type') || '';
              if (ct.includes('application/json')) {
                const data = await res.json();
                resText = JSON.stringify(data, null, 2);
              } else {
                resText = await res.text();
              }
              resultPre.textContent = `HTTP ${res.status} ${res.statusText}\n\n` + resText;
            } catch (err) {
              resultPre.textContent = 'Request failed: ' + err;
            }
          });
        }

        appsGrid.appendChild(node);
      }

      if (filtered.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'text-slate-600 text-sm';
        empty.textContent = 'No apps match your filters.';
        appsGrid.appendChild(empty);
      }
    }

    // ==========================
    // 3) Boot
    // ==========================
    function boot() {
      // Restore token
      authTokenInput.value = getToken();
      saveTokenBtn.addEventListener('click', () => {
        setToken(authTokenInput.value.trim());
        saveTokenBtn.textContent = 'Saved';
        setTimeout(() => saveTokenBtn.textContent = 'Save', 1000);
      });

      // Wire filters
      searchInput.addEventListener('input', renderGrid);
      categoryFilter.addEventListener('change', renderGrid);
      showFavoritesOnly.addEventListener('change', renderGrid);

      renderCategoryOptions();
      renderGrid();
    }

    document.addEventListener('DOMContentLoaded', boot);
  </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
