"""Build saily-vs-airalo.html from the verified country-guide data (prices checked 29 Sep - 13 Oct 2026)."""
import sys

SITE = sys.argv[1]
sys.argv = [sys.argv[0], SITE]
import esim_country_pages as e  # noqa: E402
import pagekit  # noqa: E402
from pagekit import NORD, SAILY, build  # noqa: E402

AIRALO = "https://www.airalo.com/"
SLUG = "saily-vs-airalo"


def money(v):
    return f"${v:.2f}"


def head_to_head():
    rows = []
    for c in e.ALL_PAGES:
        ten = next(r for r in c["fixed"] if r[0] == "10 GB")
        u7 = next(r for r in c["unl"] if r[0] == 7)
        rows.append(dict(
            name=c["name"], slug=c["slug"], checked=c.get("checked", e.CHECKED),
            s10=next(p for p, d in ten[1] if d == 30), a10=next(p for p, d in ten[2] if d == 30),
            s7=u7[1], a7=u7[2]))
    return rows


ROWS = head_to_head()
UNL_SAILY = sum(r["s7"] < r["a7"] for r in ROWS)
UNL_AIRALO = sum(r["a7"] < r["s7"] for r in ROWS)
TEN_SAILY = sum(r["s10"] < r["a10"] for r in ROWS)
TEN_AIRALO = sum(r["a10"] < r["s10"] for r in ROWS)
N = len(ROWS)
assert (UNL_SAILY, UNL_AIRALO, TEN_SAILY, TEN_AIRALO) == (16, 7, 10, 13), (UNL_SAILY, UNL_AIRALO, TEN_SAILY, TEN_AIRALO)
# With Saily's 10% TRAVELCONNECTLY code applied.
UNL_CODE = sum(e.code(r["s7"]) < r["a7"] for r in ROWS)
TEN_CODE = sum(e.code(r["s10"]) < r["a10"] for r in ROWS)
assert (UNL_CODE, TEN_CODE) == (23, 17), (UNL_CODE, TEN_CODE)
CODE_SUMMARY = (f'<p class="qa-coupon">With my code <b>TRAVELCONNECTLY</b> (10% off, applied automatically), Saily was cheaper '
                f'for an unlimited week in all {N} destinations and for 10 GB in {TEN_CODE} of {N}.</p>')


def table(kind):
    s_key, a_key = ("s7", "a7") if kind == "unl" else ("s10", "a10")
    out = []
    for r in ROWS:
        s, a = r[s_key], r[a_key]
        sc = e.code(s)
        winner = "Saily" if s < a else "Airalo"
        cwin = "Saily" if sc < a else "Airalo"
        cells = (f'<td class="best">{money(s)}{e.code_tag(s)}</td><td>{money(a)}</td>' if s < a
                 else f'<td>{money(s)}{e.code_tag(s)}</td><td class="best">{money(a)}</td>')
        out.append(f'            <tr><td><a href="{r["slug"]}.html">{r["name"]}</a><small>{r["checked"]}</small></td>{cells}'
                   f'<td>{winner}<small>by {money(abs(s - a))}</small><small class="code">With code: {cwin}</small></td></tr>')
    return """      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th>Destination</th><th>Saily</th><th>Airalo</th><th>Cheaper</th></tr></thead>
          <tbody>
""" + "\n".join(out) + """
          </tbody>
        </table>
      </div>"""


CSS = e.CSS + """
.vs-rows{ margin-top:12px; display:flex; flex-direction:column; gap:8px; }
.vs-row{ display:flex; justify-content:space-between; align-items:center; gap:12px; padding:12px 14px; background:var(--navy-panel-2); border:1px solid #2A4563; border-radius:12px; }
.vs-row .k{ font-size:0.875rem; color:#C9D5E2; }
.vs-row .v{ font-family:'Space Grotesk',sans-serif; font-weight:600; white-space:nowrap; }
.vs-row .v.s{ color:var(--saily-purple-text); }
.vs-row .v.a{ color:var(--teal); }
.qa-alt{ display:flex; align-items:center; justify-content:center; min-height:48px; margin-top:8px; border:1.5px solid var(--teal); border-radius:12px; color:var(--teal); font-weight:600; text-decoration:none; }
.qa-alt:hover{ background:rgba(63,217,199,.08); }
.glance table.cov td a{ color:var(--text-light); text-decoration:underline; text-underline-offset:3px; }
.glance table.cov td:first-child{ text-align:left; }
"""

