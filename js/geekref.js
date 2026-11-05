/* ============================================================================
   geekref.js — GeekRef v2.1.0 (was css/gr.js in v1)
   1 Icons   2 Theme (System / Light / Dark)   3 Copy (commands, code, links)
   4 Search (Ctrl/Cmd+K or /)   5 Deep links (#c-…)   6 Table of contents
   7 Offline (service worker)
   Command counts are written by tools/build.py, not at runtime.
   No dependencies. Works from / and /cheatsheets/.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document, root = doc.documentElement;
  var IN_SHEET = /\/cheatsheets\//.test(location.pathname);
  var BASE = IN_SHEET ? '../' : './';
  var IS_MAC = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  var FA_DIGITS = '۰۱۲۳۴۵۶۷۸۹';
  function fa(n) { return String(n).replace(/\d/g, function (d) { return FA_DIGITS[d]; }); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* ── 1. Icons (Bootstrap Icons, MIT; source files in assets/icons/bootstrap/) ── */
  var ICONS = {
    copy:   '<path fill-rule="evenodd" d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1z"/>',
    check:  '<path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0"/>',
    search: '<path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>',
    close:  '<path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>'
  };
  function icon(name) { return '<svg class="gr-ic" viewBox="0 0 16 16" aria-hidden="true" focusable="false">' + ICONS[name] + '</svg>'; }

  /* screen-reader announcements */
  var live;
  function announce(msg) {
    if (!live) { live = doc.createElement('p'); live.className = 'gr-vh'; live.setAttribute('aria-live', 'polite'); doc.body.appendChild(live); }
    live.textContent = ''; setTimeout(function () { live.textContent = msg; }, 30);
  }

  /* ── 2. Theme: system (default) / light / dark. Key "gr-theme" kept from v1. ── */
  function readTheme() { try { return localStorage.getItem('gr-theme') || 'system'; } catch (e) { return 'system'; } }
  function setTheme(mode) {
    if (mode === 'light' || mode === 'dark') root.setAttribute('data-theme', mode);
    else { root.removeAttribute('data-theme'); mode = 'system'; }
    try { localStorage.setItem('gr-theme', mode); } catch (e) {}
    doc.querySelectorAll('[data-theme-set]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-theme-set') === mode));
    });
  }
  window.grSetTheme = setTheme;

  /* ── 3. Copy ── */
  function writeClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (ok, fail) {          // fallback for old browsers / plain http
      var t = doc.createElement('textarea');
      t.value = text; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0';
      doc.body.appendChild(t); t.select();
      try { doc.execCommand('copy') ? ok() : fail(); } catch (e) { fail(e); }
      t.remove();
    });
  }
  function flash(btn, labelEl) {
    var ic = btn.querySelector('.gr-ic');
    var before = ic ? ic.innerHTML : null, label = labelEl ? labelEl.textContent : null;
    btn.classList.add('is-copied');
    if (ic) ic.innerHTML = ICONS.check;
    if (labelEl) labelEl.textContent = 'کپی شد';
    announce('کپی شد');
    clearTimeout(btn._grT);
    btn._grT = setTimeout(function () {
      btn.classList.remove('is-copied');
      if (ic) ic.innerHTML = before;
      if (labelEl) labelEl.textContent = label;
    }, 1600);
  }
  /* kept for compatibility with v1 markup */
  window.grCopyCmd = function (text, el) { writeClipboard(text).then(function () { flash(el.closest('button') || el); }); };
  window.grCopyCode = function (btn) {
    var pre = btn.closest('.gr-code').querySelector('pre');
    writeClipboard(pre.innerText).then(function () { flash(btn, btn.querySelector('span')); });
  };
  function linkTo(id) { return location.origin + location.pathname + '#' + id; }
  doc.addEventListener('click', function (e) {
    var l = e.target.closest('[data-link]');
    if (l) {
      var id = l.getAttribute('data-link');
      writeClipboard(linkTo(id)).then(function () {
        try { history.replaceState(null, '', '#' + id); } catch (err) {}
        flash(l); announce('پیوند کپی شد');
      });
      return;
    }
    var b = e.target.closest('[data-copy]');
    if (b) { window.grCopyCmd(b.getAttribute('data-copy'), b); return; }
    var c = e.target.closest('[data-copy-code]');
    if (c) window.grCopyCode(c);
  });

  /* ── 4. Search ── */
  var index = null, dlg, input, list, hits = [], active = -1, opener = null;

  function loadIndex() {
    if (index) return Promise.resolve(index);
    return fetch(BASE + 'assets/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { index = d; return d; })
      .catch(function () { index = []; return index; });
  }

  function buildDialog() {
    dlg = doc.createElement('dialog');
    dlg.className = 'gr-search';
    dlg.setAttribute('aria-label', 'جست‌وجو در دستورها');
    dlg.innerHTML =
      '<div class="gr-search-top">' + icon('search') +
        '<input id="gr-search-input" type="search" role="combobox" aria-expanded="false" aria-controls="gr-search-results"' +
        ' aria-autocomplete="list" aria-label="جست‌وجو در دستورها" placeholder="نام دستور یا توضیح آن را بنویسید" autocomplete="off" spellcheck="false" enterkeyhint="go">' +
        '<button type="button" class="gr-icon-btn" data-close aria-label="بستن جست‌وجو">' + icon('close') + '</button>' +
      '</div>' +
      '<div id="gr-search-results" role="listbox" aria-label="نتیجه‌ها"></div>' +
      '<div class="gr-search-foot" aria-hidden="true">' +
        '<span><kbd>↑</kbd><kbd>↓</kbd> جابه‌جایی</span>' +
        '<span><kbd>Enter</kbd> باز کردن</span>' +
        '<span><kbd>Esc</kbd> بستن</span>' +
        '<span><kbd>/</kbd> یا <kbd>Ctrl K</kbd> باز کردن</span>' +
      '</div>';
    doc.body.appendChild(dlg);
    input = dlg.querySelector('#gr-search-input');
    list = dlg.querySelector('#gr-search-results');

    input.addEventListener('input', function () { render(input.value); });
    input.addEventListener('keydown', onKeys);
    dlg.querySelector('[data-close]').addEventListener('click', closeSearch);
    dlg.addEventListener('click', function (e) { if (e.target === dlg) closeSearch(); });   // click on backdrop
    dlg.addEventListener('close', function () { if (opener && opener.focus) opener.focus(); });
    list.addEventListener('click', function (e) {
      if (e.target.closest('.gr-sr-item')) { opener = null; closeSearch(); }   // the page (or hash) takes over
    });
    list.addEventListener('mousemove', function (e) {
      var a = e.target.closest('.gr-sr-item'); if (a) select(+a.dataset.i, false);
    });
  }

  function norm(t) {
    return String(t || '').toLowerCase()
      .replace(/[۰-۹]/g, function (d) { return String(d.charCodeAt(0) - 0x06F0); })
      .replace(/[٠-٩]/g, function (d) { return String(d.charCodeAt(0) - 0x0660); })
      .replace(/ي/g, 'ی').replace(/ك/g, 'ک')
      .replace(/[\u200c\s]+/g, ' ').trim();
  }

  function hint(text) { list.innerHTML = '<p class="gr-sr-hint">' + text + '</p>'; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); }

  function render(raw) {
    if (!index) return;                              // still loading; loadIndex() renders when ready
    var q = norm(raw);
    hits = []; active = -1;
    if (!q) { hint('برای نمونه بنویسید <bdi>git push</bdi> یا «مجوز فایل»'); return; }
    /* rank: command starts with the query > a word of the command does > command contains it > description/sheet;
       ties: this page's sheet first, then the original order */
    var words = q.split(' '), here = (location.pathname.match(/[^\/]+\.html$/) || [''])[0], scored = [];
    index.forEach(function (e, n) {
      var c = e._c || (e._c = norm(e.cmd)), d = e._d || (e._d = norm(e.desc + ' ' + e.title)), score = 0;
      if (c.indexOf(q) === 0) score = 4;
      else if ((' ' + c).indexOf(' ' + q) > -1) score = 3;
      else if (c.indexOf(q) > -1) score = 2;
      else if (d.indexOf(q) > -1) score = 1;
      else if (words.every(function (w) { return (c + ' ' + d).indexOf(w) > -1; })) score = 1;   // every word, any order
      if (score) scored.push({ e: e, s: score * 2 + (e.file === here ? 1 : 0), n: n });
    });
    scored.sort(function (a, b) { return b.s - a.s || a.n - b.n; });
    hits = scored.slice(0, 12).map(function (x) { return x.e; });
    if (!hits.length) { hint('نتیجه‌ای پیدا نشد. واژه‌ی کوتاه‌تری را امتحان کنید.'); announce('نتیجه‌ای پیدا نشد'); return; }

    var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    function hl(s) { return esc(s).replace(re, '<mark>$1</mark>'); }   // escape first: commands contain < >
    var sheetBase = IN_SHEET ? '' : 'cheatsheets/';
    list.innerHTML = hits.map(function (e, i) {
      return '<a class="gr-sr-item" id="gr-opt-' + i + '" data-i="' + i + '" role="option" aria-selected="false" href="' + sheetBase + esc(e.file) + (e.id ? '#' + esc(e.id) : '') + '">' +
        '<span class="gr-sr-body">' +
          '<code class="gr-sr-cmd" dir="ltr">' + hl(e.cmd) + '</code>' +
          (e.desc ? '<span class="gr-sr-desc">' + hl(e.desc) + '</span>' : '') +
        '</span>' +
        '<span class="gm-chip">' + esc(e.title) + '</span>' +
      '</a>';
    }).join('');
    input.setAttribute('aria-expanded', 'true');
    announce(fa(hits.length) + ' نتیجه');
    select(0, false);
  }

  function select(i, scroll) {
    if (!hits.length) return;
    active = (i + hits.length) % hits.length;
    list.querySelectorAll('.gr-sr-item').forEach(function (a, n) { a.setAttribute('aria-selected', String(n === active)); });
    var el = doc.getElementById('gr-opt-' + active);
    input.setAttribute('aria-activedescendant', el.id);
    if (scroll !== false) el.scrollIntoView({ block: 'nearest' });
  }

  function onKeys(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); select(active + 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); select(active - 1); }
    else if (e.key === 'Enter' && active > -1) { e.preventDefault(); doc.getElementById('gr-opt-' + active).click(); }
    else if (e.key === 'Escape') { e.preventDefault(); closeSearch(); }   // type=search would only clear the field
  }

  function openSearch() {
    if (!dlg) buildDialog();
    opener = doc.activeElement;
    input.value = '';
    hint('در حال آماده‌سازی…');
    if (!dlg.open) dlg.showModal();
    input.focus();                                   // open at once so no keystroke is lost
    loadIndex().then(function () { render(input.value); });
  }
  function closeSearch() { if (dlg && dlg.open) dlg.close(); }
  window.grOpenSearch = openSearch;
  window.grCloseSearch = closeSearch;

  function typing(el) { return el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)); }
  doc.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault();
      dlg && dlg.open ? closeSearch() : openSearch();
    } else if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey && !typing(doc.activeElement) && !(dlg && dlg.open)) {
      e.preventDefault();
      openSearch();
    }
  });

  /* ── 5. Deep links: CSS :target highlights the row; here we move keyboard focus to it ── */
  function focusTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!/^c-/.test(id)) return;
    var el = doc.getElementById(id);
    if (!el) return;
    if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
    el.focus({ preventScroll: true });              // the browser already scrolled to the hash
  }
  window.addEventListener('hashchange', focusTarget);

  /* ── 6. Table of contents: mark the section in view, close the mobile list on pick ── */
  function initToc() {
    var links = doc.querySelectorAll('.gr-toc a[href^="#"]');
    if (!links.length) return;
    var sections = Array.prototype.map.call(links, function (a) { return doc.getElementById(a.getAttribute('href').slice(1)); }).filter(Boolean);
    function onScroll() {
      var y = window.scrollY + 120, cur = sections[0];
      sections.forEach(function (s) { if (s.offsetTop <= y) cur = s; });
      links.forEach(function (a) {
        if (a.getAttribute('href') === '#' + cur.id) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    doc.querySelectorAll('.gr-toc-m a').forEach(function (a) {
      a.addEventListener('click', function () { var d = a.closest('details'); if (d) d.open = false; });
    });
  }

  /* ── 7. Offline: register the service worker (http/https only) ── */
  function initOffline() {
    if (!('serviceWorker' in navigator) || !/^https?:$/.test(location.protocol)) return;
    navigator.serviceWorker.register(BASE + 'sw.js').then(function (reg) {
      return navigator.serviceWorker.ready;
    }).then(function () {
      doc.querySelectorAll('.gr-offline').forEach(function (el) { el.hidden = false; });
    }).catch(function () {});
  }

  /* ── boot ── */
  function boot() {
    setTheme(readTheme());
    doc.querySelectorAll('[data-theme-set]').forEach(function (b) {
      b.addEventListener('click', function () { setTheme(b.getAttribute('data-theme-set')); });
    });
    doc.querySelectorAll('[data-gr-search]').forEach(function (b) { b.addEventListener('click', openSearch); });
    if (IS_MAC) doc.querySelectorAll('[data-gr-kbd]').forEach(function (k) { k.textContent = '⌘ K'; });
    initToc();
    focusTarget();
    initOffline();
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot); else boot();
})();
