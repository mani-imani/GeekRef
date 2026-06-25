/* ═══════════════════════════════════
   GeekRef — Shared JS  (gr.js)
   ═══════════════════════════════════ */

/* ── 1. THEME ── */
function grToggleTheme() {
  var html = document.documentElement;
  var isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) {
    html.removeAttribute('data-theme');
    localStorage.setItem('gr-theme', 'dark');
  } else {
    html.setAttribute('data-theme', 'light');
    localStorage.setItem('gr-theme', 'light');
  }
  grSyncIcons();
}

function grSyncIcons() {
  var isLight = document.documentElement.getAttribute('data-theme') === 'light';
  document.querySelectorAll('.gr-toggle').forEach(function(b) {
    b.textContent = isLight ? '🌙' : '☀️';
  });
}

document.addEventListener('DOMContentLoaded', grSyncIcons);

/* ── 2. COPY CODE BLOCK ── */
function grCopyCode(btn) {
  var pre = btn.closest('.gr-code').querySelector('pre');
  var text = pre.innerText;
  navigator.clipboard.writeText(text).then(function() {
    btn.textContent = '✓ کپی شد';
    btn.classList.add('copied');
    setTimeout(function() { btn.textContent = 'کپی'; btn.classList.remove('copied'); }, 2000);
  });
}

/* ── 3. COPY INLINE CMD ── */
function grCopyCmd(text, el) {
  navigator.clipboard.writeText(text).then(function() {
    var tag = el.querySelector('.gr-copied-tag') ||
              (el.parentElement && el.parentElement.querySelector('.gr-copied-tag'));
    if (tag) { tag.classList.add('show'); setTimeout(function() { tag.classList.remove('show'); }, 1200); }
  });
}

/* ── 4. GLOBAL SEARCH (Ctrl+K / Cmd+K) ── */
var grSearchIndex = null;
var grSearchOpen  = false;

function grLoadIndex(cb) {
  if (grSearchIndex) { cb(); return; }
  // figure out root path (works from / and /cheatsheets/)
  var isSheet = window.location.pathname.includes('/cheatsheets/');
  var base = isSheet ? '../' : './';
  fetch(base + 'assets/search-index.json')
    .then(function(r) { return r.json(); })
    .then(function(data) { grSearchIndex = data; cb(); })
    .catch(function() { grSearchIndex = []; cb(); });
}

function grOpenSearch() {
  grLoadIndex(function() {
    document.getElementById('gr-search-overlay').classList.add('open');
    document.getElementById('gr-search-input').value = '';
    document.getElementById('gr-search-results').innerHTML = '<div class="gr-sr-hint">شروع به تایپ کنید...</div>';
    document.getElementById('gr-search-input').focus();
    grSearchOpen = true;
  });
}

function grCloseSearch() {
  document.getElementById('gr-search-overlay').classList.remove('open');
  grSearchOpen = false;
}

function grDoSearch(q) {
  q = q.trim().toLowerCase();
  var results = document.getElementById('gr-search-results');
  if (!q) {
    results.innerHTML = '<div class="gr-sr-hint">شروع به تایپ کنید...</div>';
    return;
  }
  var isSheet = window.location.pathname.includes('/cheatsheets/');
  var base = isSheet ? '../cheatsheets/' : 'cheatsheets/';
  var hits = grSearchIndex.filter(function(e) {
    return e.cmd.toLowerCase().includes(q) || e.desc.toLowerCase().includes(q) || e.title.toLowerCase().includes(q);
  }).slice(0, 12);

  if (!hits.length) {
    results.innerHTML = '<div class="gr-sr-hint">نتیجه‌ای پیدا نشد 🔍</div>';
    return;
  }

  results.innerHTML = hits.map(function(e) {
    var hl = function(str) {
      var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + ')', 'gi');
      return str.replace(re, '<mark>$1</mark>');
    };
    return '<a class="gr-sr-item" href="' + base + e.file + '" onclick="grCloseSearch()">' +
      '<span class="gr-sr-icon">' + e.icon + '</span>' +
      '<span class="gr-sr-body">' +
        '<span class="gr-sr-cmd" style="color:' + e.accent + '">' + hl(e.cmd) + '</span>' +
        (e.desc ? '<span class="gr-sr-desc">' + hl(e.desc) + '</span>' : '') +
      '</span>' +
      '<span class="gr-sr-source">' + e.title + '</span>' +
    '</a>';
  }).join('');
}

