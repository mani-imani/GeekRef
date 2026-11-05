#!/usr/bin/env python3
"""
GeekRef build · v2.2.0
Single source of truth: data/sheets/*.json  ->  index.html, cheatsheets/*.html,
assets/search-index.json, sw.js (offline file list), manifest.webmanifest.

    python3 tools/build.py          # build
    python3 tools/build.py --check  # validate data only, write nothing

Python 3.8+, standard library only. Never edit the generated files by hand.

Text in the JSON is plain Persian. The build applies the brand rules (brand.md §5.3):
Latin runs inside Persian -> <bdi>, Persian digits outside Latin runs and code,
Persian ی/ک, common missing ZWNJ fixed. Tiny markup: **bold** and `code`.
"""
import glob, hashlib, html as H, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = '2.2.0'
SITE = 'https://mani-imani.github.io/GeekRef/'
REPO = 'https://github.com/mani-imani/GeekRef'
ZW = '‌'
FA = '؀-ۿ'
FA_D = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ERRORS = []


# ───────────────────────────── text rules ─────────────────────────────
EMOJI = re.compile('[' + ''.join(chr(a) + '-' + chr(b) for a, b in ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF), (0x231A, 0x23FF), (0xFE0F, 0xFE0F), (0x2705, 0x2705))) + ']')   # emoji ranges, written as code points so this file holds none
TOK = r"[A-Za-z0-9_.\-/+#@:*~$=&|<>\[\]{}()'\"`!?%^\\]+"
LATIN_RUN = re.compile(TOK + r'(?: ' + TOK + r')*')
ZW_RULES = [
    (re.compile(r'(?<![' + FA + r'])(ن?می) (?=[' + FA + r'])'), r'\1' + ZW),
    (re.compile(r'([' + FA + r']) (ها|های|هایی|هایت|هایش|هایمان)(?![' + FA + r'])'), r'\1' + ZW + r'\2'),
    (re.compile(r'([' + FA + r']) (تر|ترین)(?![' + FA + r'])'), r'\1' + ZW + r'\2'),
]

def fix_persian(s):
    s = s.replace('ي', 'ی').replace('ك', 'ک')
    for rx, rep in ZW_RULES:
        s = rx.sub(rep, s)
    return s

def _trim_run(run):
    lead = trail = ''
    while run and run[-1] in '.,:;!? ':
        trail = run[-1] + trail; run = run[:-1]
    while run and run[0] in '.,:;!? ':
        lead += run[0]; run = run[1:]
    changed = True
    while changed and run:
        changed = False
        for o, c in (('(', ')'), ('[', ']'), ('{', '}')):
            if run.startswith(o) and c not in run[1:]: lead += o; run = run[1:]; changed = True
            if run.endswith(c) and o not in run[:-1]: trail = c + trail; run = run[:-1]; changed = True
        for q in '"\'':
            if run.startswith(q) and run.count(q) == 1: lead += q; run = run[1:]; changed = True
            if run.endswith(q) and run.count(q) == 1: trail = q + trail; run = run[:-1]; changed = True
    # an opener at the end or a closer at the start belongs to the Persian side
    while run and (run[-1] in '([{ ' or run[0] in ')]} '):
        if run[-1] in '([{ ': trail = run[-1] + trail; run = run[:-1]
        elif run[0] in ')]} ': lead += run[0]; run = run[1:]
    return lead, run, trail

def _segments(text, digits=True):
    """Split Persian text into (kind, str) parts: ('fa', …) and ('latin', …). Persian digits only in 'fa' parts."""
    text = fix_persian(text)
    out, pos = [], 0
    for m in LATIN_RUN.finditer(text):
        lead, run, trail = _trim_run(m.group(0))
        if not re.search('[A-Za-z]', run):
            continue
        out.append(('fa', text[pos:m.start()] + lead))
        out.append(('latin', run))
        pos = m.end() - len(trail)
    out.append(('fa', text[pos:]))
    return [(k, v.translate(FA_D) if k == 'fa' and digits else v) for k, v in out if v]