FEATURES = [
    ("Fixed-data validity", "Mostly 30 days (1 GB plans: 7 days)", "3, 7, 15 or 30 days, depending on the plan"),
    ("Biggest single-country plan", "20 GB in the 19 countries checked", "50 GB in 17 of those 19 countries"),
    ("Unlimited lengths", "Usually 5 to 30 days, including 20 and 25 days; 1 or 3 days in some countries", "3, 5, 7, 10, 15 or 30 days"),
    ("Unlimited full-speed allowance stated", "5 GB a day (3 GB in Canada and Mexico), then up to 1 Mbps", "Not listed on the country pages I checked"),
    ("Networks named on plan pages", "Sometimes (e.g. Japan, China, Indonesia, Portugal)", "Usually names the primary network"),
    ("Europe-wide plan", "35 countries, incl. UK, Switzerland, Turkey", "41 countries, incl. western Balkans and Ukraine; EU + UK plan (28)"),
    ("Calls and texts", "Optional US phone number with a call and text plan, as an add-on", "Lists data, calls and texts eSIMs for some destinations, e.g. Canada"),
]

FAQ = [
    ("Is Saily cheaper than Airalo?",
     f"It depends on the plan. Across {N} destinations checked between 29 September and 13 October 2026, Saily was cheaper for a 7-day unlimited plan in {UNL_SAILY} of {N}, while Airalo was cheaper for 10 GB valid 30 days in {TEN_AIRALO} of {N}. Most differences were under $1. With my 10% code TRAVELCONNECTLY, Saily was cheaper for an unlimited week in all {N} and for 10 GB in {TEN_CODE} of {N}."),
    ("Which is better for unlimited data, Saily or Airalo?",
     f"Saily had the cheaper 7-day unlimited plan in {UNL_SAILY} of {N} destinations, usually by a cent, and by about $3 in Canada. It also states its full-speed allowance (5 GB a day in most countries, 3 GB in Canada and Mexico) and sells 20- and 25-day plans. Airalo was cheaper for a week in Japan, Turkey, France, Mexico, China, Dubai and Australia at list price."),
    ("Which is better for fixed data?",
     f"Airalo was cheaper for 10 GB valid 30 days in {TEN_AIRALO} of {N} destinations, by up to about $8 in Canada, and sells shorter 7- and 15-day plans and 50 GB plans in most countries. Saily was a cent cheaper in Japan, Thailand, the UK, France, South Korea, Dubai, Vietnam, Australia, the Philippines and Singapore."),
    ("Which has the better Europe plan?",
     "Airalo's Europe plan covers more countries (41, including the western Balkans and Ukraine), and its EU + UK plan is cheaper if you stay in the EU and the UK. Saily's Europe plan covers 35 countries including the UK, Switzerland and Turkey, and had the cheaper 7-day unlimited plan. Neither Europe plan covers Kosovo; Saily's separate Balkans plan does."),
    ("Who makes Saily?",
     "Saily is made by Nord Security, the company behind NordVPN. Its app adds security features such as a virtual location, an ad blocker and protection against malicious sites."),
    ("Can I have both on my phone?",
     "Yes. Most eSIM phones can store several eSIMs, so you can install one from each and switch the data line in your settings."),
]


