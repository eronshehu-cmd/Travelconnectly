"""Build saily-vs-holafly.html from the verified country-guide data (prices checked 29 Sep - 10 Oct 2026)."""
import sys

SITE = sys.argv[1]
sys.argv = [sys.argv[0], SITE]
import esim_country_pages as e  # noqa: E402
import pagekit  # noqa: E402
from pagekit import NORD, SAILY, build  # noqa: E402
from saily_vs_airalo import CSS  # noqa: E402  (reuses the comparison-page styles)

HOLAFLY = "https://esim.holafly.com/"
SLUG = "saily-vs-holafly"


def money(v):
    return f"${v:.2f}"


ROWS = []
for c in e.ALL_PAGES:
    u = {r[0]: r for r in c["unl"]}
    ROWS.append(dict(name=c["name"], slug=c["slug"], checked=c.get("checked", e.CHECKED),  # h30 is None where Holafly sells no 30-day plan
                     s7=u[7][1], h7=u[7][3], s15=u[15][1], h15=u[15][3], s30=u[30][1], h30=u[30][3]))
N = len(ROWS)
W7 = sum(r["s7"] < r["h7"] for r in ROWS)
W15 = sum(r["s15"] < r["h15"] for r in ROWS)
W30 = sum(r["h30"] is not None and r["s30"] < r["h30"] for r in ROWS)
N30 = sum(r["h30"] is not None for r in ROWS)
assert (W7, W15, W30, N30) == (17, 20, 18, 19), (W7, W15, W30)
# With Saily's 10% TRAVELCONNECTLY code applied.
C7 = sum(e.code(r["s7"]) < r["h7"] for r in ROWS)
C30 = sum(r["h30"] is not None and e.code(r["s30"]) < r["h30"] for r in ROWS)
assert (C7, C30) == (20, 19), (C7, C30)


def table(days):
    out = []
    for r in ROWS:
        s, h = r[f"s{days}"], r[f"h{days}"]
        if h is None:  # Holafly doesn't sell this length here
            out.append(f'            <tr><td><a href="{r["slug"]}.html">{r["name"]}</a><small>{r["checked"]}</small></td>'
                       f'<td>{money(s)}{e.code_tag(s)}</td><td>—</td><td>Not sold<small>by Holafly</small></td></tr>')
            continue
        cwin = "Saily" if e.code(s) < h else "Holafly"
        cells = (f'<td class="best">{money(s)}{e.code_tag(s)}</td><td>{money(h)}</td>' if s < h
                 else f'<td>{money(s)}{e.code_tag(s)}</td><td class="best">{money(h)}</td>')
        out.append(f'            <tr><td><a href="{r["slug"]}.html">{r["name"]}</a><small>{r["checked"]}</small></td>{cells}'
                   f'<td>{"Saily" if s < h else "Holafly"}<small>by {money(abs(s - h))}</small><small class="code">With code: {cwin}</small></td></tr>')
    return """      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th>Destination</th><th>Saily</th><th>Holafly</th><th>Cheaper</th></tr></thead>
          <tbody>
""" + "\n".join(out) + """
          </tbody>
        </table>
      </div>"""


FEATURES = [
    ("Plan types", "Fixed data (1–20 GB per country) and unlimited", "Unlimited only"),
    ("Unlimited lengths", "Usually 5 to 30 days, including 20 and 25 days", "3 to 30 days in its price tables; other lengths at checkout"),
    ("Speed limits on unlimited", "States 5 GB a day at full speed (3 GB in Canada and Mexico), then up to 1 Mbps", "Fair-usage policy may slow speeds for up to a day, then resets"),
    ("Hotspot sharing", "No hotspot restrictions stated", "1 GB a day"),
    ("Networks named per country", "Sometimes (e.g. Japan, China, Indonesia, Portugal)", "Yes — e.g. Bell and Telus in Canada, Telcel in Mexico"),
    ("Europe-wide plan", "35 countries, incl. UK, Switzerland, Turkey", "33 countries, incl. UK, Switzerland, Andorra; no Turkey"),
    ("Phone number", "Optional US number with a call and text plan, as an add-on", "Data only; no phone number"),
]

