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
             'Get My NordVPN Deal →', '30-day money-back guarantee'),
    "surf": ('https://get.surfshark.net/aff_c?offer_id=926&aff_id=44567', 'btn-surf',
             'Get My Surfshark Deal →', '30-day money-back guarantee'),
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
    t = add_saily_coupon(t)
    t = tag_links(t, slug)
    if t != orig:
        open(f, "w", encoding="utf-8", newline="\r\n").write(t)
        print("updated", f)
