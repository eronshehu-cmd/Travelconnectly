"""Build saily-alternatives.html from the verified country-guide data (prices checked 29 Sep - 13 Oct 2026)."""
import sys

SITE = sys.argv[1]
sys.argv = [sys.argv[0], SITE]
import esim_country_pages as e  # noqa: E402
import pagekit  # noqa: E402
from pagekit import MAYA, NORD, SAILY, build  # noqa: E402
from saily_vs_airalo import CSS  # noqa: E402

AIRALO = "https://www.airalo.com/"
SLUG = "saily-alternatives"


def money(v):
    return f"${v:.2f}"


ROWS = []
for c in e.ALL_PAGES:
    ten = next(r for r in c["fixed"] if r[0] == "10 GB")
    u7 = next(r for r in c["unl"] if r[0] == 7)
    ROWS.append(dict(name=c["name"], slug=c["slug"], checked=c.get("checked", e.CHECKED),
                     s10=next(p for p, d in ten[1] if d == 30), a10=next(p for p, d in ten[2] if d == 30),
                     s7=u7[1], a7=u7[2], h7=u7[3]))
N = len(ROWS)
AIRALO_10 = [r for r in ROWS if r["a10"] < r["s10"]]
AIRALO_10_CODE = [r for r in ROWS if r["a10"] < e.code(r["s10"])]
SAILY_7 = [r for r in ROWS if r["s7"] < min(r["a7"], r["h7"])]
SAILY_7_CODE = [r for r in ROWS if e.code(r["s7"]) < min(r["a7"], r["h7"])]
HOLAFLY_BEATS_SAILY_7 = [r for r in ROWS if r["h7"] < r["s7"]]
assert (len(AIRALO_10), len(AIRALO_10_CODE), len(SAILY_7), len(SAILY_7_CODE), len(HOLAFLY_BEATS_SAILY_7)) == (13, 6, 16, 23, 3), \
    (len(AIRALO_10), len(AIRALO_10_CODE), len(SAILY_7), len(SAILY_7_CODE), len(HOLAFLY_BEATS_SAILY_7))


# ---- Newer alternatives, checked 17 Oct 2026 in USD on each provider's own page (maya.net, kolet.com,
# jetpacglobal.com, roamless.com). Saily prices come from the destination guides (their dates are shown).
NEWER_CHECKED = "17 Oct 2026"
NEWER_DEST = [e.JAPAN, e.USA, e.THAILAND, e.ITALY]
NEWER_PROVIDERS = ["Maya", "Kolet", "Jetpac", "Roamless"]
# 7-day unlimited. Maya sells one global plan at the same price in every country.
NEWER_UNL7 = {
    "Japan": {"Maya": 19.99, "Kolet": 28.63, "Jetpac": 25.99, "Roamless": 23.52},
    "USA": {"Maya": 19.99, "Kolet": 26.11, "Jetpac": 26.99, "Roamless": 24.78},
    "Thailand": {"Maya": 19.99, "Kolet": 25.27, "Jetpac": 20.99, "Roamless": 20.58},
    "Italy": {"Maya": 19.99, "Kolet": 25.55, "Jetpac": 20.00, "Roamless": 22.68},
}
# 10 GB valid 30 days. Maya sells no fixed-data plans; Jetpac's Italy 10 GB lasts 7 days only.
NEWER_TEN = {
    "Japan": {"Kolet": 21.99, "Jetpac": 16.00, "Roamless": 14.95},
    "USA": {"Kolet": 21.99, "Jetpac": 19.00, "Roamless": 22.45},
    "Thailand": {"Kolet": 11.99, "Jetpac": 11.50, "Roamless": 10.95},
    "Italy": {"Kolet": 18.99, "Jetpac": None, "Roamless": 18.95},
}


def saily_of(c):
    ten = next(r for r in c["fixed"] if r[0] == "10 GB")
    return next(r for r in c["unl"] if r[0] == 7)[1], next(p for p, d in ten[1] if d == 30)