def fa_text(text, digits=True):
    """Plain Persian text (no markup) -> HTML. digits=False keeps 0-9 (used for comments inside code)."""
    return ''.join('<bdi>' + H.escape(v, quote=False) + '</bdi>' if k == 'latin' else H.escape(v, quote=False)
                   for k, v in _segments(text, digits))

def fa_plain(text, digits=True):
    """Same rules as fa_text, as plain text (search index): no 'python۳' or 'base۶۴'."""
    return ''.join(v for _, v in _segments(text, digits))

def rich(text):
    """Text with **bold** and `code` -> HTML."""
    out = []
    for part in re.split(r'(`[^`]+`|\*\*[^*]+\*\*)', text or ''):
        if not part:
            continue
        if part.startswith('`'):
            out.append('<code dir="ltr">' + H.escape(part[1:-1], quote=False) + '</code>')
        elif part.startswith('**'):
            inner = part[2:-2]
            if re.search('[A-Za-z]', inner) and not re.search('[' + FA + ']', inner):
                out.append('<strong><bdi>' + H.escape(inner, quote=False) + '</bdi></strong>')
            else:
                out.append('<strong>' + fa_text(inner) + '</strong>')
        else:
            out.append(fa_text(part))
    return ''.join(out).strip()

def plain(text):
    return re.sub(r'\*\*|`', '', text or '')

def fa_num(n):
    return str(n).translate(FA_D)


# ───────────────────────────── icons ─────────────────────────────
_ICON_CACHE = {}
def icon(name):
    if name not in _ICON_CACHE:
        svg = open(os.path.join(ROOT, 'assets/icons/bootstrap', name + '.svg'), encoding='utf-8').read()
        inner = re.sub(r'\s*\n\s*', '', re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1).strip())
        _ICON_CACHE[name] = f'<svg class="gr-ic" viewBox="0 0 16 16" aria-hidden="true" focusable="false">{inner}</svg>'
    return _ICON_CACHE[name]


# ───────────────────────────── anchors ─────────────────────────────
class Anchors:
    """Stable, unique ids for every command on a page: c-<slug>."""
    def __init__(self, reserved=()):
        self.used = set(reserved)
    def make(self, cmd):
        base = 'c-' + (re.sub(r'[^a-z0-9]+', '-', cmd.lower()).strip('-')[:48].strip('-') or 'cmd')
        aid, n = base, 2
        while aid in self.used:
            aid = f'{base}-{n}'; n += 1
        self.used.add(aid)
        return aid


# ───────────────────────────── code blocks ─────────────────────────────
SHELL = set('sudo apt apt-get python python3 pip pip3 django-admin cd find source deactivate gunicorn git curl wget '
            'ls mkdir rm cp mv cat echo export chmod chown systemctl nginx pyenv uv black flake8 pytest code tree '
            'touch ssh scp tar head grep'.split())

def is_command(line, lang):
    s = line.strip()
    if not s or s.startswith('#') or re.match(r'https?://', s):
        return False
    if lang == 'bash':
        return True                      # pure shell block: every non-comment line is a command
    if lang.split()[0] == 'python':
        return False                     # python / settings.py: not indexed
    return s.split()[0] in SHELL         # mixed "bash / python": only lines that start with a shell program

def highlight(cmd):
    """Navy for the program (and its subcommand for sudo/manage.py), plain for the rest."""
    parts = re.split(r'(\s*(?:&&|\|\||\||;)\s*)', cmd)
    out = []
    for p in parts:
        if re.fullmatch(r'\s*(?:&&|\|\||\||;)\s*', p or ''):
            out.append(H.escape(p, quote=False)); continue
        toks = p.split(' ')
        n = 1
        if toks and toks[0] == 'sudo' and len(toks) > 1: n = 2
        if len(toks) > 2 and toks[0] in ('python', 'python3') and toks[1] == 'manage.py': n = 3
        if len(toks) > 1 and toks[0] in ('pip', 'pip3', 'git', 'django-admin', 'apt', 'systemctl') and not toks[1].startswith('-'): n = 2
        head, rest = ' '.join(toks[:n]), ' '.join(toks[n:])
        out.append(f'<span class="fn">{H.escape(head, quote=False)}</span>' + ((' ' + H.escape(rest, quote=False)) if rest else ''))
    return ''.join(out)

