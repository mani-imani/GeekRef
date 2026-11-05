# Changelog

## v2.2.0 · Nov 2026
- Install prompt: on the first visit a small card offers to install GeekRef as an app (Chrome, Edge, Android). On iPhone and iPad it shows the two Safari steps instead. It appears once; an "install as an app" link stays in the footer. Nothing is shown once the app is installed, or in browsers that cannot install sites.

## v2.1.0 · Nov 2026
- New look in the GeekMani product family: `geek.css`, brand icon and wordmark, light and dark themes with a System / Light / Dark switch, and the "by GeekMani" signature.
- All content moved to `data/sheets/*.json`; `tools/build.py` generates the pages, the search index and the offline file list.
- Search across every sheet with `/` or `Ctrl`/`⌘` + `K`. Results are ranked: commands that start with your query come first, then the current sheet. Persian and English digits, ZWNJ and Arabic ي/ك are treated alike.
- Every command has its own link, with a button to copy it.
- Works offline after the first visit and can be installed as an app (PWA).
- Table of contents beside each sheet, a collapsible one on phones, and clean print styles.
- Numbers inside code comments and in the search index stay as written (`8000`, `python3`, `base64`).

## v1
- First public version: Ubuntu, Python, Python Setup, Django, Git and tree sheets.