FAQ = [
    ("Is Saily cheaper than Holafly?",
     f"Usually, yes. Across {N} destinations checked between 29 September and 10 October 2026, Saily's 7-day unlimited plan was cheaper in {W7} of {N}, its 15-day plan in all {N}, and its 30-day plan in {W30} of the {N30} destinations where Holafly sells one. Mexico, China and Dubai were the exceptions at list price: Holafly was cheaper in Mexico for 7 and 30 days and in China and Dubai for 7 days. With my 10% code TRAVELCONNECTLY, Saily was cheaper for every length Holafly sells, in all {N} destinations."),
    ("Is Holafly really unlimited?",
     "Holafly sells unlimited-data plans, but states a fair-usage policy that can slow speeds for up to a day before resetting, and limits hotspot sharing to 1 GB a day. Saily states its limit up front: 5 GB a day at full speed in most countries (3 GB in Canada and Mexico), then up to 1 Mbps, with no hotspot restrictions."),
    ("Does Holafly sell fixed-data plans?",
     "Not in the destinations I checked — Holafly only sells unlimited plans. If you only need a few gigabytes, Saily's fixed-data plans (and Airalo's) are much cheaper than any unlimited plan."),
    ("Which is better for sharing data with a laptop or friends?",
     "Saily states no hotspot restrictions. Holafly allows sharing 1 GB a day, so a 7-day plan includes 7 GB of hotspot data in total."),
    ("When is Holafly the better choice?",
     "When you want to know which networks you'll use — Holafly names them for each country, such as Telcel in Mexico or Bell and Telus in Canada — when you want WhatsApp to work in China without a separate VPN — Holafly says it does — or when you're going to Mexico and not using a discount code, where its list price was cheaper than Saily's for a week and a month."),
    ("Who makes Saily?",
     "Saily is made by Nord Security, the company behind NordVPN. Its app adds security features such as a virtual location, an ad blocker and protection against malicious sites."),
]