def render_code(block, anchors, entries, sheet):
    lang = block['lang']
    lines, note = [], ''
    for raw in block['code'].split('\n'):
        s = raw.strip()
        if s.startswith('#'):
            note = s.lstrip('#').strip()
            lines.append(f'<span class="lc"># {fa_text(note, digits=False)}</span>')   # code: digits stay as written
        elif is_command(raw, lang):
            aid = anchors.make(s)
            lines.append(f'<span class="gr-line" id="{aid}">{highlight(raw)}</span>')
            entries.append({'cmd': s, 'desc': note, 'id': aid, 'code': True})
        else:
            lines.append(H.escape(raw, quote=False))
    return (f'  <div class="gr-code">\n   <div class="gr-code-head"><span class="gr-code-lang">{H.escape(lang)}</span>'
            f'<button type="button" class="gr-copy-btn" data-copy-code aria-label="کپی همه‌ی کد این بخش">{icon("copy")}<span>کپی</span></button></div>\n'
            f'   <pre tabindex="0" aria-label="کد {H.escape(lang)}">' + '\n'.join(lines) + '</pre>\n  </div>\n')


# ───────────────────────────── command pieces ─────────────────────────────
def cmd_button(cmd, copy=None, inner=None):
    copy = cmd if copy is None else copy
    body = inner if inner is not None else f'<code dir="ltr">{H.escape(cmd, quote=False)}</code>{icon("copy")}'
    return (f'<button type="button" class="gr-cmd" data-copy="{H.escape(copy)}" aria-label="کپی دستور {H.escape(cmd)}">{body}</button>')

def link_button(aid, cmd):
    return f'<button type="button" class="gr-link-btn" data-link="{aid}" aria-label="کپی پیوند دستور {H.escape(cmd)}" title="کپی پیوند">{icon("link-45deg")}</button>'

def render_rows(block, anchors, entries):
    rows = []
    for it in block['items']:
        aid = anchors.make(it['cmd'])
        entries.append({'cmd': it['cmd'], 'desc': plain(it.get('desc', '')), 'id': aid})
        rows.append(f'   <div class="gr-row" id="{aid}">{cmd_button(it["cmd"], it.get("copy"))}'
                    f'<p class="gr-cmd-desc">{rich(it.get("desc", ""))}</p>{link_button(aid, it["cmd"])}</div>')
    return '  <div class="gr-table">\n' + '\n'.join(rows) + '\n  </div>\n'

def render_combo(block, anchors, entries):
    rows = []
    for it in block['items']:
        aid = anchors.make(it['cmd'])
        entries.append({'cmd': it['cmd'], 'desc': it['note'], 'id': aid})
        inner = (f'<span class="gr-combo-note">{fa_text(it["note"])}</span>'
                 f'<span class="gr-combo-line"><code dir="ltr">{H.escape(it["cmd"], quote=False)}</code>{icon("copy")}</span>')
        rows.append(f'   <div class="gr-combo-item" id="{aid}">{cmd_button(it["cmd"], None, inner)}{link_button(aid, it["cmd"])}</div>')
    return '  <div class="gr-table gr-combo">\n' + '\n'.join(rows) + '\n  </div>\n'

def render_packages(block):
    rows = [f'   <div class="gr-row gr-row--plain"><code class="gr-codechip" dir="ltr">{H.escape(p["name"])}</code>'
            f'<p class="gr-cmd-desc">{rich(p["desc"])}</p></div>' for p in block['items']]
    return '  <div class="gr-table">\n' + '\n'.join(rows) + '\n  </div>\n'

def render_tip(block):
    warn = block.get('warn')
    label = '<span class="gr-vh">هشدار: </span>' if warn and 'هشدار' not in block['text'] else ''
    ic = icon('exclamation-triangle' if warn else 'lightbulb')
    return f'  <div class="gr-tip{" gr-tip--warn" if warn else ""}">{ic}<p>{label}{rich(block["text"])}</p></div>\n'