def newer_table(kind):
    provs = NEWER_PROVIDERS if kind == "unl" else NEWER_PROVIDERS[1:]
    data = NEWER_UNL7 if kind == "unl" else NEWER_TEN
    out = []
    for c in NEWER_DEST:
        s7, s10 = saily_of(c)
        s = s7 if kind == "unl" else s10
        prices = {"Saily": s, **data[c["name"]]}
        low = min(p for p in prices.values() if p is not None)
        cells = "".join(
            "<td>—</td>" if prices[p] is None else
            f'<td{" class=\"best\"" if prices[p] == low else ""}>{money(prices[p])}'
            f'{e.code_tag(prices[p]) if p == "Saily" else ""}</td>'
            for p in ["Saily"] + provs)
        out.append(f'            <tr><td><a href="{c["slug"]}.html">{c["name"]}</a></td>{cells}</tr>')
    head = "".join(f"<th>{p}</th>" for p in ["Saily"] + provs)
    return f"""      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th>Destination</th>{head}</tr></thead>
          <tbody>
""" + "\n".join(out) + """
          </tbody>
        </table>
      </div>"""


MAYA_WINS = sum(NEWER_UNL7[c["name"]]["Maya"] < min(saily_of(c)[0], *[v for k, v in NEWER_UNL7[c["name"]].items() if k != "Maya"])
                for c in NEWER_DEST)
MAYA_BEATS_CODE = [c["name"] for c in NEWER_DEST if NEWER_UNL7[c["name"]]["Maya"] < e.code(saily_of(c)[0])]
assert (MAYA_WINS, MAYA_BEATS_CODE) == (4, ["Japan", "USA", "Italy"]), (MAYA_WINS, MAYA_BEATS_CODE)


def names(rows):
    n = [r["name"] for r in rows]
    return ", ".join(n[:-1]) + " and " + n[-1] if len(n) > 1 else n[0]


def table():
    out = []
    for r in ROWS:
        ten = ("Airalo", r["a10"]) if r["a10"] < r["s10"] else ("Saily", r["s10"])
        week = min((("Saily", r["s7"]), ("Airalo", r["a7"]), ("Holafly", r["h7"])), key=lambda x: x[1])
        out.append(
            f'            <tr><td><a href="{r["slug"]}.html">{r["name"]}</a><small>{r["checked"]}</small></td>'
            f'<td>{ten[0]}<small>{money(ten[1])}</small></td>'
            f'<td>{week[0]}<small>{money(week[1])}</small></td>'
            f'<td>{money(e.code(r["s10"]))}<small>{money(e.code(r["s7"]))} week</small></td></tr>')
    return """      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th>Destination</th><th>Cheapest 10 GB · 30 days</th><th>Cheapest unlimited week</th><th>Saily with code</th></tr></thead>
          <tbody>
""" + "\n".join(out) + """
          </tbody>
        </table>
      </div>"""


