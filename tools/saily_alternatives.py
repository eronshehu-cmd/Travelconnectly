"""Build saily-alternatives.html from the verified country-guide data (prices checked 29 Sep - 12 Oct 2026)."""
import sys

SITE = sys.argv[1]
sys.argv = [sys.argv[0], SITE]
import esim_country_pages as e  # noqa: E402
import pagekit  # noqa: E402
from pagekit import NORD, SAILY, build  # noqa: E402
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
assert (len(AIRALO_10), len(AIRALO_10_CODE), len(SAILY_7), len(SAILY_7_CODE), len(HOLAFLY_BEATS_SAILY_7)) == (12, 6, 13, 20, 3), \
    (len(AIRALO_10), len(AIRALO_10_CODE), len(SAILY_7), len(SAILY_7_CODE), len(HOLAFLY_BEATS_SAILY_7))


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
     f"For fixed amounts of data, Airalo: at list price it was cheaper than Saily for 10 GB valid 30 days in {len(AIRALO_10)} of {N} destinations I checked between 29 September and 12 October 2026, and it sells 7- and 15-day plans and 50 GB plans. For WhatsApp in China without a VPN, or to know the network you'll use, Holafly."),
    ("Is Airalo better than Saily?",
     f"It depends on the plan. Airalo was cheaper for 10 GB in {len(AIRALO_10)} of {N} destinations at list price, while Saily had the cheaper unlimited week in {len(SAILY_7)} of {N}. With my 10% code TRAVELCONNECTLY, Saily was cheaper for an unlimited week in all {N} and Airalo stayed cheaper for 10 GB in {len(AIRALO_10_CODE)}: {names(AIRALO_10_CODE)}."),
    ("Is Holafly better than Saily?",
     f"Holafly only sells unlimited data. At list price it was cheaper than Saily for a week only in {names(HOLAFLY_BEATS_SAILY_7)}. It's the only one of the three that says WhatsApp, Google and Instagram work in China without a separate VPN, and it names its networks in every country."),
    ("Is there a cheaper alternative to Saily?",
     f"For fixed data, often yes — Airalo, by up to $7.99 for 10 GB in Canada. For unlimited data, rarely: Saily was the cheapest unlimited week in {len(SAILY_7)} of {N} destinations at list price, and in all {N} with my code."),
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
        <div class="qa-sub">Airalo and Holafly in {N} destinations · prices checked 29 Sep – 12 Oct 2026</div>
      </div>

      <section class="qa-card" aria-labelledby="qa-title">
        <div class="qa-label"><b>Quick answer</b><span>Best alternative</span></div>
        <h2 id="qa-title" style="font-size:1.25rem;margin:12px 0 0;">Airalo for fixed data. Holafly for China and named networks.</h2>
        <div class="vs-rows">
          <div class="vs-row"><span class="k">Cheaper 10 GB · 30 days (list price)</span><span class="v a">Airalo · {len(AIRALO_10)} of {N}</span></div>
          <div class="vs-row"><span class="k">Cheapest unlimited week (list price)</span><span class="v s">Saily · {len(SAILY_7)} of {N}</span></div>
        </div>
        <a class="qa-btn other" href="{AIRALO}" target="_blank" rel="noopener">See Airalo's plans →</a>
        <p class="qa-note">I don't earn a commission from Airalo.</p>
        <a class="qa-btn" href="{SAILY}" target="_blank" rel="sponsored noopener">Or Saily with 10% off →</a>
        <p class="qa-coupon">With my code <b>TRAVELCONNECTLY</b>, Saily was the cheapest unlimited week in all {N} destinations.</p>
      </section>

      <section class="qa-take takeaways" aria-labelledby="kt-title">
        <h2 id="kt-title">Key takeaways</h2>
        <ol>
          <li><span><strong>Airalo is the main Saily alternative for fixed data</strong> — cheaper for 10 GB in {len(AIRALO_10)} of {N} destinations at list price, with 7- and 15-day plans and 50 GB.</span></li>
          <li><span><strong>For unlimited data, Saily is hard to beat</strong> — the cheapest week in {len(SAILY_7)} of {N} at list price, and in all {N} with my 10% code.</span></li>
          <li><span><strong>Holafly suits China</strong> — the only one that says WhatsApp works there without a VPN — and names its networks everywhere.</span></li>
          <li><span><strong>Even with my code, Airalo stays cheaper for 10 GB</strong> in {names(AIRALO_10_CODE)}.</span></li>
        </ol>
      </section>
    </div>

    <div class="author-strip">
      <div class="who">
        <span class="av" aria-hidden="true">E</span>
        <div class="nm"><b>Eron</b> · <span style="display:inline;">Solo traveler &amp; founder</span><span>Prices checked on provider sites · 29 Sep – 12 Oct 2026</span></div>
      </div>
      <a href="methodology.html">How I compare →</a>
    </div>
  </div>

  <div class="wrap">
    <div class="trust-note">
      <p><strong>How this page works:</strong> every price comes from my destination guides, where each was checked in US dollars on Saily's, Airalo's and Holafly's own pages between 29 September and 12 October 2026 (the date is next to each destination). Prices change often, so confirm at checkout. I earn a commission from Saily; I have no affiliate relationship with Airalo or Holafly, and this page is about when they're the better choice.{e.COUPON_NOTE}</p>
    </div>
    <article class="article">
      <p class="lede">Saily is a strong travel eSIM, but it isn't the cheapest or best fit for every trip. Here's when Airalo or Holafly is the better choice, destination by destination, based on prices I checked on each provider's own site — and when it's worth sticking with Saily.</p>

      <nav class="toc" aria-label="Table of contents">
        <h2>On this page</h2>
        <ol>
          <li><a href="#by-destination">Cheapest option by destination</a></li>
          <li><a href="#airalo">When Airalo is the better choice</a></li>
          <li><a href="#holafly">When Holafly is the better choice</a></li>
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

      <h2 id="stick-with-saily">When to stick with Saily</h2>
      <ul>
        <li><strong>You want unlimited data:</strong> Saily was the cheapest unlimited week in {len(SAILY_7)} of {N} destinations at list price, and in all {N} with my code. It states its full-speed allowance (5 GB a day in most countries) and has no hotspot restrictions.</li>
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
    pagekit.TODAY = "2026-10-12"
    build(
        SLUG,
        "Saily Alternatives 2026: Airalo vs Holafly in 20 Destinations | TravelConnectly",
        f"The best Saily alternatives compared on real, dated prices in {N} destinations: when Airalo or Holafly beats Saily, and when Saily is still the better buy.",
        "Saily alternatives, Saily alternative, eSIM like Saily, Saily vs Airalo, Saily vs Holafly, cheaper than Saily, Saily review",
        "Saily Alternatives 2026: Airalo vs Holafly in 20 Destinations",
        "When Airalo or Holafly beats Saily, destination by destination, at dated prices.",
        "og-saily-alternatives.jpg",
        "Saily Alternatives (2026): Airalo vs Holafly in 20 Destinations",
        FAQ, main_html(),
        f'<a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get Saily</a>',
        f'<div class="sticky-cta" data-custom="plan">\n  <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">See Saily\'s plans →</a>\n'
        f'  <span class="sub">{e.COUPON_STICKY}</span>\n</div>',
        CSS,
    )
