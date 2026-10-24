"""IKEA-inspired (style only) RTL CSS for the app."""
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Hebrew:wght@400;700&display=swap');
:root { --ink:#111111; --ink2:#484848; --line:#DFDFDF; --bg2:#F5F5F5; --blue:#0058A3; --blue-h:#004F93; --yellow:#FFDB00; }
html, body, .stApp, .stApp * { font-family: "Noto Sans Hebrew", sans-serif; }
.stApp { direction: rtl; text-align: right; background:#fff; color: var(--ink); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display:none !important; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0; max-width: 1280px; }
.topstrip { height:4px; background: var(--yellow); box-shadow: 0 0 0 100vmax var(--yellow); clip-path: inset(0 -100vmax); }
.hdr { display:flex; align-items:center; gap:2.5rem; padding:1rem 0; border-bottom:1px solid var(--line); }
.brand { font-weight:700; font-size:1.6rem; letter-spacing:.5px; }
.nav span { margin-inline-end:1.5rem; font-size:.9rem; color: var(--ink); }
.crumbs { font-size:.8rem; color: var(--ink2); padding:1rem 0 1.25rem; }
.crumbs .sep { color:#929292; margin:0 .4rem; }
.crumbs .cur-page { color: var(--ink); }
.gallery-box { background: var(--bg2); border-radius: 8px; padding: .5rem; }
.badge { display:inline-block; background: var(--yellow); color: var(--ink); font-weight:700;
         font-size:.75rem; padding:.2rem .6rem; margin-bottom:.6rem; }
.ptitle { font-size:1.25rem; font-weight:700; line-height:1.3; }
.psub { color: var(--ink2); font-size:.95rem; margin-top:.15rem; }
.price { font-size:2.5rem; font-weight:700; line-height:1.1; margin-top:1rem; }
.price .cur { font-size:1rem; vertical-align: top; position:relative; top:.35rem; margin-inline-end:.15rem; }
.price-note { color: var(--ink2); font-size:.8rem; margin-bottom:1rem; }
.pdesc { color: var(--ink2); font-size:.95rem; line-height:1.6; margin:1rem 0; }
.subhead { font-weight:700; font-size:1rem; margin:1.25rem 0 .5rem; }
.avail { font-size:.85rem; margin-top:.9rem; }
.dot-ok { color:#0A8A00; } .dot-bad { color:#E00751; }
.rowline { display:flex; justify-content:space-between; padding:.55rem 0; border-bottom:1px solid var(--line); }
.rowline.total { font-weight:700; }
.rowline .v { direction:ltr; }
.small-gray { color: var(--ink2); font-size:.8rem; padding-top:.5rem; }
/* accordions */
[data-testid="stExpander"] { border:0 !important; border-radius:0 !important; box-shadow:none !important;
  background:transparent; border-bottom:1px solid var(--line) !important; }
[data-testid="stExpander"]:first-of-type { border-top:1px solid var(--line) !important; }
[data-testid="stExpander"] details { border:0 !important; border-radius:0 !important; background:transparent; }
[data-testid="stExpander"] summary { padding:1.1rem 0; font-weight:700; font-size:1rem; }
[data-testid="stExpander"] summary:hover { color: var(--ink2); background: transparent; }
[data-testid="stExpanderDetails"] { padding: 0 0 1.25rem 0; }
/* buttons */
[data-testid="stBaseButton-primary"], [data-testid="stDownloadButton"] button[kind="primary"] {
  background: var(--blue); color:#fff; border:1px solid var(--blue); border-radius:64px;
  font-weight:700; padding:.75rem 1.5rem; }
[data-testid="stBaseButton-primary"]:hover, [data-testid="stDownloadButton"] button[kind="primary"]:hover {
  background: var(--blue-h); border-color: var(--blue-h); color:#fff; }
[data-testid="stBaseButton-secondary"], [data-testid="stDownloadButton"] button[kind="secondary"] {
  background: transparent; color: var(--ink); border:1px solid var(--ink); border-radius:64px; font-weight:700; }
[data-testid="stBaseButton-secondary"]:hover, [data-testid="stDownloadButton"] button[kind="secondary"]:hover {
  border-color: var(--ink); background: var(--bg2); color: var(--ink); }
/* inputs */
[data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="base-input"] {
  border-radius:4px; border-color:#929292; }
[data-testid="stNumberInput"] label p { font-size:.85rem; color: var(--ink2); }
</style>
"""
