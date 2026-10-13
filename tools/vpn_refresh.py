"""Refresh VPN prices across the site and add an answer-first Quick answer card to the VPN guides. Idempotent.

Prices checked 13 Oct 2026 on each provider's pricing page. NordVPN only showed euro prices from Kosovo
(no currency switch); Surfshark and Proton showed US dollars. To update: change VPN and CHECKED, rerun build_all.
"""
import os
import re
import sys

os.chdir(sys.argv[1])
CHECKED = "13 October 2026"
CHECKED_MONTH = "October 2026"
DATE = "2026-10-13"

VPN = {
    "nord": dict(name="NordVPN", host="go.nordvpn.net", rate="€3.49", off="69% off", total="€94.23 for the first 27 months",
                 plan="2-year Basic + 3 months", devices="10 devices", cls="nord", letter="N"),
    "surf": dict(name="Surfshark", host="get.surfshark.net", rate="$2.49", off="85% off", total="$67.23 for the first 27 months",
                 plan="2-year Starter + 3 months", devices="Unlimited devices", cls="surf", letter="S"),
    "proton": dict(name="Proton VPN", host="go.getproton.me", rate="$3.49", off="65% off", total="$83.76 for the first 24 months",
                   plan="2-year VPN Plus", devices="10 devices", cls="proton", letter="P"),
}
NOTE = (f"Lowest long-term rate and what the first term costs in total, checked {CHECKED} on each provider's pricing page. "
        "NordVPN showed me euro prices from my location; Surfshark and Proton showed US dollars. Prices renew higher — check at checkout.")

QA_CSS = """/* vpn quick answer */
.vpn-qa{ background:var(--navy-panel); border:1px solid #2A4563; border-radius:16px; padding:16px; margin:0 0 24px; max-width:620px; }
.vpn-qa .qa-label{ display:flex; justify-content:space-between; gap:12px; font-family:'IBM Plex Mono',monospace; font-size:0.69rem; letter-spacing:0.12em; text-transform:uppercase; }
.vpn-qa .qa-label b{ color:var(--amber); font-weight:600; }
.vpn-qa .qa-label span{ color:var(--text-muted); letter-spacing:0.04em; }
.vpn-qa .qa-prov{ display:flex; align-items:flex-start; gap:12px; margin-top:12px; }
.vpn-qa .qa-logo{ width:44px; height:44px; flex:0 0 auto; border-radius:11px; color:#fff; display:flex; align-items:center; justify-content:center; font-family:'Space Grotesk',sans-serif; font-size:1.25rem; font-weight:700; }
.vpn-qa .qa-logo.nord{ background:var(--nord-blue); } .vpn-qa .qa-logo.surf{ background:var(--surf-green); color:#062a22; } .vpn-qa .qa-logo.proton{ background:#5D3EBD; }
.vpn-qa h2{ font-size:1.38rem !important; margin:0 !important; line-height:1.15; }
.vpn-qa .qa-prov p{ margin:2px 0 0 !important; font-size:0.875rem !important; line-height:1.45; color:#C9D5E2 !important; }
.vpn-qa .qa-plan{ display:inline-block; margin-top:14px; line-height:36px; padding:0 12px; background:var(--navy-panel-2); border:1px solid #2A4563; border-radius:999px; font-family:'IBM Plex Mono',monospace; font-size:0.875rem; }
.vpn-qa .qa-plan strong{ color:var(--teal); font-weight:600; }
.vpn-qa .btn{ margin-top:14px; width:100%; min-height:52px; display:flex; align-items:center; justify-content:center; }
.vpn-qa .qa-trust{ list-style:none; margin:12px 0 0; padding:0; display:flex; flex-wrap:wrap; gap:4px 12px; font-size:0.75rem; line-height:1.5; color:var(--text-muted); }
.vpn-qa .qa-trust li::before{ content:"✓"; color:var(--teal); margin-right:5px; }
/* end vpn quick answer */
"""


def provider_of_href(href):
    return next((k for k, v in VPN.items() if v["host"] in href), None)


def fix_table_rows(t):
    def row(m):
        tr = m.group(0)
        k = provider_of_href(tr)
        if not k or '<td class="price">' not in tr:
            return tr
        v = VPN[k]
        cell = f'<td class="price">{v["rate"]}/mo<br><small style="color:#9FB0C4;font-size:0.76rem;">{v["total"]}</small></td>'
        return re.sub(r'<td class="price">.*?</td>', cell, tr, count=1, flags=re.S)
    return re.sub(r"<tr>.*?</tr>", row, t, flags=re.S)


def fix_notes(t):
    t = re.sub(r'<p class="price-note">Lowest advertised long-term rates shown against each provider\'s standard monthly rate, checked [A-Za-z]+ \d{4}\. Prices change often and renew higher — check the provider for current pricing\.',
               f'<p class="price-note">{NOTE}', t)
    t = re.sub(r'<p class="price-note">Lowest long-term rate and what the first term costs in total, checked .*? Prices renew higher — check at checkout\.',
               f'<p class="price-note">{NOTE}', t)
    return t