FAQ = [
    ("What is the best alternative to Saily?",
     f"For the cheapest unlimited data, Maya Mobile ($19.99 a week in any country, checked {NEWER_CHECKED}). For fixed amounts of data, Airalo: at list price it was cheaper than Saily for 10 GB valid 30 days in {len(AIRALO_10)} of {N} destinations I checked between 29 September and 13 October 2026, and it sells 7- and 15-day plans and 50 GB plans. For WhatsApp in China without a VPN, or to know the network you'll use, Holafly."),
    ("Is Airalo better than Saily?",
     f"It depends on the plan. Airalo was cheaper for 10 GB in {len(AIRALO_10)} of {N} destinations at list price, while Saily had the cheaper unlimited week in {len(SAILY_7)} of {N}. With my 10% code TRAVELCONNECTLY, Saily was cheaper for an unlimited week in all {N} and Airalo stayed cheaper for 10 GB in {len(AIRALO_10_CODE)}: {names(AIRALO_10_CODE)}."),
    ("Is Holafly better than Saily?",
     f"Holafly only sells unlimited data. At list price it was cheaper than Saily for a week only in {names(HOLAFLY_BEATS_SAILY_7)}. It's the only one of the three that says WhatsApp, Google and Instagram work in China without a separate VPN, and it names its networks in every country."),
    ("Is there a cheaper alternative to Saily?",
     f"For fixed data, often yes — Airalo, by up to $7.99 for 10 GB in Canada, and Roamless or Jetpac in some countries. For unlimited data, Maya Mobile: its global plan cost $19.99 for 7 days in every country, which was the cheapest unlimited week in all four destinations I checked on {NEWER_CHECKED} (Japan, USA, Thailand, Italy). Against Airalo and Holafly, Saily was the cheapest unlimited week in {len(SAILY_7)} of {N} destinations."),
    ("Saily vs Maya Mobile: which is cheaper?",
     "For unlimited data, Maya. On 17 October 2026 Maya's global plan cost $19.99 for 7 days, $27.99 for 14 and $49.99 for 30, the same in every country, against $20.99–26.99 for a Saily unlimited week in Japan, the USA, Thailand and Italy. With my code Saily was cheaper only in Thailand ($18.89). Maya says it never caps or throttles speeds and allows hotspot use, though its acceptable use policy lets it deprioritise unusual usage during congestion; Saily states 5 GB a day at full speed, then up to 1 Mbps. Maya sells no fixed-data plans."),
    ("Saily vs Kolet: which is cheaper?",
     "Usually Saily. Kolet's unlimited week cost $25.27–28.63 in the four destinations I checked, more than Saily in each; its 10 GB for 30 days was cheaper than Saily's list price in the USA ($21.99 vs $22.99) and Italy ($18.99 vs $20.99). Kolet lets you turn unused data into credit and transfer data to someone else."),
    ("Saily vs Jetpac: which is cheaper?",
     "It's close. Jetpac's unlimited week was cheaper than Saily's list price in Japan ($25.99) and Italy ($20.00) and tied in Thailand ($20.99), but its unlimited plans give 3 GB a day at full speed against Saily's 5 GB. Jetpac had the cheapest 10 GB for 30 days in the USA ($19.00)."),
    ("Saily vs Roamless: which is cheaper?",
     "For fixed data, often Roamless: 10 GB for 30 days was below Saily's list price in all four destinations I checked, for example $14.95 in Japan and $10.95 in Thailand. Its unlimited plans give 3 GB a day at full speed and cost $20.58–24.78 a week. Roamless also offers pay-as-you-go credits that don't expire."),
    ("Does Saily have a discount code?",
     "Yes. My code TRAVELCONNECTLY gives 10% off Saily plans, and my Saily links apply it automatically."),
]