def main_html():
    feat = "\n".join(f"            <tr><td>{k}</td><td>{s}</td><td>{h}</td></tr>" for k, s, h in FEATURES)
    faq_html = "".join(f"\n      <h3>{q}</h3>\n      <p>{a}</p>" for q, a in FAQ)
    guides = " · ".join(f'<a href="{r["slug"]}.html">{r["name"]}</a>' for r in ROWS)
    return f"""  <div class="wrap breadcrumb">
    <a href="index.html">Home</a><span class="sep">/</span><a href="guides.html#esim-countries">eSIM by country</a><span class="sep">/</span>Saily vs Holafly
  </div>

  <div class="wrap qa-top">
    <div class="qa-grid">
      <div class="qa-head">
        <h1>Saily vs Holafly (2026)</h1>
        <div class="qa-sub">{N} destinations · prices checked 29 Sep – 10 Oct 2026</div>
      </div>

      <section class="qa-card" aria-labelledby="qa-title">
        <div class="qa-label"><b>Quick answer</b><span>Most destinations</span></div>
        <div class="qa-prov">
          <div class="qa-logo" aria-hidden="true">S</div>
          <div>
            <h2 id="qa-title">Saily</h2>
            <p>Cheaper unlimited in almost every destination I checked, clearer speed limits, no hotspot cap, and fixed-data plans Holafly doesn't sell.</p>
          </div>
        </div>
        <div class="vs-rows">
          <div class="vs-row"><span class="k">Cheaper unlimited week</span><span class="v s">Saily · {W7} of {N}</span></div>
          <div class="vs-row"><span class="k">Cheaper 15 days</span><span class="v s">Saily · {W15} of {N}</span></div>
        </div>
        <a class="qa-btn" href="{SAILY}" target="_blank" rel="sponsored noopener">See Saily's plans →</a>
        <p class="qa-coupon">With my code <b>TRAVELCONNECTLY</b> (10% off, applied automatically), Saily was cheaper for 7 days in all {N} destinations and for 30 days wherever Holafly sells it.</p>
        <ul class="qa-trust"><li>Prices from each provider's own site</li><li>Exceptions at list price: Mexico, China, Dubai</li><li>I earn a commission from Saily, not Holafly</li></ul>
      </section>

      <section class="qa-take takeaways" aria-labelledby="kt-title">
        <h2 id="kt-title">Key takeaways</h2>
        <ol>
          <li><span><strong>Saily's unlimited was cheaper in {W7} of {N} destinations for a week</strong> and in all {N} for 15 days.</span></li>
          <li><span><strong>The gap grows with trip length:</strong> 30 days in Thailand cost $48.99 at Saily vs $73.90 at Holafly.</span></li>
          <li><span><strong>Holafly only sells unlimited.</strong> For light use, a small fixed plan costs far less.</span></li>
          <li><span><strong>Holafly's strengths:</strong> it names its networks in each country, says WhatsApp works in China without a VPN, and was cheaper in Mexico at list price.</span></li>
        </ol>
      </section>
    </div>

    <div class="author-strip">
      <div class="who">
        <span class="av" aria-hidden="true">E</span>
        <div class="nm"><b>Eron</b> · <span style="display:inline;">Solo traveler &amp; founder</span><span>Prices checked on provider sites · 29 Sep – 10 Oct 2026</span></div>
      </div>
      <a href="methodology.html">How I compare →</a>
    </div>
  </div>

  <div class="wrap">
    <div class="trust-note">
      <p><strong>How this page works:</strong> every price comes from my country guides, where each was checked in US dollars on Saily's and Holafly's own pages between 29 September and 10 October 2026 (the date is next to each destination). Prices change often, so confirm at checkout. I earn a commission from Saily; I have no affiliate relationship with Holafly, and this page shows where Holafly is cheaper.{e.COUPON_NOTE}</p>
    </div>
    <article class="article">
      <p class="lede">Holafly is one of the most advertised travel-eSIM brands, and it sells only unlimited data. Saily sells both unlimited and fixed-data plans. Comparing their unlimited plans destination by destination, Saily was cheaper almost everywhere — but there's one clear exception, and a couple of things Holafly does better.</p>

      <nav class="toc" aria-label="Table of contents">
        <h2>On this page</h2>
        <ol>
          <li><a href="#unlimited-week">Unlimited for a week</a></li>
          <li><a href="#unlimited-month">Unlimited for 30 days</a></li>
          <li><a href="#limits">Speed limits and hotspot</a></li>
          <li><a href="#beyond-price">Beyond price</a></li>
          <li><a href="#which-to-choose">Which one to choose</a></li>
          <li><a href="#frequently-asked-questions">Frequently asked questions</a></li>
        </ol>
      </nav>

      <h2 id="unlimited-week">Unlimited data for a week</h2>
      <p>Price of a 7-day unlimited plan in each destination. Highlighted: the cheaper one at list price. In amber: Saily with my 10% code TRAVELCONNECTLY.</p>
{table(7)}
      <p>Saily was cheaper in {W7} of {N} destinations — by 51 cents in several, but by $7.51 in Canada, $6.51 in Thailand and $3.51 in France. At list price Holafly was $2.49 cheaper in China, $1.09 cheaper in Dubai and 49 cents cheaper in Mexico; with my code, Saily's week is $22.49 in Mexico (Holafly $24.50), $26.99 in China (Holafly $27.50) and $26.09 in Dubai (Holafly $27.90). For 15 days, Saily was cheaper in all {N}.</p>

      <h2 id="unlimited-month">Unlimited data for 30 days</h2>
      <p>Price of a 30-day unlimited plan. Highlighted: the cheaper one at list price. In amber: Saily with my 10% code TRAVELCONNECTLY.</p>
{table(30)}
      <p>Over a month the differences get large: Saily was $24.91 cheaper in Thailand, $13.91 in France and $9.91 in Canada. Holafly doesn't sell a 30-day plan in Dubai, and was $5.49 cheaper in Mexico at list price; with my code, Saily's 30 days in Mexico is $64.79 against $66.50.</p>

      <h2 id="limits">Speed limits and hotspot</h2>
      <p>Neither plan means unlimited full-speed data forever. <strong>Saily</strong> states its allowance: 5 GB a day at full speed in most countries (3 GB in Canada and Mexico), then up to 1 Mbps, with no hotspot restrictions. <strong>Holafly</strong> states a fair-usage policy that can slow speeds for up to a day before resetting, and lets you share 1 GB a day as a hotspot — so a 7-day plan includes 7 GB of hotspot data in total.</p>
      <p>If you'll tether a laptop on mobile data, Saily's terms are more generous. If you mostly use maps, messaging and social media, either will do.</p>

      <h2 id="beyond-price">Beyond price</h2>
      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th></th><th>Saily</th><th>Holafly</th></tr></thead>
          <tbody>
{feat}
          </tbody>
        </table>
      </div>
      <p class="price-note">From each provider's own plan pages for the destinations above, checked 29 September – 10 October 2026.</p>
      <p>Saily plans activate automatically when you arrive and can be activated any time within 180 days of purchase. Saily also adds security features from the NordVPN team and gives 3% of each purchase back as Saily credits.</p>

      <h2 id="which-to-choose">Which one to choose</h2>
      <ul>
        <li><strong>Most trips:</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily</a> — cheaper unlimited in almost every destination, and fixed-data plans if you don't need unlimited.</li>
        <li><strong>Long trips (2 weeks to a month):</strong> Saily, where the gap is biggest.</li>
        <li><strong>Sharing data with a laptop or friends:</strong> Saily, with no stated hotspot cap.</li>
        <li><strong>Mexico:</strong> at list price Holafly was cheaper than Saily for a week and a month, and Airalo cheaper than both; with my code, Saily's unlimited week ($22.49) is the cheapest of the three. See the <a href="best-esim-for-mexico.html">Mexico guide</a>.</li>
        <li><strong>China, if WhatsApp must just work:</strong> Holafly is the only one that says WhatsApp works there without a VPN; see the <a href="best-esim-for-china.html">China guide</a>.</li> Holafly lists them for each country.</li>
      </ul>
      <p>For Saily against Airalo, see <a href="saily-vs-airalo.html">Saily vs Airalo across {N} destinations</a>; for when another provider is the better fit, see <a href="saily-alternatives.html">Saily alternatives</a>. Every destination guide also has a "Find your plan" tool: {guides}.</p>

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
        <a class="related-card" href="best-esim-for-europe.html">
          <span class="tag">eSIM · Europe</span>
          <h3>Best eSIM for Europe (2026)</h3>
        </a>
        <a class="related-card" href="esim-data-calculator.html">
          <span class="tag">Free tool</span>
          <h3>How Much Data Do I Need for My Trip?</h3>
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


pagekit.TODAY = "2026-10-10"
build(
    SLUG,
    "Saily vs Holafly 2026: Unlimited eSIM Prices in 20 Destinations | TravelConnectly",
    f"Saily vs Holafly compared on real, dated unlimited-data prices in {N} destinations, plus speed limits, hotspot rules, networks and which to choose.",
    "Saily vs Holafly, Holafly vs Saily, Holafly alternative, Holafly review, Saily eSIM review, unlimited data eSIM",
    "Saily vs Holafly 2026: Unlimited eSIM Prices in 20 Destinations",
    "Which unlimited eSIM is cheaper, destination by destination, at dated prices.",
    "og-saily-vs-holafly.jpg",
    "Saily vs Holafly (2026): Unlimited eSIM Prices in 20 Destinations",
    FAQ, main_html(),
    f'<a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get Saily</a>',
    f'<div class="sticky-cta" data-custom="plan">\n  <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">See Saily\'s plans →</a>\n'
    f'  <span class="sub">{e.COUPON_STICKY}</span>\n</div>',
    CSS,
)
