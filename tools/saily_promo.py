"""Build saily-promo-code.html: the TRAVELCONNECTLY code, what it saves on real plans, and what is (not) confirmed.

Prices come from the destination guides (re-checked 4 Nov 2026). Verified: the code applies automatically through my
links (seen on saily.com, e.g. Italy unlimited 15 days $43.99 -> $39.59) and real orders were charged the discounted
price ($31.49 = $34.99 - 10%, $44.99 = $49.99 - 10%). Saily confirmed by email on 19 Oct 2026: first purchase (all customers), no expiry, all plans, app and website, works with any public campaign.
"""
import sys

SITE = sys.argv[1]
sys.argv = [sys.argv[0], SITE]
import esim_country_pages as e  # noqa: E402
import pagekit  # noqa: E402
from pagekit import NORD, SAILY, build  # noqa: E402
from saily_vs_airalo import CSS  # noqa: E402

SLUG = "saily-promo-code"
CHECKED_LONG = "4 November 2026"
MONTH = "November 2026"
CODE = "TRAVELCONNECTLY"


def money(v):
    return f"${v:.2f}"


def plan(c, kind):
    """(label, list price) for a guide: '7-day unlimited' or '10 GB · 30 days'."""
    if kind == "unl7":
        return "Unlimited · 7 days", next(r for r in c["unl"] if r[0] == 7)[1]
    ten = next(r for r in c["fixed"] if r[0] == "10 GB")
    return "10 GB · 30 days", next(p for p, d in ten[1] if d == 30)


PAGES = {c["slug"].removeprefix("best-esim-for-"): c for c in e.ALL_PAGES + (e.ASIA,)}
EXAMPLES = [("europe", "unl7"), ("usa", "unl7"), ("italy", "unl7"), ("bali", "unl7"), ("japan", "ten"),
            ("thailand", "ten"), ("uk", "ten"), ("asia", "unl7")]
ROWS = []
for key, kind in EXAMPLES:
    c = PAGES[key]
    label, price = plan(c, kind)
    ROWS.append(dict(c=c, label=label, price=price, code=e.code(price)))
EU = ROWS[0]
assert (EU["price"], EU["code"]) == (26.99, 24.29), EU


def table():
    out = []
    for r in ROWS:
        c = r["c"]
        name = "Asia &amp; Oceania" if c["slug"].endswith("asia") else c["name"]
        out.append(
            f'            <tr><td><a href="{c["slug"]}.html">{name}</a></td><td>{r["label"]}</td><td>{money(r["price"])}</td>'
            f'<td class="best">{money(r["code"])}</td>'
            f'<td><a href="{e.saily_deep(c)}" target="_blank" rel="sponsored noopener">Get it →</a></td></tr>')
    return """      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th>Destination</th><th>Plan</th><th>List price</th><th>With code</th><th></th></tr></thead>
          <tbody>
""" + "\n".join(out) + """
          </tbody>
        </table>
      </div>"""


EXTRA_CSS = """
/* ---- promo code box ---- */
.code-box{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:14px; padding:12px 14px;
  border:2px dashed var(--amber); border-radius:12px; background:var(--navy-panel-2); }
.code-box b{ font-family:'IBM Plex Mono',monospace; font-size:1.15rem; letter-spacing:0.06em; color:var(--amber); }
.code-box button{ min-height:40px; padding:0 14px; border-radius:10px; border:1px solid #2A4563; background:var(--navy-panel);
  color:var(--text-light); font-family:'Space Grotesk',sans-serif; font-weight:600; cursor:pointer; }
"""
COPY_JS = """<script>
(function(){
  var b = document.querySelector('.code-box button');
  if (!b || !navigator.clipboard) return;
  b.addEventListener('click', function(){
    navigator.clipboard.writeText('TRAVELCONNECTLY').then(function(){ b.textContent = 'Copied'; });
  });
})();
</script>"""

FAQ = [
    ("What is the Saily promo code?",
     f"TRAVELCONNECTLY gives 10% off your first Saily eSIM order, on any plan. My Saily links apply it automatically, so the discounted price shows on Saily's plan pages and at checkout (checked {CHECKED_LONG})."),
    ("Does the Saily code work on unlimited plans?",
     f"Yes. In every destination I checked, the 10% applied to both unlimited and fixed-data plans (on a first order) — for example a 7-day Europe unlimited plan went from {money(EU['price'])} to {money(EU['code'])}."),
    ("How much does the Saily code save?",
     "10% of the plan price: about $2.70 on a $26.99 unlimited week, $1.80 on a $17.99 10 GB plan and $7.20 on a $71.99 30-day unlimited plan."),
    ("Is there a Saily Black Friday deal in 2026?",
     f"As of {CHECKED_LONG} I hadn't seen a Black Friday offer on Saily's site. Black Friday is 27 November 2026; I'll update this page if Saily announces one. Saily says my 10% code works alongside its public campaigns, and it works now."),
    ("Is the Saily code for new customers only?",
     "It's for a first purchase. Saily told me (19 October 2026) the discount is available to all customers on their first purchase, has no expiry date and works on all plans, in the app and on the website."),
    ("Does the Saily code work during sales?",
     "Yes. Saily told me the code works with any public campaign it runs, so it applies during sales such as Black Friday too. Check the total at checkout before you pay."),
    ("Is Saily legit?",
     "Yes — Saily is an eSIM service by Nord Security, the company behind NordVPN. I've compared its prices against Airalo and Holafly in 24 destinations; it's often the cheapest for unlimited data, while Airalo is often cheaper for fixed data."),
]


