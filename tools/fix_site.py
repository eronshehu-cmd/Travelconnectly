"""Bulk SEO / tracking / CRO fixes for the TravelConnectly static site. Idempotent."""
import glob
import os
import re
import sys

ROOT = sys.argv[1]
os.chdir(ROOT)

PUBLISHED = "2026-07-12"
MODIFIED = "2026-09-17"
ANALYTICS = '<script defer src="/_vercel/insights/script.js"></script>'

STICKY = {
    "nord": ('https://go.nordvpn.net/aff_c?offer_id=725&aff_id=141128', 'btn-nord',
             'Get NordVPN · €3.49/mo →', '2-year plan · 30-day money-back guarantee'),
    "surf": ('https://get.surfshark.net/aff_c?offer_id=926&aff_id=44567', 'btn-surf',
             'Get Surfshark · $2.49/mo →', '2-year plan · 30-day money-back guarantee'),
    "saily": ('https://go.saily.site/aff_c?offer_id=101&aff_id=16029&coupon=travelconnectly', 'btn-saily',
              "Get Saily's eSIM Plans →", '10% off with code TRAVELCONNECTLY'),
}


def provider_of(url):
    if "nordvpn" in url:
        return "nord"
    if "surfshark" in url:
        return "surf"
    if "saily" in url:
        return "saily"
    return None


def fix_sticky(t, slug):
    if slug == "index":
        return t
    m = re.search(r'class="nav-cta">\s*<a href="([^"]+)"', t)
    if not m:
        return t
    prov = provider_of(m.group(1))
    if not prov:
        return t
    href, cls, label, sub = STICKY[prov]
    new = (f'<div class="sticky-cta">\n  <a href="{href}" target="_blank" rel="sponsored noopener" '
           f'class="btn {cls}">{label}</a>\n  <span class="sub">{sub}</span>\n</div>')
    return re.sub(r'<div class="sticky-cta">.*?</div>', new, t, count=1, flags=re.S)


def fix_index_cta(t):
    # Header "top pick" should point at the site's stated best-overall pick (NordVPN).
    t = t.replace(
        '<a href="https://get.surfshark.net/aff_c?offer_id=926&aff_id=44567" target="_blank" rel="sponsored noopener" class="btn btn-primary">Get Our Top Pick</a>',
        '<a href="https://go.nordvpn.net/aff_c?offer_id=725&aff_id=141128" target="_blank" rel="sponsored noopener" class="btn btn-primary">Get Our Top Pick</a>')
    # Hero: best-overall first.
    surf = '<a href="https://get.surfshark.net/aff_c?offer_id=926&aff_id=44567" target="_blank" rel="sponsored noopener" class="btn btn-surf">Try Surfshark →</a>'
    nord = '<a href="https://go.nordvpn.net/aff_c?offer_id=725&aff_id=141128" target="_blank" rel="sponsored noopener" class="btn btn-nord" style="width:auto;">Try NordVPN →</a>'
    old = surf + "\n          " + nord
    if old in t:
        t = t.replace(old, nord.replace('class="btn btn-nord" style="width:auto;"', 'class="btn btn-nord" style="width:auto;"')
                      + "\n          " + surf.replace('class="btn btn-surf"', 'class="btn btn-surf" style="width:auto;"'))
    return t


def fix_schema(t, canonical):
    old = '"author": { "@type": "Organization", "name": "TravelConnectly" },'
    new = ('"author": { "@type": "Person", "name": "Eron", "url": "https://www.travelconnectly.com/about.html" },\n'
           f'  "datePublished": "{PUBLISHED}",\n'
           f'  "dateModified": "{MODIFIED}",\n'
           f'  "mainEntityOfPage": "{canonical}",')
    return t.replace(old, new)


def position_of(t, pos):
    main = t.find("<main")
    footer = t.find("<footer")
    sticky = t.find('<div class="sticky-cta"')  # also matches plan-specific stickies with data-custom
    if sticky != -1 and pos > sticky:
        return "sticky"
    if main != -1 and pos < main:
        return "header"
    if footer != -1 and pos > footer:
        return "footer"
    # Nearest preceding known container marker wins.
    markers = {
        'class="verdict-box"': "verdict", 'class="cta-band"': "ctaband", 'class="hero"': "hero",
        'class="board"': "board", 'class="provider-card': "card", 'class="usecase"': "usecase",
        'class="esim-spotlight"': "esim", 'class="mc-card': "minicard", 'class="glance': "table",
        'class="qa-card"': "quickanswer", 'class="qa-chips"': "chips",
    }
    best, best_d = "content", 2500
    for marker, name in markers.items():
        i = t.rfind(marker, 0, pos)
        if i != -1 and pos - i < best_d:
            best, best_d = name, pos - i
    return best


SAILY_BASE = "go.saily.site/aff_c?offer_id=101&aff_id=16029"


def add_saily_coupon(t):
    # Saily's TRAVELCONNECTLY code (10% off, Oct 2026) is applied automatically when the link carries coupon=.
    return re.sub(re.escape(SAILY_BASE) + r'(?!&coupon=)', SAILY_BASE + "&coupon=travelconnectly", t)