/* keyboard nav */
document.addEventListener('keydown', function(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    grSearchOpen ? grCloseSearch() : grOpenSearch();
  }
  if (e.key === 'Escape' && grSearchOpen) grCloseSearch();
});

/* ── 5. INJECT SEARCH OVERLAY + TRIGGER (runs after DOM) ── */
document.addEventListener('DOMContentLoaded', function() {
  /* overlay */
  var overlay = document.createElement('div');
  overlay.id = 'gr-search-overlay';
  overlay.innerHTML =
    '<div class="gr-search-modal" id="gr-search-modal">' +
      '<div class="gr-search-top">' +
        '<span class="gr-search-icon-wrap">🔍</span>' +
        '<input id="gr-search-input" type="text" placeholder="جستجو در ۲۸۰+ دستور..." autocomplete="off" oninput="grDoSearch(this.value)">' +
        '<kbd onclick="grCloseSearch()">Esc</kbd>' +
      '</div>' +
      '<div id="gr-search-results"><div class="gr-sr-hint">شروع به تایپ کنید...</div></div>' +
      '<div class="gr-search-footer">' +
        '<span><kbd>↑↓</kbd> ناوبری</span>' +
        '<span><kbd>Enter</kbd> باز کردن</span>' +
        '<span><kbd>Esc</kbd> بستن</span>' +
        '<span><kbd>Ctrl K</kbd> باز/بسته</span>' +
      '</div>' +
    '</div>';
  overlay.addEventListener('click', function(e) { if (e.target === overlay) grCloseSearch(); });
  document.body.appendChild(overlay);

  /* inject search trigger into every navbar */
  document.querySelectorAll('.gr-navbar-right, .gr-navbar').forEach(function(nav) {
    if (nav.querySelector('.gr-search-trigger')) return;
    var btn = document.createElement('button');
    btn.className = 'gr-search-trigger';
    btn.setAttribute('onclick', 'grOpenSearch()');
    btn.title = 'جستجو (Ctrl+K)';
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg> <span>جستجو</span> <kbd>⌃K</kbd>';
    var right = nav.querySelector('.gr-navbar-right');
    if (right) right.insertBefore(btn, right.firstChild);
    else nav.appendChild(btn);
  });
});

/* ── PROGRESS BAR ── */
(function() {
  var bar = document.createElement('div');
  bar.className = 'gr-progress';
  document.body.insertBefore(bar, document.body.firstChild);
  window.addEventListener('scroll', function() {
    var s = document.documentElement;
    var pct = (s.scrollTop / (s.scrollHeight - s.clientHeight)) * 100;
    bar.style.width = Math.min(pct, 100) + '%';
  }, { passive: true });
})();

/* ── SIDEBAR ACTIVE STATE ── */
function grInitSidebar() {
  var items = document.querySelectorAll('.gr-sidebar-item');
  if (!items.length) return;
  var sections = Array.from(items).map(function(item) {
    var id = item.getAttribute('href').replace('#','');
    return document.getElementById(id);
  }).filter(Boolean);

  var onScroll = function() {
    var scrollY = window.scrollY + 120;
    var active = sections[0];
    sections.forEach(function(s) { if (s.offsetTop <= scrollY) active = s; });
    items.forEach(function(item) {
      item.classList.toggle('active', item.getAttribute('href') === '#' + active.id);
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

document.addEventListener('DOMContentLoaded', grInitSidebar);