def main_html():
    feat = "\n".join(f"            <tr><td>{k}</td><td>{s}</td><td>{a}</td></tr>" for k, s, a in FEATURES)
    faq_html = "".join(f"\n      <h3>{q}</h3>\n      <p>{a}</p>" for q, a in FAQ)
    guides = " · ".join(f'<a href="{r["slug"]}.html">{r["name"]}</a>' for r in ROWS)
    return f"""  <div class="wrap breadcrumb">
    <a href="index.html">Home</a><span class="sep">/</span><a href="guides.html#esim-countries">eSIM by country</a><span class="sep">/</span>Saily vs Airalo
  </div>

  <div class="wrap qa-top">
    <div class="qa-grid">
      <div class="qa-head">
        <h1>Saily vs Airalo (2026)</h1>
        <div class="qa-sub">{N} destinations · prices checked 29 Sep – 13 Oct 2026</div>
      </div>

      <section class="qa-card" aria-labelledby="qa-title">
        <div class="qa-label"><b>Quick answer</b><span>It depends on the plan</span></div>
        <h2 id="qa-title" style="font-size:1.25rem;margin:12px 0 0;">Unlimited → Saily. Fixed data → it depends on the country.</h2>
        <div class="vs-rows">
          <div class="vs-row"><span class="k">Cheaper unlimited week (list price)</span><span class="v s">Saily · {UNL_SAILY} of {N}</span></div>
          <div class="vs-row"><span class="k">Cheaper 10 GB · 30 days (list price)</span><span class="v a">Airalo · {TEN_AIRALO} of {N}</span></div>
        </div>
        <a class="qa-btn" href="{SAILY}" target="_blank" rel="sponsored noopener">See Saily's plans →</a>
        {CODE_SUMMARY}
        <a class="qa-alt" href="{AIRALO}" target="_blank" rel="noopener">See Airalo's plans →</a>
        <ul class="qa-trust"><li>Prices from each provider's own site</li><li>I earn a commission from Saily, not Airalo</li></ul>
      </section>

      <section class="qa-take takeaways" aria-labelledby="kt-title">
        <h2 id="kt-title">Key takeaways</h2>
        <ol>
          <li><span><strong>Unlimited: Saily was cheaper in {UNL_SAILY} of {N} destinations</strong> — usually by a cent, but by $3.01 in Canada.</span></li>
          <li><span><strong>10 GB for 30 days: Airalo was cheaper in {TEN_AIRALO} of {N}</strong> at list price — by $7.99 in Canada, $5.99 in Portugal and $5.49 in Mexico.</span></li>
          <li><span><strong>With my 10% code TRAVELCONNECTLY,</strong> Saily was cheaper for an unlimited week in all {N} destinations and for 10 GB in {TEN_CODE} of {N}.</span></li>
          <li><span><strong>Airalo has more plan shapes:</strong> 7- and 15-day fixed plans and 50 GB in most countries. Saily's fixed plans mostly last 30 days.</span></li>
          <li><span><strong>Saily states its limits:</strong> 5 GB a day at full speed on unlimited (3 GB in Canada and Mexico) and no hotspot restrictions.</span></li>
        </ol>
      </section>
    </div>

    <div class="author-strip">
      <div class="who">
        <span class="av" aria-hidden="true">E</span>
        <div class="nm"><b>Eron</b> · <span style="display:inline;">Solo traveler &amp; founder</span><span>Prices checked on provider sites · 29 Sep – 13 Oct 2026</span></div>
      </div>
      <a href="methodology.html">How I compare →</a>
    </div>
  </div>

  <div class="wrap">
    <div class="trust-note">
      <p><strong>How this page works:</strong> every price comes from my country guides, where each was checked in US dollars on Saily's and Airalo's own pages between 29 September and 13 October 2026 (the date is next to each destination). Prices change often, so confirm at checkout. I earn a commission from Saily; I have no affiliate relationship with Airalo, and this page shows where Airalo is cheaper.{e.COUPON_NOTE}</p>
    </div>
    <article class="article">
      <p class="lede">Saily and Airalo are two of the biggest travel-eSIM brands, and they're close on price more often than not. The real difference is which kind of plan you want: in my checks, Saily was usually cheaper for unlimited data and Airalo for fixed data. Here's the destination-by-destination picture.</p>

      <nav class="toc" aria-label="Table of contents">
        <h2>On this page</h2>
        <ol>
          <li><a href="#unlimited-week">Unlimited for a week</a></li>
          <li><a href="#ten-gb">10 GB for 30 days</a></li>
          <li><a href="#big-gaps">Where the gap is big</a></li>
          <li><a href="#beyond-price">Beyond price</a></li>
          <li><a href="#which-to-choose">Which one to choose</a></li>
          <li><a href="#frequently-asked-questions">Frequently asked questions</a></li>
        </ol>
      </nav>

      <h2 id="unlimited-week">Unlimited data for a week</h2>
      <p>Price of a 7-day unlimited plan in each destination. Highlighted: the cheaper one at list price. In amber: Saily with my 10% code TRAVELCONNECTLY.</p>
{table("unl")}
      <p>Saily was cheaper in {UNL_SAILY} of {N} destinations, in thirteen of them by a single cent. The biggest gaps: Canada (Saily $3.01 cheaper), China (Airalo $2.99 cheaper), Turkey (Airalo $2.49 cheaper), South Korea (Saily $2.01 cheaper), and Mexico and Dubai (Airalo $1.49 cheaper). With my code, Saily was cheaper in all {N}.</p>

      <h2 id="ten-gb">10 GB valid for 30 days</h2>
      <p>Price of a 10 GB plan valid for 30 days. Highlighted: the cheaper one at list price. In amber: Saily with my 10% code TRAVELCONNECTLY.</p>
{table("ten")}
      <p>Airalo was cheaper in {TEN_AIRALO} of {N}. Where Saily won — Japan, Thailand, the UK, France, South Korea, Dubai, Vietnam, Australia, the Philippines and Singapore — it was by a single cent. Where Airalo won, the gap ranged from 49 cents (USA, Turkey, China) to $7.99 (Canada). With my code, Saily was cheaper in {TEN_CODE} of {N}; Airalo stayed cheaper in Canada, Spain, Greece, Mexico, Portugal and on the Europe plan.</p>

      <h2 id="big-gaps">Where the gap is big</h2>
      <ul>
        <li><strong>Canada:</strong> Saily's unlimited week was $3.01 cheaper ($28.99), but Airalo's 10 GB for 30 days was $7.99 cheaper ($23.00). See the <a href="best-esim-for-canada.html">Canada guide</a>.</li>
        <li><strong>Mexico:</strong> at list price Airalo was cheaper on both — $5.49 less for 10 GB and $1.49 less for a week of unlimited. With my code, Saily's unlimited week ($22.49) beats Airalo's $23.50, but Airalo's 10 GB is still cheaper. See the <a href="best-esim-for-mexico.html">Mexico guide</a>.</li>
        <li><strong>Europe-wide plans:</strong> Airalo's 10 GB was $4.99 cheaper; Saily's unlimited week a cent cheaper. See the <a href="best-esim-for-europe.html">Europe guide</a>.</li>
        <li><strong>Portugal:</strong> Airalo's 10 GB was $5.99 cheaper ($11.00), and still cheaper with my code. See the <a href="best-esim-for-portugal.html">Portugal guide</a>.</li> Airalo's unlimited week was $2.49 cheaper at list price; with my code, Saily's ($24.29) is 21 cents cheaper. See the <a href="best-esim-for-turkey.html">Turkey guide</a>.</li>
      </ul>

      <h2 id="beyond-price">Beyond price</h2>
      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th></th><th>Saily</th><th>Airalo</th></tr></thead>
          <tbody>
{feat}
          </tbody>
        </table>
      </div>
      <p class="price-note">From each provider's own plan pages for the destinations above, checked 29 September – 13 October 2026.</p>
      <p>Saily plans activate automatically when you arrive and can be activated any time within 180 days of purchase. Saily also adds security features from the NordVPN team — a virtual location, an ad blocker and protection against malicious sites — and gives 3% of each purchase back as Saily credits.</p>

      <h2 id="which-to-choose">Which one to choose</h2>
      <ul>
        <li><strong>You want unlimited data:</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily</a> was cheaper in most destinations, states its full-speed allowance and has no hotspot restrictions.</li>
        <li><strong>You want a fixed amount of data:</strong> at list price Airalo was cheaper for 10 GB in most destinations, and it sells 7- and 15-day plans and 50 GB. With my code, Saily was cheaper in {TEN_CODE} of {N} — check the table for your destination.</li>
        <li><strong>Your dates might change:</strong> Saily's fixed plans almost all last 30 days, so an extra few days won't cost you.</li>
        <li><strong>You're going to Portugal, Mexico or Canada with fixed data in mind:</strong> Airalo, by a wide margin.</li>
        <li><strong>Several European countries:</strong> it depends on your route — see <a href="best-esim-for-europe.html">which countries each Europe plan covers</a>.</li>
      </ul>
      <p>For Saily against Holafly's unlimited plans, see <a href="saily-vs-holafly.html">Saily vs Holafly</a>; for when another provider is the better fit, see <a href="saily-alternatives.html">Saily alternatives</a>. Every destination guide also has a "Find your plan" tool that picks the cheapest plan for your trip length and usage: {guides}.</p>

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
        <a class="related-card" href="best-esim-for-travelers.html">
          <span class="tag">eSIM</span>
          <h3>Best eSIM for Travelers</h3>
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


if __name__ == "__main__":
  pagekit.TODAY = "2026-10-10"
  build(
    SLUG,
    "Saily vs Airalo 2026: Prices Compared in 23 Destinations | TravelConnectly",
    f"Saily vs Airalo compared on real, dated prices in {N} destinations: who is cheaper for unlimited data and for fixed data, plan lengths, Europe coverage and which to choose.",
    "Saily vs Airalo, Airalo vs Saily, Saily or Airalo, Saily eSIM review, Airalo eSIM review, best travel eSIM",
    "Saily vs Airalo 2026: Prices Compared in 23 Destinations",
    "Who is cheaper for unlimited and for fixed data, destination by destination, at dated prices.",
    "og-saily-vs-airalo.jpg",
    "Saily vs Airalo (2026): Prices Compared in 23 Destinations",
    FAQ, main_html(),
    f'<a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get Saily</a>',
    f'<div class="sticky-cta" data-custom="plan">\n  <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">See Saily\'s plans →</a>\n'
    f'  <span class="sub">{e.COUPON_STICKY}</span>\n</div>',
    CSS,
)
