"""Build saily-review.html: a fact-based Saily review from the verified guide data (prices re-checked 4 Nov 2026).

Only states what was checked on saily.com or confirmed by Saily (code terms, email 19 Oct 2026). It does not claim
long-term personal testing in every country.
"""
import sys

SITE = sys.argv[1]
sys.argv = [sys.argv[0], SITE]
import esim_country_pages as e  # noqa: E402
import pagekit  # noqa: E402
import saily_vs_airalo as sva  # noqa: E402
from pagekit import NORD, SAILY, build  # noqa: E402
from saily_vs_airalo import CSS  # noqa: E402

SLUG = "saily-review"
CHECKED_LONG = "4 November 2026"
N = sva.N
assert N == 23
N_ALL = len(e.ALL_PAGES) + 1  # plus the Asia regional guide
# Saily vs Holafly, 7-day unlimited (same rule as saily_vs_holafly.py, without importing it: that script builds on import).
H7 = sum(next(r for r in c["unl"] if r[0] == 7)[1] < next(r for r in c["unl"] if r[0] == 7)[3] for c in e.ALL_PAGES)
assert H7 == 20, H7

FAQ = [
    ("Is Saily legit?",
     "Yes. Saily is an eSIM service by Nord Security, the company behind NordVPN. It sells prepaid data plans for 200+ destinations through its app and website, and plans activate automatically when you arrive."),
    ("Is Saily cheaper than Airalo?",
     f"For unlimited data, usually: Saily's 7-day unlimited plan was cheaper than Airalo's in {sva.UNL_SAILY} of {N} destinations I checked on {CHECKED_LONG}. For fixed data, usually not: Airalo was cheaper for 10 GB over 30 days in {sva.TEN_AIRALO} of {N}. With my 10% code on a first order, Saily was cheaper for an unlimited week in all {N}."),
    ("Does Saily have unlimited data?",
     "Yes. Saily's unlimited plans give 5 GB a day at full speed in most countries (3 GB in Canada, Mexico and the UAE), then up to 1 Mbps for the rest of the day, with no hotspot restrictions."),
    ("Can I use Saily as a hotspot?",
     "Yes. Saily's plan pages state no hotspot or tethering restrictions."),
    ("Does Saily include a phone number?",
     "Saily plans are data-only. Saily sells an optional US phone number with calls and texts as a monthly add-on in its app, which requires identity verification."),
    ("When does a Saily plan start?",
     "When you arrive in a covered country, as long as the eSIM is turned on and data roaming is enabled. You can activate a plan any time within 180 days of buying it."),
    ("Is there a Saily discount code?",
     "Yes — TRAVELCONNECTLY gives 10% off a first Saily order on any plan. It has no expiry and works on the website and in the app (confirmed by Saily, 19 October 2026)."),
]


