<div dir="rtl">

<div align="center">

```
   ____          _    ____       __
  / ___| ___  __| | _|  _ \ ___ / _|
 | |  _ / _ \/ _` |/ / |_) / _ \ |_
 | |_| |  __/ (_| |< <|  _ <  __/  _|
  \____|\___|\__,_|\_\_| \_\___|_|
```

# GeekRef

**مرجع سریع دستورات توسعه‌دهنده — فارسی · دقیق · کاربردی**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen?style=flat-square&logo=github)](https://mani-imani.github.io/geekref)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
![Static](https://img.shields.io/badge/Static-HTML%20%2F%20CSS%20%2F%20JS-orange?style=flat-square)
![RTL](https://img.shields.io/badge/RTL-فارسی-red?style=flat-square)

</div>

---

## 📖 درباره پروژه

GeekRef یه مرجع شخصی و سریع برای دستورات توسعه‌ست — ساخته‌شده توسط یه گیک تمام عیار که داره به Senior Web Developer تبدیل می‌شه.

پروژه کاملاً استاتیکه (HTML + CSS + JS)، بدون هیچ framework یا backend — فقط فایل‌های ساده که روی GitHub Pages آپلود می‌شن.

---

## ✨ ویژگی‌ها

- 🔍 **جستجوی سراسری** — با `Ctrl+K` در بین ۲۸۰+ دستور جستجو کن
- 🌙 **Dark / Light Mode** — toggle بدون flash، با حافظه localStorage
- 📋 **کپی با یک کلیک** — هر دستور رو سریع کپی کن
- 🌿 **فهرست مطالب** — ناوبری سریع داخل هر cheatsheet
- 🖥️ **Terminal Hero** — انیمیشن تایپ‌کردن روی صفحه اصلی
- 📱 **واکنش‌گرا** — روی موبایل هم خوب کار می‌کنه
- ⚡ **سریع** — بدون dependency خارجی، بدون build step

---

## 📚 محتوا

| Cheatsheet | دستورات | موضوع |
|---|---|---|
| 🐧 **Ubuntu** | ۹۴+ | مدیریت فایل، شبکه، پردازش‌ها، SSH |
| 🌿 **Django** | ۶۰+ | manage.py، migration، ORM، deploy |
| 🐍 **Python** | ۵۶+ | نصب، pip، venv، pyenv، دیباگ |
| ⚙️ **Python Setup** | ۳۴+ | محیط توسعه، pyenv، pip، گام‌به‌گام |
| 🔀 **Git** | ۲۷ | commit، branch، remote، undo |
| 🌳 **tree** | ۲۶ | ساختار درختی، فیلتر، خروجی |

---

## 🚀 استفاده

```bash
# Clone
git clone https://github.com/mani-imani/geekref.git
cd geekref

# باز کردن
open index.html
# یا با VS Code Live Server
```

---

## 📁 ساختار پروژه

```
geekref/
├── index.html              ← صفحه اصلی
├── css/
│   ├── shared.css          ← سیستم طراحی مشترک (dark/light tokens)
│   └── gr.js               ← جستجو، toggle تم، copy
├── assets/
│   ├── favicon.svg         ← آیکون سایت
│   └── search-index.json   ← ایندکس جستجوی سراسری
└── cheatsheets/
    ├── ubuntu.html
    ├── django.html
    ├── python.html
    ├── python_setup.html
    ├── git.html
    └── tree.html
```

---

## 🌐 دیپلوی روی GitHub Pages

```bash
# 1. ساخت repository
git init
git add .
git commit -m "feat: GeekRef initial release"

# 2. اتصال به GitHub
git remote add origin https://github.com/mani-imani/geekref.git
git push -u origin main

# 3. فعال کردن GitHub Pages
# Settings > Pages > Source: Deploy from branch > main / (root)
```

سایت در آدرس زیر آنلاین می‌شه:
`https://mani-imani.github.io/geekref`

---

## ➕ اضافه کردن cheatsheet جدید

```html
<!-- 1. فایل جدید بساز: cheatsheets/newsheet.html -->
<!-- از الگوی زیر استفاده کن: -->

<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <script>(function(){var t=localStorage.getItem('gr-theme');if(t==='light')document.documentElement.setAttribute('data-theme','light');})();</script>
  <!-- ... -->
  <link rel="stylesheet" href="../css/shared.css">
  <style>
    :root { --accent: #YOUR_COLOR; --accent-rgb: R,G,B; }
  </style>
</head>
<body>
  <nav class="gr-navbar">...</nav>
  <!-- محتوا -->
  <script src="../css/gr.js"></script>
</body>
</html>
```

```json
// 2. دستورات رو به assets/search-index.json اضافه کن:
{
  "cmd": "your-command",
  "desc": "توضیح فارسی",
  "title": "SheetName",
  "icon": "🔧",
  "accent": "#YOUR_COLOR",
  "file": "newsheet.html"
}
```

```html
<!-- 3. کارت رو به index.html اضافه کن -->
<a href="cheatsheets/newsheet.html" class="card" style="--card-accent:#COLOR">
  ...
</a>
```

---

## 🛠️ تکنولوژی

- **HTML5 + CSS3 + Vanilla JS** — بدون framework
- **CSS Custom Properties** — سیستم توکن برای dark/light mode
- **Vazirmatn** — فونت فارسی
- **JetBrains Mono** — فونت کد
- **GitHub Pages** — هاستینگ رایگان

---

## 👤 سازنده

**GeekMani** — گیک تمام عیار، در مسیر Senior Web Developer

[![GitHub](https://img.shields.io/badge/GitHub-mani--imani-181717?style=flat-square&logo=github)](https://github.com/mani-imani)
[![Telegram](https://img.shields.io/badge/Telegram-mani__imani-2CA5E0?style=flat-square&logo=telegram)](https://t.me/mani_imani)

---

## 📄 لایسنس

MIT — آزادانه استفاده کن، فقط اگه خوشت اومد یه ⭐ بذار 🙂

</div>

---

<div align="center">

# GeekRef — English

**A fast, bilingual (Persian) developer reference — built by a full-on geek**

</div>

## About

GeekRef is a personal developer cheat-sheet site built with pure HTML/CSS/JS — no framework, no build step, no backend. Deploy anywhere with a single drag-and-drop.

Written entirely in Persian (RTL), but structured so anyone can read and extend it.

## Features

- **Global Search** (`Ctrl+K`) — searches 280+ commands across all sheets
- **Dark / Light Mode** — flash-free toggle with localStorage persistence  
- **One-click Copy** — every command is copyable instantly
- **Table of Contents** — fast in-page navigation
- **Terminal Hero** — typewriter animation on the landing page
- **Responsive** — works on mobile too
- **Zero dependencies** — no npm, no bundler, no CDN (fonts excluded)

## Cheatsheets

| Sheet | Commands | Topics |
|---|---|---|
| 🐧 Ubuntu | 94+ | Files, Network, Processes, SSH, Cron |
| 🌿 Django | 60+ | manage.py, Migrations, ORM, Deploy |
| 🐍 Python | 56+ | Install, pip, venv, pyenv, Debug |
| ⚙️ Python Setup | 34+ | pyenv, venv, pip, Step-by-step setup |
| 🔀 Git | 27 | commit, branch, remote, undo |
| 🌳 tree | 26 | Directory tree, filter, output formats |

## Quick Start

```bash
git clone https://github.com/mani-imani/geekref.git
cd geekref
open index.html   # or use VS Code Live Server
```

## Deploy to GitHub Pages

1. Push to GitHub
2. `Settings > Pages > Deploy from branch > main / (root)`
3. Done — live at `https://mani-imani.github.io/geekref`

## Adding a New Cheatsheet

1. Create `cheatsheets/newsheet.html` using the shared template pattern
2. Add entries to `assets/search-index.json`
3. Add a card to `index.html`

## Stack

`HTML5` · `CSS3 Custom Properties` · `Vanilla JS` · `GitHub Pages`  
Fonts: `Vazirmatn` (Persian) · `JetBrains Mono` (code)

## License

MIT — use freely, star if you like it ⭐