def main_html():
    faq_html = "".join(f"\n      <h3>{q}</h3>\n      <p>{a}</p>" for q, a in FAQ)
    airalo_wins = "\n".join(
        f'        <li><a href="{r["slug"]}.html">{r["name"]}</a>: Airalo {money(r["a10"])} vs Saily {money(r["s10"])}'
        f'{" — still cheaper than Saily with my code (" + money(e.code(r["s10"])) + ")" if r in AIRALO_10_CODE else ""}.</li>'
        for r in sorted(AIRALO_10, key=lambda r: r["s10"] - r["a10"]))
    return f"""  <div class="wrap breadcrumb">
    <a href="index.html">Home</a><span class="sep">/</span><a href="guides.html#esim-countries">eSIM by country</a><span class="sep">/</span>Saily alternatives
  </div>

  <div class="wrap qa-top">
    <div class="qa-grid">
      <div class="qa-head">
        <h1>Saily Alternatives (2026)</h1>
        <div class="qa-sub">Airalo, Holafly, Maya, Kolet, Jetpac and Roamless · prices checked 29 Sep – 17 Oct 2026</div>
      </div>

      <section class="qa-card" aria-labelledby="qa-title">
        <div class="qa-label"><b>Quick answer</b><span>Best alternative</span></div>
        <h2 id="qa-title" style="font-size:1.25rem;margin:12px 0 0;">Maya for cheap unlimited. Airalo for fixed data. Holafly for China.</h2>
        <div class="vs-rows">
          <div class="vs-row"><span class="k">Cheapest unlimited week ({NEWER_CHECKED})</span><span class="v a">Maya · {MAYA_WINS} of {len(NEWER_DEST)}</span></div>
          <div class="vs-row"><span class="k">Cheaper 10 GB · 30 days (list price)</span><span class="v a">Airalo · {len(AIRALO_10)} of {N}</span></div>
          <div class="vs-row"><span class="k">Unlimited week vs Airalo &amp; Holafly</span><span class="v s">Saily · {len(SAILY_7)} of {N}</span></div>
        </div>
        <a class="qa-btn other" href="{MAYA}" target="_blank" rel="sponsored noopener">See Maya's global unlimited →</a>
        <a class="qa-btn other" href="{AIRALO}" target="_blank" rel="noopener">See Airalo's plans →</a>
        <p class="qa-note">I don't earn a commission from Airalo.</p>
        <a class="qa-btn" href="{SAILY}" target="_blank" rel="sponsored noopener">Or Saily with 10% off →</a>
        <p class="qa-coupon">With my code <b>TRAVELCONNECTLY</b>, Saily beat Airalo and Holafly for an unlimited week in all {N} destinations.</p>
      </section>

      <section class="qa-take takeaways" aria-labelledby="kt-title">
        <h2 id="kt-title">Key takeaways</h2>
        <ol>
          <li><span><strong>Airalo is the main Saily alternative for fixed data</strong> — cheaper for 10 GB in {len(AIRALO_10)} of {N} destinations at list price, with 7- and 15-day plans and 50 GB.</span></li>
          <li><span><strong>Cheapest unlimited: Maya Mobile</strong> — one global plan at $19.99 a week in every country, cheaper than Saily even with my code in {", ".join(MAYA_BEATS_CODE[:-1])} and {MAYA_BEATS_CODE[-1]}. Maya says it doesn't cap or throttle speeds.</span></li>
          <li><span><strong>Against Airalo and Holafly, Saily wins on unlimited</strong> — the cheapest week in {len(SAILY_7)} of {N} at list price, and in all {N} with my 10% code.</span></li>
          <li><span><strong>Holafly suits China</strong> — the only one that says WhatsApp works there without a VPN — and names its networks everywhere.</span></li>
          <li><span><strong>Even with my code, Airalo stays cheaper for 10 GB</strong> in {names(AIRALO_10_CODE)}.</span></li>
        </ol>
      </section>
    </div>

    <div class="author-strip">
      <div class="who">
        <span class="av" aria-hidden="true">E</span>
        <div class="nm"><b>Eron</b> · <span style="display:inline;">Solo traveler &amp; founder</span><span>Prices checked on provider sites · 29 Sep – 17 Oct 2026</span></div>
      </div>
      <a href="methodology.html">How I compare →</a>
    </div>
  </div>

  <div class="wrap">
    <div class="trust-note">
      <p><strong>How this page works:</strong> every price comes from my destination guides, where each was checked in US dollars on Saily's, Airalo's and Holafly's own pages between 29 September and 13 October 2026 (the date is next to each destination). Prices change often, so confirm at checkout. I earn a commission from Saily and Maya Mobile; I have no affiliate relationship with Airalo, Holafly, Kolet, Jetpac or Roamless, and this page is about when they're the better choice.{e.COUPON_NOTE}</p>
    </div>
    <article class="article">
      <p class="lede">Saily is a strong travel eSIM, but it isn't the cheapest or best fit for every trip. Here's when Airalo, Holafly or one of the newer global eSIMs — Maya Mobile, Kolet, Jetpac and Roamless — is the better choice, based on prices I checked on each provider's own site — and when it's worth sticking with Saily.</p>

      <nav class="toc" aria-label="Table of contents">
        <h2>On this page</h2>
        <ol>
          <li><a href="#by-destination">Cheapest option by destination</a></li>
          <li><a href="#airalo">When Airalo is the better choice</a></li>
          <li><a href="#holafly">When Holafly is the better choice</a></li>
          <li><a href="#newer-alternatives">Maya, Kolet, Jetpac and Roamless</a></li>
          <li><a href="#stick-with-saily">When to stick with Saily</a></li>
          <li><a href="#frequently-asked-questions">Frequently asked questions</a></li>
        </ol>
      </nav>

      <h2 id="by-destination">Cheapest option by destination</h2>
      <p>The cheapest 10 GB plan valid 30 days and the cheapest 7-day unlimited plan among Saily, Airalo and Holafly at list price, plus Saily's price with my 10% code.</p>
{table()}

      <h2 id="airalo">When Airalo is the better choice</h2>
      <ul>
        <li><strong>You want a fixed amount of data.</strong> At list price Airalo was cheaper for 10 GB valid 30 days in {len(AIRALO_10)} of {N} destinations (gaps below).</li>
        <li><strong>Your trip fits a short window.</strong> Airalo sells 3-, 7- and 15-day fixed plans; Saily's fixed plans mostly last 30 days.</li>
        <li><strong>You need a lot of data.</strong> Airalo sells 50 GB in 17 of the 19 single countries I checked; Saily's single-country plans top out at 20 GB.</li>
        <li><strong>You're visiting the western Balkans or Ukraine on a Europe trip.</strong> Airalo's Europe plan covers 41 countries including them; Saily's covers 35. See the <a href="best-esim-for-europe.html">Europe guide</a>.</li>
      </ul>
      <p>Where Airalo's 10 GB for 30 days was cheaper than Saily's at list price, smallest gap first:</p>
      <ul>
{airalo_wins}
      </ul>

      <h2 id="holafly">When Holafly is the better choice</h2>
      <ul>
        <li><strong>China, if WhatsApp must just work.</strong> Holafly says WhatsApp, Google and Instagram work with its China eSIM without a separate VPN. Saily says Google and Instagram work through its app's virtual location, but WhatsApp needs a VPN. See the <a href="best-esim-for-china.html">China guide</a>.</li>
        <li><strong>You want to know the network.</strong> Holafly names its networks in every country — for example Telcel in Mexico, Bell and Telus in Canada.</li>
        <li><strong>Mexico at list price.</strong> Holafly's unlimited week ($24.50) was 49 cents below Saily's — though Airalo was cheaper than both, and Saily with my code is cheaper still ($22.49).</li>
      </ul>
      <p>Holafly only sells unlimited data, limits hotspot sharing to 1 GB a day, and was more expensive than Saily for a week in {N - len(HOLAFLY_BEATS_SAILY_7)} of {N} destinations. See <a href="saily-vs-holafly.html">Saily vs Holafly</a>.</p>

      <h2 id="newer-alternatives">Maya, Kolet, Jetpac and Roamless</h2>
      <p>Four newer travel eSIMs come up often as Saily alternatives. I checked their prices in four popular destinations on {NEWER_CHECKED}, in US dollars on each provider's own page; Saily's prices are from my destination guides. Highlighted: the cheapest at list price. Each of them also advertises a first-purchase discount code on its own site.</p>
      <h3>Unlimited data for 7 days</h3>
{newer_table("unl")}
      <h3>10 GB valid 30 days</h3>
{newer_table("ten")}
      <p class="price-note">Maya, Kolet, Jetpac and Roamless checked {NEWER_CHECKED}; Saily from the linked guides. Maya sells unlimited plans only; Jetpac's 10 GB plan in Italy lasts 7 days, so it isn't listed.</p>
      <ul>
        <li><strong><a href="{MAYA}" target="_blank" rel="sponsored noopener">Maya Mobile</a> — the cheapest unlimited.</strong> One global plan with the same price in every country: $9.99 for 3 days, $19.99 for 7, $27.99 for 14 and $49.99 for 30. Its coverage list includes 188 countries, Kosovo among them. Maya says it never caps or throttles speeds and allows hotspot use; its acceptable use policy lets it deprioritise usage that isn't normal individual use during network congestion. No auto-renew unless you turn on Auto Top-Up, and no fixed-data plans.</li>
        <li><strong>Kolet — flexible, but not the cheapest.</strong> Fixed plans last 30 days, and unlimited is priced by the day with 5 GB a day at full speed. It was more expensive than Saily for an unlimited week in all four destinations. You can turn unused data into credit or transfer it to someone else.</li>
        <li><strong>Jetpac — cheap fixed data in some countries.</strong> Cheapest 10 GB for 30 days in the USA ($19.00) and an unlimited week below Saily's list price in Japan and Italy. Its unlimited plans give 3 GB a day at full speed, then up to 1 Mbps.</li>
        <li><strong>Roamless — cheap fixed data and pay-as-you-go.</strong> The cheapest 10 GB for 30 days in Japan ($14.95), Thailand ($10.95) and Italy ($18.95) at list price, plus credits that never expire. Unlimited gives 3 GB a day at full speed.</li>
      </ul>
      <p>With my 10% code, Saily's 10 GB was the cheapest of the five in Thailand ($9.89) and Italy ($18.89), and its unlimited week was the cheapest in Thailand ($18.89).</p>

      <h2 id="stick-with-saily">When to stick with Saily</h2>
      <ul>
        <li><strong>You want unlimited data with a stated allowance:</strong> against Airalo and Holafly, Saily was the cheapest unlimited week in {len(SAILY_7)} of {N} destinations at list price, and in all {N} with my code. It states 5 GB a day at full speed in most countries — more than Jetpac's and Roamless's 3 GB — and has no hotspot restrictions. Maya is cheaper and says it doesn't cap speeds at all.</li>
        <li><strong>Your dates might change:</strong> its fixed plans almost all last 30 days.</li>
        <li><strong>You want extras:</strong> an optional US phone number, security features from the NordVPN team and 3% back in Saily credits.</li>
      </ul>
      <p>For the full head-to-head, see <a href="saily-vs-airalo.html">Saily vs Airalo</a> and <a href="saily-vs-holafly.html">Saily vs Holafly</a>.</p>

      <h2 id="frequently-asked-questions">Frequently asked questions</h2>{faq_html}
    </article>
  </div>

  <section class="related">
    <div class="wrap">
      <div class="section-head" style="margin-bottom:28px;">
        <div class="eyebrow">KEEP READING</div>
        <h2>Related guides</h2>
      </div>
      <div class="related-grid">
        <a class="related-card" href="saily-vs-airalo.html">
          <span class="tag">eSIM · Comparison</span>
          <h3>Saily vs Airalo (2026)</h3>
        </a>
        <a class="related-card" href="saily-vs-holafly.html">
          <span class="tag">eSIM · Comparison</span>
          <h3>Saily vs Holafly (2026)</h3>
        </a>
        <a class="related-card" href="best-esim-for-travelers.html">
          <span class="tag">eSIM</span>
          <h3>Best eSIM for Travelers</h3>
        </a>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="cta-band">
        <div class="eyebrow" style="justify-content:center;">STILL DECIDING?</div>
        <h2>Pick your destination, then your plan</h2>
        <p>Each destination guide compares Saily, Airalo and Holafly at dated prices. Saily is 10% off with code TRAVELCONNECTLY, applied automatically through my links.</p>
        <div class="hero-ctas">
          <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily" style="width:auto;">See Saily's plans →</a>
          <a href="{NORD}" target="_blank" rel="sponsored noopener" class="btn btn-nord" style="width:auto;">Get NordVPN →</a>
        </div>
      </div>
    </div>
  </section>"""