def main_html():
    faq_html = "".join(f"\n      <h3>{q}</h3>\n      <p>{a}</p>" for q, a in FAQ)
    return f"""  <div class="wrap breadcrumb">
    <a href="index.html">Home</a><span class="sep">/</span><a href="guides.html#esim-countries">eSIM by country</a><span class="sep">/</span>Saily review
  </div>

  <div class="wrap qa-top">
    <div class="qa-grid">
      <div class="qa-head">
        <h1>Saily eSIM Review (2026): Prices, Pros and Cons</h1>
        <div class="qa-sub">Prices compared in {N} destinations · checked {CHECKED_LONG}</div>
      </div>

      <section class="qa-card" aria-labelledby="qa-title">
        <div class="qa-label"><b>Verdict</b><span>Saily eSIM</span></div>
        <h2 id="qa-title" style="font-size:1.25rem;margin:12px 0 0;">Good value for unlimited data — check fixed-data prices before you buy.</h2>
        <div class="vs-rows">
          <div class="vs-row"><span class="k">Cheaper unlimited week than Airalo</span><span class="v s">{sva.UNL_SAILY} of {N}</span></div>
          <div class="vs-row"><span class="k">Cheaper 10 GB · 30 days than Airalo</span><span class="v a">{sva.TEN_SAILY} of {N}</span></div>
          <div class="vs-row"><span class="k">Cheaper unlimited week than Holafly</span><span class="v s">{H7} of {N}</span></div>
        </div>
        <a class="qa-btn" href="{SAILY}" target="_blank" rel="sponsored noopener">See Saily's plans →</a>
        <p class="qa-coupon">10% off your first order with code <b>TRAVELCONNECTLY</b> · applied automatically</p>
      </section>

      <section class="qa-take takeaways" aria-labelledby="kt-title">
        <h2 id="kt-title">Key takeaways</h2>
        <ol>
          <li><span><strong>Strong on unlimited data:</strong> cheaper than Airalo for a 7-day unlimited plan in {sva.UNL_SAILY} of {N} destinations, and than Holafly in {H7} of {N}.</span></li>
          <li><span><strong>Weaker on fixed data:</strong> Airalo was cheaper for 10 GB over 30 days in {sva.TEN_AIRALO} of {N}, and sells 50 GB plans Saily's country plans don't.</span></li>
          <li><span><strong>Clear limits:</strong> 5 GB a day at full speed on unlimited plans in most countries, then up to 1 Mbps, with no hotspot restrictions.</span></li>
          <li><span><strong>Made by Nord Security</strong> (NordVPN), with security extras in the app and an optional US phone number.</span></li>
        </ol>
      </section>
    </div>

    <div class="author-strip">
      <div class="who">
        <span class="av" aria-hidden="true">E</span>
        <div class="nm"><b>Eron</b> · <span style="display:inline;">Solo traveler &amp; founder</span><span>Prices checked on provider sites · {CHECKED_LONG}</span></div>
      </div>
      <a href="methodology.html">How I compare →</a>
    </div>
  </div>

  <div class="wrap">
    <div class="trust-note">
      <p><strong>How this review works:</strong> it's based on Saily's published plans, prices and terms, checked in US dollars on saily.com on {CHECKED_LONG} and compared with Airalo and Holafly in my destination guides — not on long-term use in every country. I earn a commission from Saily, so I've included where it isn't the best choice.{e.COUPON_NOTE}</p>
    </div>
    <article class="article">
      <p class="lede">Saily is the travel eSIM from Nord Security, the company behind NordVPN. It sells prepaid data plans for 200+ destinations, from small fixed-data plans to unlimited data, installed through one app. Here's how its prices compare, what you get, and who it suits.</p>

      <nav class="toc" aria-label="Table of contents">
        <h2>On this page</h2>
        <ol>
          <li><a href="#prices">Prices: how Saily compares</a></li>
          <li><a href="#what-you-get">What you get</a></li>
          <li><a href="#pros-and-cons">Pros and cons</a></li>
          <li><a href="#who-should-use-saily">Who should use Saily</a></li>
          <li><a href="#how-to-buy">How to buy with 10% off</a></li>
          <li><a href="#frequently-asked-questions">Frequently asked questions</a></li>
        </ol>
      </nav>

      <h2 id="prices">Prices: how Saily compares</h2>
      <p>I compare Saily with Airalo and Holafly in {N} single destinations and regions, using prices from each provider's own site. On {CHECKED_LONG}:</p>
      <ul>
        <li><strong>Unlimited, 7 days:</strong> Saily was cheaper than Airalo in {sva.UNL_SAILY} of {N} — usually by a cent — and than Holafly in {H7} of {N}. A Saily unlimited week cost $20.99–29.99 depending on the destination (for example $26.99 in Europe and $24.99 in the USA).</li>
        <li><strong>10 GB for 30 days:</strong> Saily was cheaper in {sva.TEN_SAILY} of {N}; Airalo in {sva.TEN_AIRALO}, by up to about $8 in Canada.</li>
        <li><strong>With my 10% code</strong> on a first order, Saily was cheaper for an unlimited week in all {N} and for 10 GB in {sva.TEN_CODE} of {N}.</li>
      </ul>
      <p>Full tables: <a href="saily-vs-airalo.html">Saily vs Airalo</a>, <a href="saily-vs-holafly.html">Saily vs Holafly</a>, and your destination in the <a href="guides.html#esim-countries">eSIM guides by country</a>.</p>

      <h2 id="what-you-get">What you get</h2>
      <ul>
        <li><strong>Plans:</strong> fixed data from 1 GB (usually 7 days) to 20 GB (30 days) in most countries, unlimited plans from 5 to 30 days, plus regional plans such as Europe (35 countries) and Asia &amp; Oceania (22).</li>
        <li><strong>Unlimited limits:</strong> 5 GB a day at full speed in most countries (3 GB in Canada, Mexico and the UAE), then up to 1 Mbps; no hotspot restrictions.</li>
        <li><strong>Activation:</strong> plans switch on automatically when you arrive, and can be activated any time within 180 days.</li>
        <li><strong>App extras:</strong> Saily lists security features such as virtual locations, malicious-link blocking and an ad blocker, plus an optional US phone number with calls and texts.</li>
        <li><strong>Credits:</strong> Saily's plan pages show 3% back in Saily credits.</li>
      </ul>

      <h2 id="pros-and-cons">Pros and cons</h2>
      <p><strong>Pros</strong></p>
      <ul>
        <li>Often the cheapest of the big three for unlimited data, and cheapest in all {N} destinations with my code.</li>
        <li>States its full-speed allowance up front, and doesn't restrict hotspot use.</li>
        <li>Fixed plans mostly last 30 days, so a small plan covers a whole trip.</li>
        <li>One app for every destination; plans activate on arrival.</li>
      </ul>
      <p><strong>Cons</strong></p>
      <ul>
        <li>Fixed data is often pricier than Airalo, and single-country plans stop at 20 GB.</li>
        <li>Doesn't name its local networks for many countries.</li>
        <li>"Unlimited" slows to 1 Mbps after the daily allowance (3 GB in Canada, Mexico and the UAE).</li>
        <li>Cheaper unlimited options exist outside the big three — for example Maya Mobile's global plan — though they may need their own app to buy. See <a href="saily-alternatives.html">Saily alternatives</a>.</li>
      </ul>

      <h2 id="who-should-use-saily">Who should use Saily</h2>
      <ul>
        <li><strong>Good fit:</strong> trips of 5 days to a month where you want unlimited data, travelers who use a phone hotspot, and anyone who wants one app across several trips.</li>
        <li><strong>Look elsewhere:</strong> if you need a fixed 10 GB or more for a month in Canada, Portugal, Mexico or Spain (Airalo was cheaper there), or WhatsApp in China without a VPN (see the <a href="best-esim-for-china.html">China guide</a>).</li>
      </ul>

      <h2 id="how-to-buy">How to buy with 10% off</h2>
      <ol>
        <li>Open Saily through one of my links — the code <strong>TRAVELCONNECTLY</strong> is applied automatically (10% off a first order, any plan; details on the <a href="saily-promo-code.html">Saily promo code</a> page).</li>
        <li>Choose your destination and plan, and check the discounted total at checkout.</li>
        <li>Install the eSIM in the Saily app at home over WiFi; it switches on when you land.</li>
      </ol>

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
        <a class="related-card" href="saily-promo-code.html">
          <span class="tag">eSIM · Deal</span>
          <h3>Saily Promo Code: 10% Off</h3>
        </a>
        <a class="related-card" href="saily-vs-airalo.html">
          <span class="tag">eSIM · Comparison</span>
          <h3>Saily vs Airalo (2026)</h3>
        </a>
        <a class="related-card" href="saily-alternatives.html">
          <span class="tag">eSIM · Comparison</span>
          <h3>Saily Alternatives (2026)</h3>
        </a>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="cta-band">
        <div class="eyebrow" style="justify-content:center;">DECIDED ON SAILY?</div>
        <h2>Get 10% off your first order</h2>
        <p>Code TRAVELCONNECTLY is applied automatically through my link. Add a VPN for hotel and café WiFi.</p>
        <div class="hero-ctas">
          <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily" style="width:auto;">See Saily's plans →</a>
          <a href="{NORD}" target="_blank" rel="sponsored noopener" class="btn btn-nord" style="width:auto;">Get NordVPN →</a>
        </div>
      </div>
    </div>
  </section>"""


if __name__ == "__main__":
    pagekit.TODAY = "2026-11-06"
    build(
        SLUG,
        "Saily eSIM Review 2026: Prices, Pros and Cons | TravelConnectly",
        f"Saily eSIM review: how its prices compare with Airalo and Holafly in {N} destinations, unlimited-data limits, hotspot, app extras, pros and cons, and 10% off your first order.",
        "Saily review, Saily eSIM review, is Saily legit, Saily eSIM, Saily unlimited data, Saily vs Airalo, Saily pros and cons",
        "Saily eSIM Review 2026: Prices, Pros and Cons",
        "How Saily's prices compare in 23 destinations, what you get, and who it suits.",
        "og-saily-review.jpg",
        "Saily eSIM Review (2026): Prices, Pros and Cons",
        FAQ, main_html(),
        f'<a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get Saily</a>',
        f'<div class="sticky-cta" data-custom="plan">\n  <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">See Saily\'s plans →</a>\n'
        f'  <span class="sub">{e.COUPON_STICKY}</span>\n</div>',
        CSS,
    )