def main_html():
    faq_html = "".join(f"\n      <h3>{q}</h3>\n      <p>{a}</p>" for q, a in FAQ)
    return f"""  <div class="wrap breadcrumb">
    <a href="index.html">Home</a><span class="sep">/</span><a href="guides.html#esim-countries">eSIM by country</a><span class="sep">/</span>Saily promo code
  </div>

  <div class="wrap qa-top">
    <div class="qa-grid">
      <div class="qa-head">
        <h1>Saily Promo Code ({MONTH}): 10% Off</h1>
        <div class="qa-sub">Code {CODE} · checked {CHECKED_LONG}</div>
      </div>

      <section class="qa-card" aria-labelledby="qa-title">
        <div class="qa-label"><b>Promo code</b><span>Working on {CHECKED_LONG}</span></div>
        <h2 id="qa-title" style="font-size:1.25rem;margin:12px 0 0;">10% off your first Saily order — any plan, unlimited or fixed data</h2>
        <div class="code-box"><b>{CODE}</b><button type="button">Copy</button></div>
        <a class="qa-btn" href="{SAILY}" target="_blank" rel="sponsored noopener">Get 10% off at Saily →</a>
        <p class="qa-coupon">Applied automatically when you use my link</p>
        <ul class="qa-trust"><li>Saily is by Nord Security (NordVPN)</li><li>Plans activate when you land</li><li>First order · no expiry</li></ul>
      </section>

      <section class="qa-take takeaways" aria-labelledby="kt-title">
        <h2 id="kt-title">Key takeaways</h2>
        <ol>
          <li><span><strong>{CODE} takes 10% off your first Saily order</strong> — any country, regional, unlimited or fixed-data plan — applied automatically through my links.</span></li>
          <li><span><strong>Real example:</strong> a 7-day Europe unlimited plan costs {money(EU['price'])}, or {money(EU['code'])} with the code.</span></li>
          <li><span><strong>No expiry, works in the app and on the website</strong>, according to Saily (19 October 2026).</span></li>
          <li><span><strong>It works alongside Saily's public sales</strong> — so during a Black Friday sale you'd still get the 10% on a first order.</span></li>
        </ol>
      </section>
    </div>

    <div class="author-strip">
      <div class="who">
        <span class="av" aria-hidden="true">E</span>
        <div class="nm"><b>Eron</b> · <span style="display:inline;">Solo traveler &amp; founder</span><span>Code checked on saily.com · {CHECKED_LONG}</span></div>
      </div>
      <a href="methodology.html">How I compare →</a>
    </div>
  </div>

  <div class="wrap">
    <div class="trust-note">
      <p><strong>How this page works:</strong> TRAVELCONNECTLY is my own Saily affiliate code — I earn a commission when you buy through my links, at no extra cost to you. Every price below is from my destination guides, checked in US dollars on Saily's own pages on {CHECKED_LONG}; the code's terms are as Saily confirmed them to me by email on 19 October 2026.</p>
    </div>
    <article class="article">
      <p class="lede">A working code is worth knowing about before you buy a travel eSIM. Here's exactly what {CODE} takes off real plans, how to use it, and the terms Saily confirmed to me.</p>

      <nav class="toc" aria-label="Table of contents">
        <h2>On this page</h2>
        <ol>
          <li><a href="#how-much-you-save">How much you save</a></li>
          <li><a href="#how-to-use-the-code">How to use the code</a></li>
          <li><a href="#what-i-know">The code's terms</a></li>
          <li><a href="#black-friday">Saily Black Friday 2026</a></li>
          <li><a href="#is-saily-the-cheapest">Is Saily the cheapest with the code?</a></li>
          <li><a href="#frequently-asked-questions">Frequently asked questions</a></li>
        </ol>
      </nav>

      <h2 id="how-much-you-save">How much you save</h2>
      <p>List prices and prices with the 10% code for popular plans, from my destination guides. Each "Get it" link opens that destination's plans on Saily with the code applied.</p>
{table()}
      <p class="price-note">Prices in USD from saily.com, checked {CHECKED_LONG}. Saily rounds the discounted price to the cent at checkout.</p>

      <h2 id="how-to-use-the-code">How to use the code</h2>
      <ol>
        <li><strong>Open Saily through one of my links</strong> on this page or in my destination guides. The 10% is added automatically, and plan prices on Saily's site show the discount.</li>
        <li><strong>Pick your destination and plan</strong>, then go to checkout and check that the total includes the 10% discount before you pay.</li>
        <li><strong>Download the Saily app and install the eSIM</strong> at home over WiFi (the code also works if you buy inside the app). Plans can be activated any time within 180 days and switch on when you arrive.</li>
      </ol>

      <h2 id="what-i-know">The code's terms</h2>
      <ul>
        <li><strong>First purchase:</strong> Saily told me (19 October 2026) the 10% is available to all customers on their first purchase.</li>
        <li><strong>No expiry, all plans:</strong> the code has no expiration date and works on every plan.</li>
        <li><strong>App and website:</strong> it works whether you buy on saily.com or in the Saily app.</li>
        <li><strong>Sales:</strong> it works alongside any public campaign Saily runs.</li>
        <li><strong>Verified in practice:</strong> the discount shows on Saily's plan pages through my links (for example Italy unlimited for 15 days, $43.99 → $39.59), and orders through my links were charged the discounted price.</li>
        <li><strong>Saily credits:</strong> Saily's plan pages also show 3% back in Saily credits on plans, separate from this code.</li>
      </ul>

      <h2 id="black-friday">Saily Black Friday 2026</h2>
      <p>As of {CHECKED_LONG} I hadn't seen a Black Friday offer on Saily's site. Black Friday is <strong>27 November 2026</strong>. Saily says my code works alongside its public campaigns, so if it runs a sale you'd still get the 10% on a first order. eSIM plans are bought per trip, so there's little reason to wait if you travel before then. For VPN deals, see <a href="vpn-black-friday-deals.html">VPN &amp; eSIM Black Friday deals</a>.</p>

      <h2 id="is-saily-the-cheapest">Is Saily the cheapest with the code?</h2>
      <p>Often, but not always. In my comparisons Saily is usually the cheapest of Saily, Airalo and Holafly for unlimited data, and the code widens that gap. For fixed data, Airalo is often cheaper at list price, and in some destinations even with the code. Check your destination before you buy — see <a href="saily-vs-airalo.html">Saily vs Airalo</a>, <a href="saily-vs-holafly.html">Saily vs Holafly</a> and the <a href="saily-alternatives.html">best Saily alternatives</a>.</p>

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
        <a class="related-card" href="best-esim-for-europe.html">
          <span class="tag">eSIM · Europe</span>
          <h3>Best eSIM for Europe (2026)</h3>
        </a>
        <a class="related-card" href="saily-vs-airalo.html">
          <span class="tag">eSIM · Comparison</span>
          <h3>Saily vs Airalo (2026)</h3>
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
        <div class="eyebrow" style="justify-content:center;">TRAVELLING SOON?</div>
        <h2>Get 10% off your Saily eSIM</h2>
        <p>Code {CODE} takes 10% off your first order and is applied automatically through my link. Add a VPN for hotel and café WiFi.</p>
        <div class="hero-ctas">
          <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily" style="width:auto;">Get 10% off at Saily →</a>
          <a href="{NORD}" target="_blank" rel="sponsored noopener" class="btn btn-nord" style="width:auto;">Get NordVPN →</a>
        </div>
      </div>
    </div>
  </section>"""


if __name__ == "__main__":
    pagekit.TODAY = "2026-11-04"
    build(
        SLUG,
        f"Saily Promo Code ({MONTH}): 10% Off with TRAVELCONNECTLY | TravelConnectly",
        f"Saily promo code TRAVELCONNECTLY: 10% off your first eSIM order on any plan, no expiry, applied automatically. Real savings on Europe, USA, Japan and more, checked {CHECKED_LONG}.",
        "Saily promo code, Saily coupon code, Saily discount code, Saily code, Saily eSIM discount, Saily Black Friday, Saily voucher",
        f"Saily Promo Code ({MONTH}): 10% Off",
        "TRAVELCONNECTLY takes 10% off your first Saily eSIM order — real savings and the confirmed terms.",
        "og-saily-promo-code.jpg",
        f"Saily Promo Code ({MONTH}): 10% Off with TRAVELCONNECTLY",
        FAQ, main_html(),
        f'<a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get 10% off</a>',
        f'<div class="sticky-cta" data-custom="plan">\n  <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get 10% off Saily →</a>\n'
        f'  <span class="sub">Code {CODE} · applied automatically</span>\n</div>',
        CSS + EXTRA_CSS, COPY_JS,
    )