if __name__ == "__main__":
    pagekit.TODAY = "2026-10-17"
    build(
        SLUG,
        "Saily Alternatives 2026: Airalo, Holafly, Maya, Kolet, Jetpac and Roamless | TravelConnectly",
        f"The best Saily alternatives compared on real, dated prices: Airalo and Holafly in {N} destinations, plus Maya Mobile, Kolet, Jetpac and Roamless — when each beats Saily, and when Saily is still the better buy.",
        "Saily alternatives, Saily alternative, eSIM like Saily, Saily vs Airalo, Saily vs Holafly, Saily vs Maya, Saily vs Kolet, Saily vs Jetpac, Saily vs Roamless, cheaper than Saily",
        "Saily Alternatives 2026: Airalo, Holafly, Maya, Kolet, Jetpac and Roamless",
        "When Airalo, Holafly, Maya, Kolet, Jetpac or Roamless beats Saily, at dated prices.",
        "og-saily-alternatives.jpg",
        "Saily Alternatives (2026): Airalo, Holafly, Maya, Kolet, Jetpac and Roamless Compared",
        FAQ, main_html(),
        f'<a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get Saily</a>',
        f'<div class="sticky-cta" data-custom="plan">\n  <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">See Saily\'s plans →</a>\n'
        f'  <span class="sub">{e.COUPON_STICKY}</span>\n</div>',
        CSS,
    )