def fix_home(t):
    # Provider cards (NordVPN, Surfshark, Proton VPN, in that order): price, discount and the first-term total.
    cards = list(re.finditer(r'<div class="price-block">.*?</div>\s*</div>', t, flags=re.S))
    order = ["nord", "surf", "proton"]
    for m, k in reversed(list(zip(cards, order))):
        v = VPN[k]
        block = m.group(0)
        block = re.sub(r'<span class="price-now">.*?</span>', f'<span class="price-now">{v["rate"]}</span>', block)
        block = re.sub(r'<span class="price-off">.*?</span>', f'<span class="price-off">{v["off"]}</span>', block)
        block = re.sub(r'<span>(<s>.*?</s> month-to-month|[^<]*for the first \d+ months)</span>', f'<span>{v["total"]}</span>', block)
        t = t[:m.start()] + block + t[m.end():]
    t = re.sub(r'<p class="price-note">Prices are each provider\'s lowest advertised long-term rate, checked [A-Za-z]+ \d{4}, shown against their standard monthly rate\. Renewal prices are usually higher\.',
               f'<p class="price-note">Prices are each provider\'s lowest long-term rate and first-term total, checked {CHECKED}. NordVPN showed me euro prices from my location; Surfshark and Proton showed US dollars. Renewal prices are usually higher.', t)
    t = re.sub(r'<tr><td>Lowest price</td><td class="nord">.*?</td><td class="surf">.*?</td></tr>',
               f'<tr><td>Lowest price</td><td class="nord">{VPN["nord"]["rate"]}/mo</td><td class="surf">{VPN["surf"]["rate"]}/mo</td></tr>', t)
    t = re.sub(r'<p class="price-note">Lowest advertised rates on multi-year plans, checked [A-Za-z]+ \d{4}\. Prices change often and renew higher — check the provider for current pricing\.</p>',
               f'<p class="price-note">Lowest rates on multi-year plans, checked {CHECKED}. NordVPN showed me euro prices from my location. Prices renew higher — check at checkout.</p>', t)
    return t


def add_quick_answer(t, slug):
    if "vpn-qa" in t:
        t = re.sub(r'\n    <section class="qa-card vpn-qa".*?</section>', "", t, flags=re.S)  # rebuild with current prices
    m = re.search(r'<div class="verdict-box">\s*<div class="eyebrow">OUR PICK</div>\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>\s*<a href="([^"]+)"', t, flags=re.S)
    if not m:
        return t
    k = provider_of_href(m.group(3))
    if not k:
        return t
    v = VPN[k]
    head = re.search(r'<div class="wrap article-head">\s*<div class="eyebrow">(.*?)</div>', t, flags=re.S)
    label = head.group(1).replace("BEST FOR ", "").title() if head else "Our pick"
    # Tagged here because fix_site.py's position markers only recognise class="qa-card" exactly.
    base = re.sub(r"&aff_sub=.*$", "", m.group(3)) + f"&aff_sub={slug}&aff_sub2=quickanswer"
    card = f"""
    <section class="qa-card vpn-qa" aria-labelledby="qa-title">
      <div class="qa-label"><b>Quick answer</b><span>{label}</span></div>
      <div class="qa-prov">
        <div class="qa-logo {v['cls']}" aria-hidden="true">{v['letter']}</div>
        <div>
          <h2 id="qa-title">{v['name']}</h2>
          <p>{m.group(2)}</p>
        </div>
      </div>
      <span class="qa-plan">{v['plan']} · <strong>{v['rate']}/mo</strong></span>
      <a class="btn btn-{v['cls']}" href="{base}" target="_blank" rel="sponsored noopener">Get {v['name']} →</a>
      <ul class="qa-trust"><li>30-day money-back guarantee</li><li>{v['devices']}</li><li>Audited no-logs policy</li></ul>
    </section>"""
    t = t.replace('<div class="wrap">\n    <img class="hero-img"', '<div class="wrap">' + card + '\n    <img class="hero-img"', 1)
    if "/* end vpn quick answer */" in t:
        t = re.sub(r"/\* vpn quick answer \*/.*?/\* end vpn quick answer \*/\n", lambda _: QA_CSS, t, count=1, flags=re.S)
    elif "/* vpn quick answer */" in t:  # first version had no end marker and sat right before </style>
        t = re.sub(r"/\* vpn quick answer \*/.*?(?=</style>)", lambda _: QA_CSS, t, count=1, flags=re.S)
    else:
        t = t.replace("</style>", QA_CSS + "</style>", 1)
    return t


def bump_dates(t):
    t = re.sub(r"UPDATED [A-Z]+ 2026", f"UPDATED {CHECKED_MONTH.upper()}", t)
    t = re.sub(r"Last updated: [A-Za-z]+ 2026", f"Last updated: {CHECKED_MONTH}", t)
    return re.sub(r'"dateModified": "[^"]+"', f'"dateModified": "{DATE}"', t, count=1)


changed = []
for f in sorted(os.listdir(".")):
    if not f.endswith(".html"):
        continue
    t = open(f, encoding="utf-8").read()
    orig = t
    if f == "index.html":
        t = fix_home(t)
    elif f.startswith("best-vpn-for-") or f in ("best-budget-vpn-for-travelers.html", "free-vpn-vs-paid-vpn.html"):
        t = fix_table_rows(t)
        t = fix_notes(t)
        t = add_quick_answer(t, f[:-5])
        if t != orig:
            t = bump_dates(t)
    if t != orig:
        open(f, "w", encoding="utf-8", newline="\r\n").write(t)
        changed.append(f)

sm = open("sitemap.xml", encoding="utf-8").read()
for f in changed:
    if f == "index.html":
        continue
    loc = f"<loc>https://www.travelconnectly.com/{f}</loc>"
    if loc in sm:
        j = sm.index("<lastmod>", sm.index(loc))
        sm = sm[:j] + f"<lastmod>{DATE}" + sm[sm.index("</lastmod>", j):]
open("sitemap.xml", "w", encoding="utf-8", newline="\r\n").write(sm)
print("vpn refresh updated:", ", ".join(changed) or "nothing")
