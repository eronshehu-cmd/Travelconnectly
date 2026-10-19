"""Refresh VPN prices across the site (and the Black Friday page) and add an answer-first Quick answer card to the VPN guides. Idempotent.

Prices checked 13 Oct 2026 and re-checked 19 Oct 2026 on each provider's pricing page. NordVPN only showed euro prices from Kosovo
(no currency switch); Surfshark and Proton showed US dollars. To update: change VPN and CHECKED, rerun build_all.
"""
import json
import os
import re
import sys

os.chdir(sys.argv[1])
CHECKED = "19 October 2026"
CHECKED_MONTH = "October 2026"
DATE = "2026-10-19"

VPN = {
    "nord": dict(name="NordVPN", host="go.nordvpn.net", rate="€3.49", off="69% off", total="€94.23 for the first 27 months",
                 plan="2-year Basic + 3 months", devices="10 devices", cls="nord", letter="N"),
    "surf": dict(name="Surfshark", host="get.surfshark.net", rate="$2.49", off="87% off", total="$67.23 for the first 27 months",
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


# ---- Black Friday page (refreshed 19 Oct 2026; all three pricing pages re-checked that day).
BF_SLUG = "vpn-black-friday-deals"
BF_CHECKED = "19 October 2026"
MAYA = "https://mayamobile.pxf.io/KBLO5v"
SAILY = "https://go.saily.site/aff_c?offer_id=101&aff_id=16029&coupon=travelconnectly"
BF_STATUS = (f'<p><strong>Deal status (checked {BF_CHECKED}):</strong> NordVPN and Proton VPN haven\'t launched Black Friday '
             "pricing yet. Surfshark already calls its current offer a Black Friday deal, at the same $2.49/mo it charged "
             "before. Black Friday is <strong>Friday 27 November 2026</strong> and Cyber Monday is <strong>Monday 30 November</strong>. "
             "I'll update this page as each sale goes live — until then, the table below is the price any \"deal\" needs to beat.</p>")
BF_NEW_FAQ = ("What is a good VPN Black Friday price in 2026?",
              f"Anything clearly below today's long-term prices in total cost: NordVPN {VPN['nord']['rate']}/mo ({VPN['nord']['total']}), "
              f"Surfshark {VPN['surf']['rate']}/mo ({VPN['surf']['total']}) and Proton VPN {VPN['proton']['rate']}/mo "
              f"({VPN['proton']['total']}), checked {BF_CHECKED}. Compare the total you pay upfront, not the percentage.")
BF_ESIM_FAQ = ("Do eSIMs have Black Friday deals?",
               "Seasonal eSIM deals tend to be discount codes or bonus data, and plans are bought per trip, so there's no need to "
               "stock up. Saily is 10% off all year with my code TRAVELCONNECTLY, and Maya Mobile's global unlimited plan costs "
               "$19.99 for 7 days in any country. Buy close to your departure date.")


def bf_quick_answer():
    v = VPN["nord"]
    href = "https://go.nordvpn.net/aff_c?offer_id=725&aff_id=141128&aff_sub=vpn-black-friday-deals&aff_sub2=quickanswer"
    return f"""
    <section class="qa-card vpn-qa" aria-labelledby="qa-title">
      <div class="qa-label"><b>Quick answer</b><span>Before the sale</span></div>
      <div class="qa-prov">
        <div class="qa-logo nord" aria-hidden="true">N</div>
        <div>
          <h2 id="qa-title">Travelling before late November? Don't wait.</h2>
          <p>NordVPN's 2-year plan is {v['rate']}/mo today ({v['total']}) with a 30-day money-back guarantee. Planning a 2027 trip? Hold any Black Friday offer up against the table below.</p>
        </div>
      </div>
      <span class="qa-plan">{v['plan']} · <strong>{v['rate']}/mo</strong></span>
      <a class="btn btn-nord" href="{href}" target="_blank" rel="sponsored noopener">Get NordVPN →</a>
      <ul class="qa-trust"><li>30-day money-back guarantee</li><li>{v['devices']}</li><li>Black Friday: 27 Nov 2026</li></ul>
    </section>"""


def faq_json(q, a):
    return ('    {\n      "@type": "Question",\n      "name": ' + json.dumps(q) + ',\n      "acceptedAnswer": {\n'
            '        "@type": "Answer",\n        "text": ' + json.dumps(a, ensure_ascii=False) + '\n      }\n    }')


def fix_black_friday(t):
    rows = "\n".join(f'            <tr><td>{v["name"]}</td><td class="price">{v["rate"]}/mo</td><td>{v["total"]}</td><td>{v["plan"]}</td></tr>'
                     for v in VPN.values())
    table = ("<table>\n          <thead><tr><th>Provider</th><th>Price to beat</th><th>First-term total</th><th>Plan</th></tr></thead>\n"
             f"          <tbody>\n{rows}\n          </tbody>\n        </table>")
    t = re.sub(r'(<h2 id="the-prices-to-beat">The prices to beat</h2>\s*<div class="table-wrap glance">\s*)<table>.*?</table>',
               lambda m: m.group(1) + table, t, count=1, flags=re.S)
    t = re.sub(r'(<h2 id="the-prices-to-beat">.*?</table>\s*</div>\s*)<p class="price-note">.*?</p>',
               lambda m: m.group(1) + f'<p class="price-note">{NOTE.replace(CHECKED, BF_CHECKED)}</p>', t, count=1, flags=re.S)
    t = re.sub(r'<p><strong>Deal status \(checked .*?</p>', lambda m: BF_STATUS, t, count=1, flags=re.S)
    t = re.sub(r"(<li><strong>Check what it renews at\.</strong> Introductory prices end\.).*?(</li>)",
               lambda m: m.group(1) + " NordVPN's 2-year Basic plan renews at €139.08 a year and Proton VPN Plus at $83.88 a year "
               f"(from their pricing pages, {BF_CHECKED}). Put a reminder in your calendar for a week before renewal." + m.group(2),
               t, count=1, flags=re.S)
    esim = (f'<h2 id="esim-deals">eSIM deals</h2>\n      <p>eSIM plans are bought per trip, not as subscriptions, so there\'s no point stocking up months ahead — work out the size you need with the <a href="esim-data-calculator.html">trip data calculator</a> and buy close to departure. Two offers that don\'t depend on Black Friday:</p>\n'
            f'      <ul>\n        <li><strong>Saily:</strong> 10% off every plan with my code TRAVELCONNECTLY, applied automatically through my links. <a href="{SAILY}&aff_sub={BF_SLUG}&aff_sub2=content" target="_blank" rel="sponsored noopener">See Saily\'s plans →</a></li>\n'
            f'        <li><strong>Maya Mobile:</strong> one global unlimited plan at the same price in every country — $19.99 for 7 days, $27.99 for 14 (checked {BF_CHECKED}). <a href="{MAYA}?subId1={BF_SLUG}&subId2=content" target="_blank" rel="sponsored noopener">See Maya\'s plans →</a></li>\n'
            '      </ul>\n      <p>For prices in your destination, see the <a href="guides.html#esim-countries">eSIM guides by country</a>.</p>\n\n      ')
    t = re.sub(r'<h2 id="esim-deals">eSIM deals</h2>.*?(?=<h2 id="frequently-asked-questions">)', lambda m: esim, t, count=1, flags=re.S)
    # FAQ (visible + schema): add the price question first, refresh the eSIM answer.
    q, a = BF_NEW_FAQ
    if q not in t:
        t = t.replace('<h2 id="frequently-asked-questions">Frequently asked questions</h2>',
                      f'<h2 id="frequently-asked-questions">Frequently asked questions</h2>\n      <h3>{q}</h3>\n      <p>{a}</p>', 1)
        t = t.replace('"mainEntity": [\n', '"mainEntity": [\n' + faq_json(q, a) + ",\n", 1)
    else:
        t = re.sub(rf"(<h3>{re.escape(q)}</h3>\s*<p>).*?(</p>)", lambda m: m.group(1) + a + m.group(2), t, count=1, flags=re.S)
        t = re.sub(r'("name": ' + re.escape(json.dumps(q)) + r',\s*"acceptedAnswer": \{\s*"@type": "Answer",\s*"text": )".*?"(\s*\})',
                   lambda m: m.group(1) + json.dumps(a, ensure_ascii=False) + m.group(2), t, count=1, flags=re.S)
    q, a = BF_ESIM_FAQ
    t = re.sub(rf"(<h3>{re.escape(q)}</h3>\s*<p>).*?(</p>)", lambda m: m.group(1) + a + m.group(2), t, count=1, flags=re.S)
    t = re.sub(r'("name": ' + re.escape(json.dumps(q)) + r',\s*"acceptedAnswer": \{\s*"@type": "Answer",\s*"text": )".*?"(\s*\})',
               lambda m: m.group(1) + json.dumps(a, ensure_ascii=False) + m.group(2), t, count=1, flags=re.S)
    # Quick answer card above the hero image.
    t = re.sub(r'\n    <section class="qa-card vpn-qa".*?</section>', "", t, flags=re.S)
    t = t.replace('<div class="wrap">\n    <img class="hero-img"', '<div class="wrap">' + bf_quick_answer() + '\n    <img class="hero-img"', 1)
    if "/* end vpn quick answer */" in t:
        t = re.sub(r"/\* vpn quick answer \*/.*?/\* end vpn quick answer \*/\n", lambda _: QA_CSS, t, count=1, flags=re.S)
    else:
        t = t.replace("</style>", QA_CSS + "</style>", 1)
    t = re.sub(r"Last updated: \d+ [A-Za-z]+ 2026", f"Last updated: {BF_CHECKED}", t)
    t = re.sub(r"UPDATED [A-Z]+ 2026", "UPDATED OCTOBER 2026", t)
    return re.sub(r'"dateModified": "[^"]+"', '"dateModified": "2026-10-19"', t, count=1)


changed = []
for f in sorted(os.listdir(".")):
    if not f.endswith(".html"):
        continue
    t = open(f, encoding="utf-8").read()
    orig = t
    if f == "index.html":
        t = fix_home(t)
    elif f == BF_SLUG + ".html":
        t = fix_black_friday(t)
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