# ───────────────────────────── page chrome ─────────────────────────────
def head(title, desc, depth, canonical):
    p = '../' * depth
    return f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(){{try{{var t=localStorage.getItem('gr-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc)}">
<meta name="generator" content="GeekRef build {VERSION} (do not edit; source: data/sheets)">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/svg+xml" sizes="32x32" href="{p}assets/brand/geekref-icon-32.svg">
<link rel="icon" type="image/svg+xml" sizes="16x16" href="{p}assets/brand/geekref-icon-16.svg">
<link rel="apple-touch-icon" href="{p}assets/brand/geekref-touch-180.png">
<link rel="manifest" href="{p}manifest.webmanifest">
<meta name="apple-mobile-web-app-title" content="GeekRef">
<meta name="theme-color" content="#F4F4F0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E1217" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="GeekRef">
<meta property="og:locale" content="fa_IR">
<meta property="og:title" content="{H.escape(title)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="{p}fonts/vazirmatn/Vazirmatn-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}css/geek.css">
<link rel="stylesheet" href="{p}css/geekref.css">
<script src="{p}js/geekref.js" defer></script>
</head>
<body>
<a class="gr-skip" href="#main">رفتن به محتوا</a>
'''

def header(depth, crumb=None):
    p = '../' * depth
    crumb_html = ''
    if crumb:
        crumb_html = f'\n    <nav class="gr-crumb" aria-label="مسیر"><span aria-hidden="true">/</span><span aria-current="page"><bdi>{H.escape(crumb)}</bdi></span></nav>'
    return f'''<header class="gr-header">
  <div class="gm-page gr-header-in">
   <div class="gr-brand-row">
    <a class="gr-brand" href="{p}index.html" aria-label="GeekRef، صفحه‌ی اصلی">
     <img class="gr-wm--light" src="{p}assets/brand/geekref-wordmark-light.svg" alt="" width="92" height="22">
     <img class="gr-wm--dark" src="{p}assets/brand/geekref-wordmark-dark.svg" alt="" width="92" height="22">
    </a>{crumb_html}
   </div>
   <div class="gr-actions">
    <button type="button" class="gr-search-btn" data-gr-search aria-label="جست‌وجو در دستورها" aria-keyshortcuts="Control+K Meta+K /">{icon('search')}<span>جست‌وجو</span><kbd dir="ltr" data-gr-kbd>Ctrl K</kbd></button>
    <div class="gm-seg gr-theme" role="group" aria-label="پوسته">
     <button type="button" data-theme-set="system" aria-pressed="true" title="پیروی از سیستم">{icon('circle-half')}<span>سیستم</span></button>
     <button type="button" data-theme-set="light" aria-pressed="false" title="روشن">{icon('sun')}<span>روشن</span></button>
     <button type="button" data-theme-set="dark" aria-pressed="false" title="تیره">{icon('moon')}<span>تیره</span></button>
    </div>
   </div>
  </div>
</header>
'''

def footer(depth, sheets):
    p = '../' * depth
    sp = '' if depth else 'cheatsheets/'
    links = '\n'.join(f'     <li><a href="{sp}{s["file"]}"><bdi>{H.escape(s["name"])}</bdi></a></li>' for s in sheets)
    return f'''<footer class="gr-footer">
  <div class="gm-page gr-footer-in">
   <nav class="gr-footer-nav" aria-label="برگه‌ها">
    <ul>
     <li><a href="{p}index.html">صفحه‌ی اصلی</a></li>
{links}
    </ul>
   </nav>
   <div class="gr-footer-meta">
    <a class="gm-sign" href="https://github.com/mani-imani">از گیک‌مانی<i class="gm-cursor"></i></a>
    <div class="gr-footer-small">
     <span class="gr-offline" hidden>{icon('check2')}بدون اینترنت هم در دسترس است</span>
     <button type="button" class="gr-install-link" data-gr-install hidden>{icon('download')}نصب به‌شکل برنامه</button>
     <a href="{REPO}">کد پروژه</a>
     <span>مجوز <bdi>MIT</bdi></span>
     <span class="gm-mono">v{VERSION}</span>
    </div>
   </div>
  </div>
</footer>
</body>
</html>
'''

def page_head(sheet, count, nparts, label):
    return f'''<header class="gr-head">
  <p class="gr-eyebrow"><span class="gm-mono">{H.escape(sheet["eyebrow"])}</span></p>
  <h1><bdi>{H.escape(sheet["name"])}</bdi><span class="gr-h1-sub">{fa_text(sheet["subtitle"])}</span></h1>
  <p class="gr-lede">{rich(sheet["lede"])}</p>
  <p class="gr-meta"><b>{fa_num(count)}</b> دستور · <b>{fa_num(nparts)}</b> {label}</p>
 </header>
'''

def toc(items):
    lis = '\n'.join(f'     <li><a href="#{sid}"><span class="gr-toc-num">{fa_num(str(i + 1).zfill(2))}</span><span>{t}</span></a></li>'
                    for i, (sid, t) in enumerate(items))
    desk = f'''  <nav class="gr-toc" aria-label="فهرست این برگه">
   <p class="gr-toc-title">در این برگه</p>
   <ol>
{lis}
   </ol>
  </nav>
'''
    mob = f'''  <details class="gr-toc-m">
   <summary>فهرست این برگه{icon('chevron-down')}</summary>
   <nav aria-label="فهرست این برگه (موبایل)">
    <ol>
{lis}
    </ol>
   </nav>
  </details>
'''
    return desk, mob


# ───────────────────────────── sheet pages ─────────────────────────────
def unique_count(entries):
    return len({e['cmd'] for e in entries})

def build_sections(sheet, sheets):
    anchors = Anchors(s['id'] for s in sheet['sections'])
    entries, body, items = [], [], []
    for i, sec in enumerate(sheet['sections'], 1):
        sid = sec['id']
        th = fa_text(sec['title'])
        items.append((sid, th))
        out = (f'<section class="gr-section" id="{sid}" aria-labelledby="{sid}-t">\n'
               f'  <h2 id="{sid}-t"><span class="gr-section-num" aria-hidden="true">{fa_num(str(i).zfill(2))}</span><span>{th}</span></h2>\n')
        if sec.get('desc'):
            out += f'  <p class="gr-section-desc">{rich(sec["desc"])}</p>\n'
        for b in sec['blocks']:
            t = b['type']
            if t == 'rows': out += render_rows(b, anchors, entries)
            elif t == 'combo': out += render_combo(b, anchors, entries)
            elif t == 'code': out += render_code(b, anchors, entries, sheet)
            elif t == 'tip': out += render_tip(b)
            elif t == 'packages': out += render_packages(b)
        body.append(out + '</section>\n')
    desk, mob = toc(items)
    html_out = (head(f'{sheet["name"]} · {sheet["subtitle"]} | GeekRef', plain(sheet['lede']), 1, f'{SITE}cheatsheets/{sheet["file"]}')
                + header(1, sheet['name'])
                + '<main id="main" class="gm-page">\n ' + page_head(sheet, unique_count(entries), len(items), 'بخش')
                + ' <div class="gr-layout">\n  <div class="gr-content">\n' + mob
                + ''.join(body) + '  </div>\n' + desk + ' </div>\n</main>\n'
                + footer(1, sheets))
    return html_out, entries

GIT_SCRIPT = '''<script>
/* category + text filter (v1 logic, now with aria-pressed) */
var activeCat = 'all';
function gitCat(cat, btn) {
  activeCat = cat;
  document.querySelectorAll('.gr-pills button').forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
  gitFilter();
}
function gitFilter() {
  var q = document.getElementById('gitSearch').value.toLowerCase().trim();
  var visible = 0;
  document.querySelectorAll('.git-card').forEach(function (card) {
    var ok = (activeCat === 'all' || card.dataset.cat === activeCat) &&
             (!q || (card.dataset.text + ' ' + card.textContent).toLowerCase().indexOf(q) > -1);
    card.classList.toggle('hidden', !ok);
    if (ok) visible++;
  });
  document.getElementById('gitEmpty').style.display = visible === 0 ? 'block' : 'none';
}
</script>
'''

def build_cards(sheet, sheets):
    anchors = Anchors()
    entries, cards = [], []
    for c in sheet['cards']:
        aid = anchors.make(c['cmd'])
        entries.append({'cmd': c['cmd'], 'desc': plain(c['desc']), 'id': aid})
        cards.append(f'''   <article class="gm-card git-card" id="{aid}" data-cat="{c['cat']}" data-text="{H.escape(c['cmd'] + ' ' + c.get('keywords', ''))}">
    <div class="git-card-top">{cmd_button(c['cmd'])}<span class="gm-chip">{c['cat']}</span></div>
    <div class="git-card-foot"><p class="git-desc">{rich(c['desc'])}</p>{link_button(aid, c['cmd'])}</div>
   </article>''')
    cats = [{'id': 'all', 'label': 'همه'}] + sheet['categories']
    pills = '\n'.join(f'    <button type="button" aria-pressed="{"true" if c["id"] == "all" else "false"}" data-cat="{c["id"]}" onclick="gitCat(\'{c["id"]}\',this)">{H.escape(c["label"])}</button>'
                      for c in cats)
    body = f'''<div class="gr-filterbar">
   <div class="gr-field">{icon('search')}
    <label class="gr-vh" for="gitSearch">جست‌وجو در دستورهای این برگه</label>
    <input class="gr-input" id="gitSearch" type="search" oninput="gitFilter()" placeholder="جست‌وجو در دستورهای این برگه" autocomplete="off" spellcheck="false">
   </div>
   <div class="gr-pills" role="group" aria-label="دسته‌بندی">
{pills}
   </div>
  </div>
  <div class="git-grid" id="gitGrid">
{chr(10).join(cards)}
  </div>
  <p class="git-empty" id="gitEmpty" role="status">دستوری با این مشخصات پیدا نشد.</p>
'''
    html_out = (head(f'{sheet["name"]} · {sheet["subtitle"]} | GeekRef', plain(sheet['lede']), 1, f'{SITE}cheatsheets/{sheet["file"]}')
                + header(1, sheet['name'])
                + '<main id="main" class="gm-page">\n ' + page_head(sheet, unique_count(entries), len(sheet['categories']), 'دسته')
                + ' ' + body + '</main>\n' + GIT_SCRIPT + footer(1, sheets))
    return html_out, entries


# ───────────────────────────── home ─────────────────────────────
def build_home(sheets, counts, total):
    cards = []
    for s in sheets:
        cards.append(f'''   <li><a class="gm-card gm-card--lift gr-sheet" href="cheatsheets/{s['file']}">
    <span class="gr-sheet-icon">{icon(s['icon'])}</span>
    <h3><bdi>{H.escape(s['name'])}</bdi><small>{fa_text(s['subtitle'])}</small></h3>
    <p>{rich(s['card'])}</p>
    <span class="gr-sheet-meta"><span>{fa_num(counts[s['file']])} دستور</span>{icon('arrow-up-left')}</span>
   </a></li>''')
    desc = 'برگه‌های مرجع فارسی برای برنامه‌نویس‌ها: دستورهای پرکاربرد Ubuntu، Python، Django و Git با توضیح کوتاه فارسی.'
    return (head('GeekRef · برگه‌های مرجع فارسی برای برنامه‌نویس‌ها', desc, 0, SITE)
            + header(0)
            + f'''<main id="main" class="gm-page">
 <section class="gr-hero" aria-labelledby="hero-t">
  <h1 id="hero-t">برگه‌های مرجع فارسی برای برنامه‌نویس‌ها</h1>
  <p class="gr-hero-lede">دستورهای پرکاربرد <bdi>Ubuntu</bdi>، <bdi>Python</bdi>، <bdi>Django</bdi> و <bdi>Git</bdi>، هر کدام با یک توضیح کوتاه فارسی. پیدا کنید، با یک کلیک کپی کنید و به کارتان برسید.</p>
  <button type="button" class="gr-hero-search" data-gr-search>{icon('search')}<span>جست‌وجو در {fa_num(total)} دستور</span><kbd dir="ltr" data-gr-kbd>Ctrl K</kbd></button>
  <div class="gm-term"><span class="gm-prompt">$</span> ls cheatsheets/ | wc -l → {len(sheets)}</div>
 </section>

 <section class="gr-block" aria-labelledby="sheets-t">
  <h2 class="gr-h2" id="sheets-t">برگه‌ها</h2>
  <ul class="gr-sheets">
{chr(10).join(cards)}
  </ul>
 </section>

 <section class="gr-block" aria-labelledby="about-t">
  <h2 class="gr-h2" id="about-t">سازنده</h2>
  <div class="gm-card gr-about">
   <h3>مانی ایمانی‌سنجر <span>| گیک‌مانی</span></h3>
   <p>دانشجوی مهندسی کامپیوتر در کرمانشاه. ابزارهای ساده می‌سازم و طراحی می‌کنم؛ با نام گیک‌مانی.</p>
   <p>این برگه‌ها را اول برای کار خودم نوشتم و حالا برای هر کسی است که دستورها را فارسی و سریع می‌خواهد.</p>
   <div class="gr-links">
    <a class="gm-btn gm-btn--secondary" href="https://github.com/mani-imani">{icon('github')}<bdi>GitHub</bdi></a>
    <a class="gm-btn gm-btn--secondary" href="https://www.linkedin.com/in/mani-imani">{icon('linkedin')}<bdi>LinkedIn</bdi></a>
    <a class="gm-btn gm-btn--secondary" href="https://t.me/mani_imani">{icon('telegram')}<bdi>Telegram</bdi></a>
    <a class="gm-btn gm-btn--secondary" href="mailto:imanisanjar@gmail.com">{icon('envelope')}ایمیل</a>
   </div>
  </div>
 </section>
</main>
''' + footer(0, sheets))


# ───────────────────────────── offline (PWA) ─────────────────────────────
PRECACHE_GLOBS = ['index.html', 'cheatsheets/*.html', 'css/*.css', 'js/*.js', 'fonts/*/*.woff2',
                  'assets/search-index.json', 'assets/brand/*.svg', 'assets/brand/*.png', 'manifest.webmanifest']

def write_manifest():
    m = {
        'name': 'GeekRef · برگه‌های مرجع فارسی برای برنامه‌نویس‌ها',
        'short_name': 'GeekRef',
        'description': 'دستورهای پرکاربرد با توضیح کوتاه فارسی؛ بدون اینترنت هم کار می‌کند.',
        'lang': 'fa', 'dir': 'rtl',
        'start_url': './', 'scope': './', 'display': 'standalone',
        'background_color': '#F4F4F0', 'theme_color': '#F4F4F0',
        'icons': [
            {'src': 'assets/brand/geekref-pwa-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': 'assets/brand/geekref-pwa-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': 'assets/brand/geekref-pwa-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
            {'src': 'assets/brand/geekref-icon.svg', 'sizes': 'any', 'type': 'image/svg+xml', 'purpose': 'any'},
        ],
    }
    write('manifest.webmanifest', json.dumps(m, ensure_ascii=False, indent=2) + '\n')

def write_sw():
    files = sorted({os.path.relpath(f, ROOT) for g in PRECACHE_GLOBS for f in glob.glob(os.path.join(ROOT, g))})
    h = hashlib.sha256()
    for f in files:
        h.update(f.encode()); h.update(open(os.path.join(ROOT, f), 'rb').read())
    version = h.hexdigest()[:10]
    listing = ',\n  '.join(json.dumps(f) for f in ['./'] + files)
    write('sw.js', f'''/* GeekRef service worker. Generated by tools/build.py; do not edit.
   Pages: network first (fresh when online), cache when offline.
   Everything else: cache first. The cache name changes whenever a file changes. */
var CACHE = 'geekref-{version}';
var FILES = [
  {listing}
];

self.addEventListener('install', function (e) {{
  e.waitUntil(caches.open(CACHE).then(function (c) {{ return c.addAll(FILES); }}).then(function () {{ return self.skipWaiting(); }}));
}});

self.addEventListener('activate', function (e) {{
  e.waitUntil(caches.keys().then(function (keys) {{
    return Promise.all(keys.filter(function (k) {{ return k.indexOf('geekref-') === 0 && k !== CACHE; }}).map(function (k) {{ return caches.delete(k); }}));
  }}).then(function () {{ return self.clients.claim(); }}));
}});

self.addEventListener('fetch', function (e) {{
  var req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {{
    e.respondWith(fetch(req).then(function (res) {{
      var copy = res.clone(); caches.open(CACHE).then(function (c) {{ c.put(req, copy); }});
      return res;
    }}).catch(function () {{
      return caches.match(req, {{ ignoreSearch: true }}).then(function (r) {{ return r || caches.match('index.html'); }});
    }}));
    return;
  }}
  e.respondWith(caches.match(req, {{ ignoreSearch: true }}).then(function (r) {{
    return r || fetch(req).then(function (res) {{
      if (res.ok) {{ var copy = res.clone(); caches.open(CACHE).then(function (c) {{ c.put(req, copy); }}); }}
      return res;
    }});
  }}));
}});
''')
    return version, len(files)


# ───────────────────────────── validation ─────────────────────────────
def walk_strings(obj, path=''):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items(): yield from walk_strings(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj): yield from walk_strings(v, f'{path}[{i}]')

def validate(sheet, fname):
    def err(msg): ERRORS.append(f'{fname}: {msg}')
    for k in ('order', 'file', 'name', 'subtitle', 'eyebrow', 'lede', 'card', 'icon', 'layout'):
        if k not in sheet: err(f'missing "{k}"')
    if not os.path.exists(os.path.join(ROOT, 'assets/icons/bootstrap', sheet.get('icon', '') + '.svg')):
        err(f'icon "{sheet.get("icon")}" not found in assets/icons/bootstrap/')
    for path, s in walk_strings(sheet):
        if EMOJI.search(s): err(f'emoji in {path} (brand.md §5.5)')
        if 'ي' in s or 'ك' in s: err(f'Arabic ي/ك in {path}; use Persian ی/ک')
    if sheet.get('layout') == 'sections':
        ids = [s.get('id') for s in sheet.get('sections', [])]
        if len(ids) != len(set(ids)): err('duplicate section ids')
        for s in sheet.get('sections', []):
            for b in s.get('blocks', []):
                if b.get('type') not in ('rows', 'combo', 'code', 'tip', 'packages'):
                    err(f'unknown block type "{b.get("type")}" in section {s.get("id")}')
    elif sheet.get('layout') == 'cards':
        cats = {c['id'] for c in sheet.get('categories', [])}
        for c in sheet.get('cards', []):
            if c.get('cat') not in cats: err(f'card "{c.get("cmd")}" has unknown category "{c.get("cat")}"')
    else:
        err('layout must be "sections" or "cards"')


# ───────────────────────────── main ─────────────────────────────
def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

def main():
    check_only = '--check' in sys.argv
    sheets = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data/sheets/*.json'))):
        try:
            s = json.load(open(f, encoding='utf-8'))
        except json.JSONDecodeError as e:
            ERRORS.append(f'{os.path.basename(f)}: invalid JSON: {e}'); continue
        validate(s, os.path.basename(f))
        sheets.append(s)
    if ERRORS:
        print('\n'.join('error: ' + e for e in ERRORS)); sys.exit(1)
    sheets.sort(key=lambda s: s['order'])
    if check_only:
        print(f'ok: {len(sheets)} sheets valid'); return

    index, counts = [], {}
    for s in sheets:
        out, entries = (build_cards if s['layout'] == 'cards' else build_sections)(s, sheets)
        write(f'cheatsheets/{s["file"]}', out)
        seen = set()
        for e in entries:
            if e['cmd'] in seen: continue
            seen.add(e['cmd'])
            index.append({'cmd': e['cmd'], 'desc': fa_plain(e['desc'], digits=not e.get('code')),
                          'title': s['name'], 'file': s['file'], 'id': e['id']})
        counts[s['file']] = len(seen)
    write('assets/search-index.json', json.dumps(index, ensure_ascii=False, indent=1) + '\n')
    write('index.html', build_home(sheets, counts, len(index)))
    write_manifest()
    version, n = write_sw()
    print(f'built {len(sheets)} sheets · {len(index)} commands · offline cache {version} ({n} files)')
    for s in sheets:
        print(f'  {s["file"]:<18} {counts[s["file"]]}')

if __name__ == '__main__':
    main()