def tag_links(t, slug):
    def hasoffers(m):
        url = m.group(1)
        if "aff_sub=" in url:
            return m.group(0)
        return f'href="{url}&aff_sub={slug}&aff_sub2={position_of(t, m.start())}"'

    t2 = re.sub(r'href="(https://(?:go\.nordvpn\.net|get\.surfshark\.net|go\.saily\.site|go\.getproton\.me)/aff_c\?[^"]+)"', hasoffers, t)

    def wise(m):
        return f'href="{m.group(1)}/pubref:{slug}"'

    t2 = re.sub(r'href="(https://wise\.prf\.hn/click/camref:[A-Za-z0-9]+)"', wise, t2)
    return t2


def fix_menu(t):
    t = t.replace('<button class="menu-toggle" aria-label="Open menu">',
                  '<button class="menu-toggle" aria-label="Open menu" aria-expanded="false">')
    old = "navLinks.style.display = isOpen ? 'none' : 'flex';"
    if old in t and "aria-expanded', String" not in t:
        t = t.replace(old, old + "\n    toggle.setAttribute('aria-expanded', String(!isOpen));")
    return t


def fix_proton(t):
    # Proton became an affiliate partner (Sept 2026); its links are handled by proton.py.
    return t


GUTTER_CSS = "/* .breadcrumb/.article-head padding overrides .wrap's side gutter */\n.wrap.breadcrumb, .wrap.article-head{ padding-left:28px; padding-right:28px; }\n"


def fix_gutter(t):
    if ".wrap.breadcrumb, .wrap.article-head" in t or 'class="wrap breadcrumb"' not in t:
        return t
    return t.replace("</style>", GUTTER_CSS + "</style>", 1)


def add_analytics(t):
    if "/_vercel/insights/script.js" in t:
        return t
    return t.replace("</head>", ANALYTICS + "\n</head>", 1)


# Both Saily sales so far came from the sticky button, which used to show on mobile only.
# On desktop it becomes a small bottom-right card that appears after scrolling and can be closed.
DESKTOP_STICKY_CSS = """/* desktop sticky */
.sticky-cta .sc-close{ display:none; }
@media (min-width:761px){
  .sticky-cta{ display:flex; flex-direction:column; gap:6px; position:fixed; right:24px; bottom:24px; z-index:60; width:300px;
    padding:14px 16px 12px; background:rgba(13,27,42,0.97); border:1px solid #2A4563; border-radius:14px;
    box-shadow:0 12px 32px rgba(0,0,0,.35); opacity:0; transform:translateY(16px); pointer-events:none; transition:opacity .25s, transform .25s; }
  .sticky-cta.show{ opacity:1; transform:none; pointer-events:auto; }
  .sticky-cta .btn{ width:100%; padding:12px 16px; font-size:0.9rem; text-align:center; }
  .sticky-cta .sub{ display:block; text-align:center; font-size:0.68rem; color:var(--text-muted); font-family:'IBM Plex Mono',monospace; }
  .sticky-cta .sc-close{ display:flex; align-items:center; justify-content:center; position:absolute; top:-12px; right:-12px; width:28px; height:28px;
    border-radius:50%; border:1px solid #2A4563; background:var(--navy-panel); color:var(--text-light); font-size:16px; line-height:1; cursor:pointer; }
}
"""
DESKTOP_STICKY_JS = """<script>
(function(){
  var s = document.querySelector('.sticky-cta');
  if (!s) return;
  var off = false;
  try { off = sessionStorage.getItem('tc-sticky-off') === '1'; } catch (e) {}
  if (off) { s.style.display = 'none'; return; }
  var b = document.createElement('button');
  b.type = 'button'; b.className = 'sc-close'; b.setAttribute('aria-label', 'Close'); b.textContent = '\\u00d7';
  b.addEventListener('click', function(){
    s.style.display = 'none';
    try { sessionStorage.setItem('tc-sticky-off', '1'); } catch (e) {}
  });
  s.appendChild(b);
  function onScroll(){ s.classList.toggle('show', window.scrollY > 700); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
</script>"""


def add_desktop_sticky(t):
    if "/* desktop sticky */" in t or '<div class="sticky-cta"' not in t:
        return t
    t = t.replace("</style>", DESKTOP_STICKY_CSS + "</style>", 1)
    return t.replace("</body>", DESKTOP_STICKY_JS + "\n</body>", 1)


for f in sorted(glob.glob("*.html")):
    if f.startswith("google"):
        continue
    slug = f[:-5]
    t = open(f, encoding="utf-8").read()
    orig = t
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', t).group(1)
    if slug == "index":
        t = fix_index_cta(t)
    t = fix_sticky(t, slug)
    t = fix_schema(t, canonical)
    t = fix_proton(t)
    t = fix_menu(t)
    t = add_analytics(t)
    t = fix_gutter(t)
    t = add_desktop_sticky(t)
    t = add_saily_coupon(t)
    t = tag_links(t, slug)
    if t != orig:
        open(f, "w", encoding="utf-8", newline="\r\n").write(t)
        print("updated", f)
