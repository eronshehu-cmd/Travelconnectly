"""Generate the country eSIM guides (Japan, Thailand, USA, Turkey) with the answer-first layout.

Layout follows the Claude Design "USA eSIM Page" / "Find Your Plan" / "Author Trust Strip" components,
rebuilt as static HTML/CSS + vanilla JS with TravelConnectly's verified data only.

Prices checked 29 Sept 2026 in USD on each provider's own country page
(saily.com, airalo.com with currency=USD, esim.holafly.com with USD selected).
"""
import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

os.environ["SITE_DIR"] = sys.argv[1]
os.environ["PAGE_DATE"] = "2026-09-29"
sys.path.insert(0, os.path.dirname(__file__))
import pagekit  # noqa: E402
from pagekit import NORD, SAILY, build  # noqa: E402

# Defaults for the first four guides; newer guides set checked / checked_long / date in their config.
CHECKED = "29 Sep 2026"
CHECKED_LONG = "29 September 2026"
DATE = "2026-09-29"
# Saily affiliate coupon (10% off, confirmed by Saily on 12 Oct 2026); links carry coupon= so it applies automatically.
COUPON_LINE = '<p class="qa-coupon">10% off with code <b>TRAVELCONNECTLY</b> · applied automatically</p>'
COUPON_STICKY = "10% off with code TRAVELCONNECTLY"
COUPON_NOTE = " Saily prices on this page are before the 10% TRAVELCONNECTLY discount, which my Saily links apply automatically."
# Single-country guides where a Europe-wide plan is a real alternative (they get a link to the Europe guide).
EUROPE_TRIP_SLUGS = {"best-esim-for-italy", "best-esim-for-spain", "best-esim-for-uk", "best-esim-for-france",
                     "best-esim-for-greece", "best-esim-for-portugal", "best-esim-for-turkey"}
COUNTRY_LIST = [("japan", "Japan"), ("thailand", "Thailand"), ("usa", "USA"), ("turkey", "Turkey"),
                ("canada", "Canada"), ("italy", "Italy"), ("spain", "Spain"), ("uk", "UK"), ("france", "France"),
                ("greece", "Greece"), ("mexico", "Mexico"), ("china", "China"), ("south-korea", "South Korea"),
                ("bali", "Bali"), ("portugal", "Portugal"), ("europe", "Europe")]

CSS = """
/* ---- country eSIM tables ---- */
.glance table.fit{ min-width:0; }
@media (max-width:560px){ .glance table.fit th, .glance table.fit td{ padding:11px 9px; } }
.glance td.best{ color:var(--teal); font-weight:600; }
.glance table.cov td:not(:first-child), .glance table.cov th:not(:first-child){ text-align:center; }
@media (max-width:560px){ .glance table.cov th, .glance table.cov td{ padding:9px 5px; font-size:0.8rem; } .glance table.cov th{ font-size:0.7rem; } }
.glance td small{ display:block; color:var(--text-muted); font-size:0.74rem; font-family:'IBM Plex Mono',monospace; }
.glance td small.code{ color:var(--amber); font-weight:400; }
.takeaways{ background:var(--navy-panel); border:1px solid var(--hairline); border-radius:14px; padding:18px 18px 6px; }
.takeaways h2{ font-size:0.75rem !important; font-family:'IBM Plex Mono',monospace; letter-spacing:0.12em; text-transform:uppercase; color:var(--text-muted); margin:0 0 4px !important; }
.takeaways ol{ list-style:none; margin:0; padding:0; counter-reset:kt; }
.takeaways li{ counter-increment:kt; display:flex; gap:12px; padding:10px 0; border-bottom:1px solid var(--hairline); font-size:0.95rem; line-height:1.55; }
.takeaways li:last-child{ border-bottom:none; }
.takeaways li::before{ content:counter(kt, decimal-leading-zero); font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:var(--teal); padding-top:3px; }

/* ---- answer-first top (from Claude Design) ---- */
.qa-top{ padding-top:14px; }
.qa-grid{ display:grid; grid-template-columns:minmax(0,1fr); grid-template-areas:"head" "card" "chips" "take"; align-items:start; }
.qa-head{ grid-area:head; margin-bottom:14px; }
.qa-head h1{ font-size:clamp(1.75rem,4.2vw,2.9rem); line-height:1.1; letter-spacing:-0.02em; margin:0; text-wrap:balance; }
.qa-sub{ margin-top:8px; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; letter-spacing:0.02em; color:var(--text-muted); }
.qa-card{ grid-area:card; background:var(--navy-panel); border:1px solid #2A4563; border-radius:16px; padding:16px; }
.qa-card .qa-label{ display:flex; justify-content:space-between; gap:12px; font-family:'IBM Plex Mono',monospace; font-size:0.69rem; letter-spacing:0.12em; text-transform:uppercase; }
.qa-card .qa-label b{ color:var(--amber); font-weight:600; }
.qa-card .qa-label span{ color:var(--text-muted); letter-spacing:0.04em; }
.qa-prov{ display:flex; align-items:center; gap:12px; margin-top:12px; }
.qa-logo{ width:44px; height:44px; flex:0 0 auto; border-radius:11px; background:var(--saily-purple); color:#fff; display:flex; align-items:center; justify-content:center; font-family:'Space Grotesk',sans-serif; font-size:1.25rem; font-weight:700; }
.qa-prov h2{ font-size:1.38rem; margin:0; line-height:1.15; }
.qa-prov p{ margin:2px 0 0; font-size:0.875rem; line-height:1.4; color:#C9D5E2; }
.qa-plan{ display:inline-block; margin-top:14px; line-height:36px; padding:0 12px; background:var(--navy-panel-2); border:1px solid #2A4563; border-radius:999px; font-family:'IBM Plex Mono',monospace; font-size:0.875rem; white-space:nowrap; }
.qa-plan strong{ color:var(--teal); font-weight:600; }
.qa-btn{ margin-top:14px; display:flex; align-items:center; justify-content:center; min-height:52px; padding:0 16px; background:var(--saily-purple); color:#fff; border-radius:12px; font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:600; text-align:center; }
.qa-btn:hover{ background:#5A3AB8; }
.qa-logo.other{ background:#1B3247; color:var(--teal); }
.qa-btn.other{ background:transparent; border:1.5px solid var(--teal); color:var(--teal); }
.qa-btn.other:hover{ background:rgba(63,217,199,.08); }
.qa-coupon{ margin:10px 0 0 !important; text-align:center; font-size:0.82rem !important; line-height:1.45; color:var(--amber) !important; }
.qa-coupon b{ font-family:'IBM Plex Mono',monospace; letter-spacing:0.04em; }
.qa-note{ margin:8px 0 0 !important; text-align:center; font-size:0.75rem !important; color:var(--text-muted) !important; }
.qa-trust{ list-style:none; margin:12px 0 0; padding:0; display:flex; flex-wrap:wrap; gap:4px 12px; font-size:0.75rem; line-height:1.5; color:var(--text-muted); }
.qa-trust li::before{ content:"✓"; color:var(--teal); margin-right:5px; }
.qa-chips{ grid-area:chips; display:flex; flex-direction:column; gap:8px; margin-top:12px; }
.qa-chip{ display:flex; align-items:center; justify-content:space-between; gap:10px; min-height:48px; padding:10px 14px; background:var(--navy-panel); border:1px solid var(--navy-panel-2); border-radius:12px; font-size:0.875rem; line-height:1.4; }
.qa-chip:hover{ border-color:var(--teal); }
.qa-chip .k{ color:var(--text-muted); }
.qa-chip .v{ font-family:'IBM Plex Mono',monospace; font-weight:600; color:var(--teal); white-space:nowrap; }
.qa-chip .arr{ color:var(--text-muted); }
.qa-take{ grid-area:take; margin-top:28px; }
@media (min-width:960px){
  .qa-top{ padding-top:36px; }
  .qa-grid{ grid-template-columns:minmax(0,1fr) 400px; grid-template-areas:"head card" "chips card" "take card"; column-gap:56px; }
  .qa-chips{ margin-top:4px; }
}

/* ---- compact author strip ---- */
.author-strip{ margin-top:22px; display:flex; flex-wrap:wrap; align-items:center; gap:4px 14px; padding:8px 0; border-top:1px solid var(--hairline); border-bottom:1px solid var(--hairline); }
.author-strip .who{ display:flex; align-items:center; gap:10px; flex:1 1 auto; min-width:0; }
.author-strip .av{ width:36px; height:36px; border-radius:50%; flex:0 0 auto; background:#1B3247; display:flex; align-items:center; justify-content:center; font-family:'Space Grotesk',sans-serif; font-weight:700; color:var(--teal); }
.author-strip .nm{ line-height:1.3; min-width:0; }
.author-strip .nm b{ font-size:0.875rem; font-weight:600; }
.author-strip .nm span{ display:block; font-size:0.78rem; color:var(--text-muted); }
.author-strip a{ display:flex; align-items:center; min-height:48px; font-size:0.875rem; font-weight:500; color:var(--teal); text-decoration:underline; text-underline-offset:3px; }

/* ---- Find your plan widget ---- */
.planpick{ background:var(--navy-panel); border:1px solid #2A4563; border-radius:20px; padding:18px 16px; margin:8px 0 36px; }
.planpick .pp-eyebrow{ font-family:'IBM Plex Mono',monospace; font-size:0.69rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:var(--amber); }
.planpick h2{ margin:6px 0 18px !important; font-size:1.3rem !important; }
.pp-grid{ display:grid; gap:24px; grid-template-columns:minmax(0,1fr); }
.pp-label{ font-size:0.875rem; font-weight:600; margin-bottom:8px; }
.pp-label span{ font-weight:400; color:var(--text-muted); }
.pp-days{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:4px; padding:4px; background:var(--navy-deep); border:1px solid #2A4563; border-radius:12px; }
.pp-days button{ min-height:52px; border:0; border-radius:9px; background:transparent; color:var(--text-light); font-family:'IBM Plex Mono',monospace; font-size:1.1rem; cursor:pointer; }
.pp-days button[aria-checked="true"]{ background:var(--teal); color:var(--navy-deep); font-weight:600; }
.pp-use{ display:flex; flex-direction:column; gap:8px; }
.pp-use button{ display:flex; align-items:center; gap:12px; min-height:60px; padding:10px 14px; text-align:left; background:var(--navy-panel-2); border:1.5px solid var(--navy-panel-2); border-radius:12px; color:var(--text-light); cursor:pointer; font-family:inherit; }
.pp-use button[aria-checked="true"]{ background:rgba(63,217,199,.1); border-color:var(--teal); }
.pp-use .dot{ width:20px; height:20px; flex:0 0 auto; border-radius:50%; border:2px solid var(--text-muted); }
.pp-use button[aria-checked="true"] .dot{ border-color:var(--teal); box-shadow:inset 0 0 0 4px var(--navy-panel-2), inset 0 0 0 10px var(--teal); }
.pp-use .t{ display:flex; flex-direction:column; gap:2px; }
.pp-use .t b{ font-size:0.94rem; }
.pp-use .t span{ font-size:0.8rem; color:var(--text-muted); }
.pp-wifi{ display:flex; align-items:center; justify-content:space-between; gap:14px; width:100%; min-height:60px; padding:10px 14px; text-align:left; background:var(--navy-panel-2); border:1px solid #2A4563; border-radius:12px; color:var(--text-light); cursor:pointer; font-family:inherit; }
.pp-wifi .t b{ display:block; font-size:0.94rem; }
.pp-wifi .t span{ font-size:0.8rem; color:var(--text-muted); }
.pp-wifi .sw{ width:52px; height:30px; flex:0 0 auto; border-radius:999px; background:var(--navy-deep); border:1px solid #3A5878; padding:2px; display:flex; }
.pp-wifi .sw i{ width:24px; height:24px; border-radius:50%; background:var(--text-muted); }
.pp-wifi[aria-checked="true"] .sw{ background:var(--teal); justify-content:flex-end; border-color:var(--teal); }
.pp-wifi[aria-checked="true"] .sw i{ background:var(--navy-deep); }
.pp-out .empty{ border:1.5px dashed #3A5878; border-radius:16px; padding:22px 18px; color:#C9D5E2; font-size:0.94rem; line-height:1.55; }
.pp-res{ background:var(--navy-deep); border:1px solid #2A4563; border-radius:16px; padding:18px; }
.pp-res .lbl{ font-family:'IBM Plex Mono',monospace; font-size:0.69rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:var(--text-muted); }
.pp-res .lbl.rec{ color:var(--amber); }
.pp-res .est{ display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 12px; margin-top:6px; }
.pp-res .est b{ font-family:'IBM Plex Mono',monospace; font-size:2.4rem; font-weight:600; line-height:1; color:var(--teal); }
.pp-res .est span{ font-size:0.8rem; color:var(--text-muted); }
.pp-res hr{ border:0; height:1px; background:var(--navy-panel-2); margin:16px 0; }
.pp-res .prov{ margin-top:6px; display:flex; flex-wrap:wrap; align-items:baseline; gap:2px 10px; }
.pp-res .prov b{ font-family:'Space Grotesk',sans-serif; font-size:1.35rem; }
.pp-res .prov span{ font-family:'IBM Plex Mono',monospace; font-size:0.94rem; }
.pp-res p{ margin:8px 0 0 !important; font-size:0.875rem !important; line-height:1.5; color:#C9D5E2 !important; }
.pp-res .note{ margin-top:14px; padding:12px 14px; background:rgba(244,168,37,.08); border:1px solid rgba(244,168,37,.45); border-radius:12px; font-size:0.875rem; }
.pp-res .cta{ margin-top:16px; display:flex; align-items:center; justify-content:center; min-height:52px; padding:0 16px; border-radius:12px; font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:600; text-decoration:none !important; }
.pp-res .cta.saily{ background:var(--saily-purple); color:#fff !important; }
.pp-res .cta.other{ background:transparent; border:1.5px solid var(--teal); color:var(--teal) !important; }
.pp-res .sub{ display:block; margin-top:8px; text-align:center; font-size:0.75rem; color:var(--text-muted); }
@media (min-width:720px){
  .planpick{ padding:32px; }
  .pp-grid{ grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:32px; }
}
.hero-img.lower{ max-width:640px; margin-top:8px; }
"""

PLANPICK_JS = """<script>
(function(){
  var root = document.getElementById('planpick');
  if (!root) return;
  var D = JSON.parse(document.getElementById('planpick-data').textContent);
  var USE = { light:{t:'light', d:0.25}, medium:{t:'medium', d:0.7}, heavy:{t:'heavy', d:1.8} };
  var st = { days:null, use:null, wifi:false };
  var out = root.querySelector('.pp-out');
  function money(v){ return '$' + v.toFixed(2); }
  function link(o, label){
    var saily = o.p === 'Saily';
    return '<a class="cta ' + (saily ? 'saily' : 'other') + '" href="' + o.url + '" target="_blank" rel="' + (saily ? 'sponsored noopener' : 'noopener') + '">' + label + '</a>'
      + (saily ? '<span class="sub">10% off with code TRAVELCONNECTLY, applied automatically.</span>' : '<span class="sub">I don\\'t earn a commission from ' + o.p + '.</span>');
  }
  function render(){
    root.querySelectorAll('[data-days]').forEach(function(b){ b.setAttribute('aria-checked', String(+b.dataset.days === st.days)); });
    root.querySelectorAll('[data-use]').forEach(function(b){ b.setAttribute('aria-checked', String(b.dataset.use === st.use)); });
    root.querySelector('[data-wifi]').setAttribute('aria-checked', String(st.wifi));
    if (!st.days || !st.use) {
      out.innerHTML = '<div class="empty">Pick a trip length and how you use your phone. I\\'ll suggest the smallest plan that covers it, at the lowest price I found on ' + D.checked + '.</div>';
      return;
    }
    var est = st.days * USE[st.use].d * (st.wifi ? 0.5 : 1);
    var need = est * 1.15;
    var plan = null;
    for (var i = 0; i < D.fixed.length; i++) { if (D.fixed[i].gb >= need) { plan = D.fixed[i]; break; } }
    var overflow = !plan;
    if (overflow) plan = D.fixed[D.fixed.length - 1];
    var unl = D.unl[String(st.days)];
    var rec, spec, why, note = '';
    if (unl && (overflow || unl.price <= plan.price + 0.5)) {
      rec = unl; spec = 'Unlimited · ' + unl.days + ' days · ' + money(unl.price);
      why = overflow ? 'At this pace even the biggest fixed plan is tight, so unlimited is the safer buy.'
                     : 'Costs about the same as or less than the ' + plan.gb + ' GB plan you would otherwise need.';
      if (!overflow) note = plan.p + ' ' + plan.gb + ' GB · 30 days would be ' + money(plan.price) + '.';
    } else {
      rec = plan; spec = plan.gb + ' GB · 30 days · ' + money(plan.price);
      why = 'Covers about ' + Math.max(1, Math.round(est)) + ' GB with headroom, at the lowest 30-day price I found for this size.';
      if (unl && unl.price - plan.price <= 3) note = 'For ' + st.days + ' days, unlimited is only ' + money(unl.price - plan.price) + ' more: ' + unl.p + ' ' + unl.days + ' days for ' + money(unl.price) + '.';
    }
    if (rec.p === 'Saily' && rec.sc) spec += ' (' + money(rec.sc) + ' with code)';
    else if (rec.sc && rec.sc < rec.price) note = (note ? note + ' ' : '') + 'With my code TRAVELCONNECTLY, Saily\\'s ' + (rec.gb ? rec.gb + ' GB for 30 days' : rec.days + '-day unlimited') + ' is ' + money(rec.sc) + ' — <a href="' + rec.surl + '" target="_blank" rel="sponsored noopener">see Saily</a>.';
    var label = rec.p === 'Saily' ? 'Get Saily ' + D.country + (rec.gb ? ' ' + rec.gb + ' GB' : ' unlimited') + ' →' : 'See ' + rec.p + '\\'s ' + D.country + ' plans →';
    out.innerHTML = '<div class="pp-res">'
      + '<div class="lbl">Estimated data</div>'
      + '<div class="est"><b>' + (est < 1 ? '&lt; 1 GB' : '≈ ' + Math.round(est) + ' GB') + '</b><span>for ' + st.days + ' days, ' + USE[st.use].t + ' use' + (st.wifi ? ', mostly on Wi-Fi' : '') + '</span></div>'
      + '<hr><div class="lbl rec">Recommended</div>'
      + '<div class="prov"><b>' + rec.p + '</b><span>' + spec + '</span></div>'
      + '<p>' + why + '</p>'
      + (note ? '<div class="note">' + note + '</div>' : '')
      + link(rec, label)
      + '</div>';
  }
  root.addEventListener('click', function(e){
    var b = e.target.closest('button');
    if (!b || !root.contains(b)) return;
    if (b.dataset.days) st.days = +b.dataset.days;
    else if (b.dataset.use) st.use = b.dataset.use;
    else if (b.hasAttribute('data-wifi')) st.wifi = !st.wifi;
    render();
  });
  render();
})();
</script>"""


def money(v):
    return f"${v:.2f}"


def code(p):
    """Saily price with the 10% TRAVELCONNECTLY code, rounded like Saily's checkout (9.99 -> 8.99)."""
    return float((Decimal(str(p)) * Decimal("0.9")).quantize(Decimal("0.01"), ROUND_HALF_UP))


def code_tag(p):
    return f'<small class="code">{money(code(p))} with code</small>'


def fixed_table(rows):
    """rows: (label, [(price, days)] saily, [(price, days)] airalo). Highlights the cheaper 30-day option at list price."""
    out = []
    for label, saily, airalo in rows:
        s30 = [p for p, d in saily if d == 30]
        a30 = [p for p, d in airalo if d == 30]
        s_best = s30 and a30 and s30[0] < a30[0]
        a_best = s30 and a30 and a30[0] < s30[0]

        def cell(opts, best, is_saily=False):
            inner = "".join(f"{money(p)}<small>{d} day{'s' if d > 1 else ''}</small>{code_tag(p) if is_saily else ''}"
                            for p, d in opts) or "—"
            return f'<td class="best">{inner}</td>' if best else f"<td>{inner}</td>"

        out.append(f"            <tr><td>{label}</td>{cell(saily, s_best, True)}{cell(airalo, a_best)}</tr>")
    return """      <div class="table-wrap glance">
        <table class="fit">
          <thead><tr><th>Data</th><th>Saily</th><th>Airalo</th></tr></thead>
          <tbody>
""" + "\n".join(out) + """
          </tbody>
        </table>
      </div>"""


def unlimited_table(rows):
    """rows: (days, saily, airalo, holafly), None = not sold. Highlights the cheapest."""
    out = []
    for days, *prices in rows:
        low = min(p for p in prices if p is not None)
        cells = "".join(
            "<td>—</td>" if p is None else
            f'<td{" class=\"best\"" if p == low else ""}>{money(p)}{code_tag(p) if i == 0 else ""}</td>'
            for i, p in enumerate(prices))
        out.append(f"            <tr><td>{days}</td>{cells}</tr>")
    return """      <div class="table-wrap glance">
        <table class="fit">
          <thead><tr><th>Days</th><th>Saily</th><th>Airalo</th><th>Holafly</th></tr></thead>
          <tbody>
""" + "\n".join(out) + """
          </tbody>
        </table>
      </div>"""


def planner_data(c):
    """Cheapest 30-day plan per size and cheapest unlimited per trip length, from the verified tables."""
    saily_url = f"{SAILY}&aff_sub={c['slug']}&aff_sub2=picker"
    urls = {"Saily": saily_url, "Airalo": c["airalo_url"], "Holafly": c["holafly_url"]}
    fixed = []
    for label, saily, airalo in c["fixed"]:
        opts = [("Saily", p) for p, d in saily if d == 30] + [("Airalo", p) for p, d in airalo if d == 30]
        if not opts:
            continue
        prov, price = min(opts, key=lambda o: o[1])  # ties keep the first (Saily)
        s30 = next((p for p, d in saily if d == 30), None)
        fixed.append({"gb": int(label.split()[0]), "p": prov, "price": price, "url": urls[prov],
                      "sc": code(s30) if s30 else None, "surl": saily_url})
    unl = {}
    for want, actual in ((3, 3), (7, 7), (14, 15), (30, 30)):
        row = next((r for r in c["unl"] if r[0] == actual), None)
        if not row:
            continue
        best = None
        for prov, price in zip(("Saily", "Airalo", "Holafly"), row[1:]):
            if price is not None and (best is None or price < best[1]):
                best = (prov, price)
        unl[str(want)] = {"p": best[0], "price": best[1], "days": actual, "url": urls[best[0]],
                          "sc": code(row[1]) if row[1] is not None else None, "surl": saily_url}
    return {"country": c["name"], "checked": c.get("checked", CHECKED), "fixed": fixed, "unl": unl}


def chip_html(kind, text, price, prov, c, url=None):
    if prov == "Saily":
        href, rel = SAILY, "sponsored noopener"
    else:
        href, rel = url or (c["airalo_url"] if prov == "Airalo" else c["holafly_url"]), "noopener"
    return (f'        <a class="qa-chip" href="{href}" target="_blank" rel="{rel}">'
            f'<span><span class="k">{kind}</span> {text} <span class="v">{money(price)}</span></span>'
            f'<span class="arr" aria-hidden="true">→</span></a>')


def page(c):
    faq_html = "".join(f"\n      <h3>{q}</h3>\n      <p>{a}</p>" for q, a in c["faq"])
    picks = list(c["picks"])
    if c["slug"] in EUROPE_TRIP_SLUGS and not any("best-esim-for-europe.html" in p for p in picks):
        picks.append('<strong>Visiting several European countries?</strong> See <a href="best-esim-for-europe.html">Europe eSIM plans compared</a> — which of 33–41 countries each plan covers, and when one regional plan beats separate country plans.')
    pick_html = "\n".join(f"        <li>{p}</li>" for p in picks)
    net_html = "\n".join(f"        <li>{n}</li>" for n in c["networks"])
    tips_html = "\n".join(f"        <li>{n}</li>" for n in c["tips"])
    take_html = "\n".join(f"          <li><span>{t}</span></li>" for t in c["takeaways"])
    trust_html = "".join(f"<li>{t}</li>" for t in c["qa_trust"])
    chips = "\n".join(chip_html(*ch[:4], c, *ch[4:]) for ch in c["qa_chips"])
    # Quick answer normally recommends Saily; where a non-partner is clearly cheaper, it recommends that one instead.
    qa_prov = c.get("qa_provider", "Saily")
    if qa_prov == "Saily":
        qa_code = money(code(float(c["qa_price"].lstrip("$"))))
        qa_note = (f'\n        <p class="qa-coupon">{qa_code} with code <b>TRAVELCONNECTLY</b> (10% off) · applied automatically</p>')
        qa_other, qa_href, qa_rel = "", SAILY, "sponsored noopener"
    else:
        qa_other = " other"
        qa_href = c["airalo_url"] if qa_prov == "Airalo" else c["holafly_url"]
        qa_rel = "noopener"
        qa_note = f'\n        <p class="qa-note">I don\'t earn a commission from {qa_prov}.</p>'
    coverage = c.get("coverage_html", "")
    coverage_toc = '\n          <li><a href="#countries-covered">Which countries are covered</a></li>' if coverage else ""
    data = json.dumps(planner_data(c), ensure_ascii=False)
    CHECKED = c.get("checked", globals()["CHECKED"])  # noqa: N806 - shadows the default inside this page
    checked_long = c.get("checked_long", CHECKED_LONG)
    more = " · ".join(f'<a href="best-esim-for-{s}.html">{n}</a>' for s, n in COUNTRY_LIST if f"best-esim-for-{s}" != c["slug"])

    main = f"""  <div class="wrap breadcrumb">
    <a href="index.html">Home</a><span class="sep">/</span><a href="guides.html#esim-countries">eSIM by country</a><span class="sep">/</span>{c['name']}
  </div>

  <div class="wrap qa-top">
    <div class="qa-grid">
      <div class="qa-head">
        <h1>Best eSIM for {c['name_h1']} (2026)</h1>
        <div class="qa-sub">Saily vs Airalo vs Holafly · prices checked {CHECKED}</div>
      </div>

      <section class="qa-card" aria-labelledby="qa-title">
        <div class="qa-label"><b>Quick answer</b><span>{c['qa_label']}</span></div>
        <div class="qa-prov">
          <div class="qa-logo{qa_other}" aria-hidden="true">{qa_prov[0]}</div>
          <div>
            <h2 id="qa-title">{qa_prov}</h2>
            <p>{c['qa_reason']}</p>
          </div>
        </div>
        <span class="qa-plan">{c['qa_plan']} · <strong>{c['qa_price']}</strong></span>
        <a class="qa-btn{qa_other}" href="{qa_href}" target="_blank" rel="{qa_rel}">{c['qa_cta']}</a>{qa_note}
        <ul class="qa-trust">{trust_html}</ul>
      </section>

      <div class="qa-chips">
{chips}
      </div>

      <section class="qa-take takeaways" aria-labelledby="kt-title">
        <h2 id="kt-title">Key takeaways</h2>
        <ol>
{take_html}
        </ol>
      </section>
    </div>

    <div class="author-strip">
      <div class="who">
        <span class="av" aria-hidden="true">E</span>
        <div class="nm"><b>Eron</b> · <span style="display:inline;">Solo traveler &amp; founder</span><span>Prices checked on provider sites · {CHECKED}</span></div>
      </div>
      <a href="methodology.html">How I compare →</a>
    </div>
  </div>

  <div class="wrap">
    <div class="trust-note">
      <p><strong>How this page works:</strong> every price was checked in US dollars on each provider's own {c.get('plan_name', c['name'])} page on {CHECKED}. Prices change often, so confirm at checkout. I earn a commission from Saily; I have no affiliate relationship with Airalo or Holafly, and I say where they're cheaper.{COUPON_NOTE}</p>
    </div>
    <article class="article">
      <p class="lede">{c['lede']}</p>

      <section class="planpick" id="planpick" aria-labelledby="find-your-plan">
        <div class="pp-eyebrow">Find your plan</div>
        <h2 id="find-your-plan">How much data do you need in {c['name_h1']}?</h2>
        <div class="pp-grid">
          <div style="display:flex;flex-direction:column;gap:22px;">
            <div>
              <div class="pp-label" id="pp-days-l">Trip length <span>(days)</span></div>
              <div class="pp-days" role="radiogroup" aria-labelledby="pp-days-l">
                <button type="button" role="radio" aria-checked="false" data-days="3" aria-label="3 days">3</button>
                <button type="button" role="radio" aria-checked="false" data-days="7" aria-label="7 days">7</button>
                <button type="button" role="radio" aria-checked="false" data-days="14" aria-label="14 days">14</button>
                <button type="button" role="radio" aria-checked="false" data-days="30" aria-label="30 days">30</button>
              </div>
            </div>
            <div>
              <div class="pp-label" id="pp-use-l">How you use your phone</div>
              <div class="pp-use" role="radiogroup" aria-labelledby="pp-use-l">
                <button type="button" role="radio" aria-checked="false" data-use="light"><span class="dot" aria-hidden="true"></span><span class="t"><b>Light</b><span>Maps &amp; messaging</span></span></button>
                <button type="button" role="radio" aria-checked="false" data-use="medium"><span class="dot" aria-hidden="true"></span><span class="t"><b>Medium</b><span>+ social media &amp; music</span></span></button>
                <button type="button" role="radio" aria-checked="false" data-use="heavy"><span class="dot" aria-hidden="true"></span><span class="t"><b>Heavy</b><span>+ video &amp; hotspot</span></span></button>
              </div>
            </div>
            <button type="button" class="pp-wifi" role="switch" aria-checked="false" data-wifi><span class="t"><b>Wi-Fi most of the time?</b><span>Hotel, café or office Wi-Fi roughly halves what you need</span></span><span class="sw" aria-hidden="true"><i></i></span></button>
          </div>
          <div class="pp-out" aria-live="polite"></div>
        </div>
        <script type="application/json" id="planpick-data">{data}</script>
      </section>

      <nav class="toc" aria-label="Table of contents">
        <h2>On this page</h2>
        <ol>
          <li><a href="#find-your-plan">Find your plan</a></li>{coverage_toc}
          <li><a href="#fixed-data-prices">Fixed-data plan prices</a></li>
          <li><a href="#unlimited-data-prices">Unlimited plan prices</a></li>
          <li><a href="#which-one-to-pick">Which one to pick</a></li>
          <li><a href="#networks-and-coverage">Networks and coverage</a></li>
          <li><a href="#tips">{c['tips_title']}</a></li>
          <li><a href="#how-much-data">How much data you need</a></li>
          <li><a href="#setting-up-before-you-fly">Setting up before you fly</a></li>
          <li><a href="#frequently-asked-questions">Frequently asked questions</a></li>
        </ol>
      </nav>
{coverage}
      <h2 id="fixed-data-prices">Fixed-data plan prices</h2>
      <p>Holafly only sells unlimited plans here, so fixed data is Saily against Airalo. Validity matters as much as price: a plan that expires after 7 days is only cheap if your trip is 7 days. Highlighted: the cheaper 30-day option at list price. In amber: Saily's price with my 10% code TRAVELCONNECTLY.</p>
{fixed_table(c['fixed'])}
      <p class="price-note">Prices in USD from saily.com and airalo.com, checked {checked_long}.</p>
      <p>{c['fixed_note']}</p>

      <h2 id="unlimited-data-prices">Unlimited plan prices</h2>
{unlimited_table(c['unl'])}
      <p class="price-note">Prices in USD from each provider's {c.get('plan_name', c['name'])} page, checked {checked_long}. Highlighted: cheapest for that length at list price. In amber: Saily with code TRAVELCONNECTLY. — = not sold at that length.</p>
      <p>{c['unl_note']}</p>
      <p>"Unlimited" rarely means unlimited full speed. <strong>Saily</strong> states {c.get('saily_fup', '5 GB')} per day at full speed, then up to 1 Mbps, with no hotspot restrictions. <strong>Holafly</strong> states a fair-usage policy that can slow speeds for up to a day, and lets you share 1 GB per day as a hotspot. <strong>Airalo's</strong> page didn't list its unlimited limits, so check the plan details before buying.</p>

      <h2 id="which-one-to-pick">Which one to pick</h2>
      <ul>
{pick_html}
      </ul>

      <img class="hero-img lower" src="{c['photo']}" alt="{c['photo_alt']}" width="1200" height="630" loading="lazy">

      <h2 id="networks-and-coverage">Networks and coverage</h2>
      <p>{c['net_intro']}</p>
      <ul>
{net_html}
      </ul>
      <p>None of the three includes a local phone number — they're data-only. Use WhatsApp, FaceTime or other internet calling.</p>

      <h2 id="tips">{c['tips_title']}</h2>
      <ul>
{tips_html}
      </ul>

      <h2 id="how-much-data">How much data you need</h2>
      <p>Using the rates from the <a href="esim-data-calculator.html">trip data calculator</a> — three hours a day of maps, messaging and browsing, an hour of social media and an hour of music, with 40% of your time on WiFi:</p>
      <ul>
        <li><strong>7 days:</strong> about 3.6 GB → a 5 GB plan</li>
        <li><strong>14 days:</strong> about 7.2 GB → a 10 GB plan</li>
        <li><strong>21 days:</strong> about 10.9 GB → a 20 GB plan, or 10 GB plus another small plan</li>
      </ul>
      <p>Streaming video or tethering a laptop changes the picture fast — use <a href="#find-your-plan">Find your plan</a> above or the full <a href="esim-data-calculator.html">calculator</a>.</p>

      <h2 id="setting-up-before-you-fly">Setting up before you fly</h2>
      <ol>
        <li><strong>Check your phone is eSIM-compatible and carrier-unlocked.</strong> A phone locked to your home carrier won't accept another provider's eSIM.</li>
        <li><strong>Install the eSIM at home over WiFi.</strong> Installation needs a connection; activation can wait. Saily plans can be activated any time within 180 days of purchase and switch on automatically when you arrive.</li>
        <li><strong>On landing, set the eSIM as your data line and turn on data roaming for it.</strong> That's normal for travel eSIMs and doesn't cost extra.</li>
        <li><strong>Turn off data roaming on your home SIM</strong> so it can still receive calls and texts without running up charges.</li>
      </ol>

      <p>More country guides: {more}. Comparing providers? See <a href="saily-vs-airalo.html">Saily vs Airalo</a> and <a href="saily-vs-holafly.html">Saily vs Holafly</a> across {len(ALL_PAGES)} destinations, or the <a href="saily-alternatives.html">best Saily alternatives</a>.</p>

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
        <a class="related-card" href="esim-data-calculator.html">
          <span class="tag">Free tool</span>
          <h3>How Much Data Do I Need for My Trip?</h3>
        </a>
        <a class="related-card" href="{c['related_href']}">
          <span class="tag">{c['related_tag']}</span>
          <h3>{c['related_title']}</h3>
        </a>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="cta-band">
        <div class="eyebrow" style="justify-content:center;">HEADING TO {c['name'].upper()}?</div>
        <h2>Sort your data before you board</h2>
        <p>Install a Saily {c.get('plan_name', c['name'])} plan at home and it switches on when you land — 10% off with code TRAVELCONNECTLY, applied automatically. Add a VPN for hotel and café WiFi.</p>
        <div class="hero-ctas">
          <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily" style="width:auto;">Get Saily for {c['name']} →</a>
          <a href="{NORD}" target="_blank" rel="sponsored noopener" class="btn btn-nord" style="width:auto;">Get NordVPN →</a>
        </div>
      </div>
    </div>
  </section>"""

    pagekit.TODAY = c.get("date", DATE)
    build(
        c["slug"], c["title"], c["desc"], c["keywords"], c["og_title"], c["og_desc"], c["og_image"], c["headline"],
        c["faq"], main,
        f'<a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">Get Saily</a>',
        # data-custom keeps fix_site.py from replacing this plan-specific sticky button.
        f'<div class="sticky-cta" data-custom="plan">\n  <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">{c["sticky_label"]}</a>\n  <span class="sub">{COUPON_STICKY}</span>\n</div>',
        CSS, PLANPICK_JS,
    )


HOLAFLY = [11.90, 20.50, 27.50, 36.50, 50.50, 73.90]  # 3, 5, 7, 10, 15, 30 days — same price in all four countries
TRUST = ["Hotspot allowed", "Activates when you land", "180 days to activate"]

JAPAN = dict(
    slug="best-esim-for-japan", name="Japan", name_h1="Japan",
    airalo_url="https://www.airalo.com/japan-esim", holafly_url="https://esim.holafly.com/esim-japan/",
    sticky_label="Japan eSIM · from $3.99 →",
    sticky_sub="5 GB/30 days $10.99 · 10 GB $17.99",
    headline="Best eSIM for Japan (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Japan 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Japan eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (KDDI, SoftBank), how much data you need, and setup.",
    keywords="best eSIM for Japan, Japan eSIM, Saily Japan, Airalo Japan, Holafly Japan, Japan eSIM unlimited data, eSIM vs pocket WiFi Japan",
    og_title="Best eSIM for Japan 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Japan eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-japan.jpg",
    photo="photo-esim.jpg", photo_alt="Traveler using a smartphone on mobile data while waiting on a train platform",
    qa_label="Most 1–3 week trips",
    qa_reason="Same price as Airalo on 30-day plans, runs on KDDI and SoftBank, and switches on when you land.",
    qa_plan="10 GB · 30 days", qa_price="$17.99", qa_cta="Get Saily Japan 10 GB →",
    qa_trust=["KDDI + SoftBank", "Hotspot allowed", "180 days to activate"],
    qa_chips=[("Light use:", "Saily 5 GB · 30 days", 10.99, "Saily"), ("Cheapest unlimited:", "Airalo 7 days", 26.50, "Airalo")],
    takeaways=[
        "<strong>At 30-day validity Saily and Airalo cost the same</strong> within a cent — 10 GB is $17.99 vs $18.00.",
        "<strong>Airalo's 7- and 15-day plans are up to $1 cheaper</strong> if your trip fits that window.",
        "<strong>Cheapest unlimited at every length: Airalo</strong> ($26.50 for 7 days). Saily states 5 GB a day at full speed.",
        "<strong>Data-only, no Japanese number.</strong> Install at home over WiFi; Saily activates when you land.",
    ],
    lede="Japan runs on your phone: train transfers, walking directions through stations with a dozen exits, and pointing your camera at a menu to translate it. Here's what a Japan eSIM actually costs, which one fits your trip, and how to set it up before you fly.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(7.99, 30)], [(7.50, 3), (8.00, 7)]),
        ("5 GB", [(10.99, 30)], [(10.00, 7), (10.50, 15), (11.00, 30)]),
        ("10 GB", [(17.99, 30)], [(17.00, 7), (17.50, 15), (18.00, 30)]),
        ("20 GB", [(24.99, 30)], [(24.00, 15), (25.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at 30-day validity the two are effectively the same price. Airalo is 50 cents to $1 cheaper if you're sure your trip fits a shorter 7- or 15-day window. Saily's plans are simpler — almost everything lasts 30 days, so a delayed flight or an extra few days won't cost you.",
    unl=[(3, 11.99, 11.50, HOLAFLY[0]), (5, 18.99, 17.00, HOLAFLY[1]), (7, 26.99, 26.50, HOLAFLY[2]),
         (10, 34.99, 34.50, HOLAFLY[3]), (15, 48.99, 48.00, HOLAFLY[4]), (30, 71.99, 69.00, HOLAFLY[5])],
    unl_note="Airalo was the cheapest unlimited option at every length, though only by 50 cents to $3. Saily also sells every length from 1 to 30 days. Unlimited is worth it if you'll stream video or tether a laptop on mobile data; for maps, messaging and social media, a 10 GB plan covers most two-week trips for far less.",
    picks=[
        f'<strong>Most travelers (1–3 weeks, normal use):</strong> Saily 5 GB or 10 GB. Same price as Airalo\'s 30-day plans, activates on arrival, and <a href="{SAILY}" target="_blank" rel="sponsored noopener">you can add another plan in the app</a> if you run low.',
        "<strong>Short trip, fixed dates, lowest price:</strong> Airalo's 7- or 15-day plans shave off up to $1.",
        "<strong>Heavy users who want unlimited:</strong> Airalo was cheapest on every length; Saily's clearly stated 5 GB/day full-speed allowance is the easiest to plan around; Holafly suits you if you want to share data by hotspot.",
        "<strong>Japan as one stop on a longer Asia trip:</strong> a regional plan can beat several single-country plans. Saily and Airalo both sell Asia plans — compare them against buying each country separately.",
    ],
    net_intro="Japan has several nationwide networks, including NTT Docomo, KDDI (au) and SoftBank. Travel eSIMs connect as roaming users on one or more of them:",
    networks=[
        "<strong>Saily:</strong> partners with KDDI and SoftBank; 4G/LTE and 5G where available.",
        "<strong>Airalo:</strong> SoftBank, plus one other network listed on its site.",
        "<strong>Holafly:</strong> KDDI and SoftBank; 4G/LTE and 5G where available.",
    ],
    tips_title="Japan tips",
    tips=[
        "<strong>Two networks help outside the cities.</strong> In rural areas and mountain towns one network may be stronger than the other.",
        "<strong>eSIM vs pocket WiFi:</strong> an eSIM needs nothing collected or returned; pocket WiFi can serve a whole group but must be picked up, charged and returned. A physical tourist SIM suits unlocked phones without eSIM support.",
        "<strong>VPNs are legal in Japan.</strong> You'll lean on hotel, station and café WiFi to save data — see <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>, or <a href=\"best-vpn-for-streaming-netflix-abroad.html\">the streaming guide</a> for your home library.",
        "<strong>Camera translation and constant map use in big stations add up</strong> — round your data estimate up rather than down.",
    ],
    faq=[
        ("Do I need an eSIM for Japan?",
         "You don't strictly need one, but mobile data makes Japan much easier: train connections, Google Maps walking directions and camera translation of menus and signs all need a connection. An eSIM is usually cheaper than roaming and quicker than buying a SIM or renting pocket WiFi at the airport."),
        ("What is the cheapest eSIM for Japan?",
         "On 29 September 2026, the cheapest fixed-data plans were within a few cents of each other: Saily charged $10.99 for 5 GB valid 30 days and Airalo $11.00 for the same. Airalo was slightly cheaper for short-validity and unlimited plans, for example $26.50 for 7 days unlimited versus $26.99 at Saily and $27.50 at Holafly."),
        ("Which network do Japan travel eSIMs use?",
         "Saily says it partners with KDDI and SoftBank, Holafly lists KDDI and SoftBank, and Airalo lists SoftBank plus one other network. KDDI (au) and SoftBank are two of Japan's major nationwide networks."),
        ("Do Japan eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Keep your home SIM active if you need to receive texts such as bank codes, but turn off its data roaming to avoid charges."),
        ("Is it legal to use a VPN in Japan?",
         "Yes. VPNs are legal in Japan, and using one on hotel, station or café WiFi is a sensible precaution."),
    ],
    related_href="best-vpn-for-airport-hotel-wifi.html", related_tag="Public WiFi", related_title="Best VPN for Airport &amp; Hotel WiFi Security",
)

THAILAND = dict(
    slug="best-esim-for-thailand", name="Thailand", name_h1="Thailand",
    airalo_url="https://www.airalo.com/thailand-esim", holafly_url="https://esim.holafly.com/esim-thailand/",
    sticky_label="Thailand eSIM · from $2.99 →",
    sticky_sub="5 GB/30 days $7.99 · 10 GB $10.99",
    headline="Best eSIM for Thailand (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Thailand 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Thailand eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (AIS, True), how much data you need, and setup.",
    keywords="best eSIM for Thailand, Thailand eSIM, Saily Thailand, Airalo Thailand, Holafly Thailand, Thailand eSIM unlimited data, Thailand tourist SIM",
    og_title="Best eSIM for Thailand 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Thailand eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-thailand.jpg",
    photo="photo-solo.jpg", photo_alt="Solo female traveler with a backpack checking her phone in a train station",
    qa_label="Most 1–3 week trips",
    qa_reason="Cheapest or within a cent on 30-day plans up to 10 GB and on every unlimited length it sells.",
    qa_plan="10 GB · 30 days", qa_price="$10.99", qa_cta="Get Saily Thailand 10 GB →",
    qa_trust=TRUST,
    qa_chips=[("Unlimited week:", "Saily 7 days", 20.99, "Saily"), ("Heavy use:", "Airalo 50 GB · 30 days", 27.50, "Airalo")],
    takeaways=[
        "<strong>Saily is cheapest or within a cent</strong> at 30-day validity for 1–10 GB (10 GB for $10.99).",
        "<strong>Unlimited:</strong> Saily and Airalo are within a cent of each other; Holafly costs about $6 more for a week.",
        "<strong>Heavy users:</strong> Airalo's 50 GB for $27.50 is the best value per GB.",
        "<strong>Coverage is strong in cities and on popular islands</strong>, thinner in national parks and on boats.",
    ],
    lede="Grab rides, island ferry times, hotel check-ins and translating street-food menus all run through your phone in Thailand. Here's what a Thailand eSIM actually costs from the three biggest travel-eSIM brands, and which one fits your trip.",
    fixed=[
        ("1 GB", [(2.99, 7)], [(4.00, 3)]),
        ("3 GB", [(5.99, 30)], [(5.50, 3), (6.00, 7)]),
        ("5 GB", [(7.99, 30)], [(7.00, 7), (7.50, 15), (8.00, 30)]),
        ("10 GB", [(10.99, 30)], [(10.00, 7), (10.50, 15), (11.00, 30)]),
        ("20 GB", [(19.99, 30)], [(17.50, 15), (18.00, 30)]),
        ("50 GB", [], [(27.50, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at 30-day validity, Saily is the cheapest or within a cent for 1–10 GB. Airalo's 3- and 7-day plans are up to $1 cheaper if your trip fits that window, it's about $2 cheaper at 20 GB, and it's the only one selling 50 GB — the best value if you'll use a lot of data.",
    unl=[(3, None, 9.50, HOLAFLY[0]), (5, 14.99, 15.00, HOLAFLY[1]), (7, 20.99, 21.00, HOLAFLY[2]),
         (10, 30.99, 31.00, HOLAFLY[3]), (15, 38.99, 39.00, HOLAFLY[4]), (30, 48.99, 49.00, HOLAFLY[5])],
    unl_note="Saily and Airalo are effectively tied on unlimited — Saily is a cent cheaper at every length both sell, and Saily also sells 20- and 25-day plans ($43.99 and $47.99). Holafly costs noticeably more in Thailand, from about $6 more for a week to $25 more for a month.",
    picks=[
        f'<strong>Most travelers (1–3 weeks):</strong> Saily 5 GB or 10 GB — cheapest or tied, valid 30 days, and <a href="{SAILY}" target="_blank" rel="sponsored noopener">you can add another plan in the app</a> if you run low.',
        "<strong>Heavy users on a month-long trip:</strong> Airalo's 50 GB for $27.50 is the best value per GB here.",
        "<strong>A weekend or quick stopover:</strong> Airalo's 3-day unlimited ($9.50), or Saily's 1 GB ($2.99) if you mostly need maps and messages.",
        "<strong>Island-hopping or long days out:</strong> unlimited from Saily or Airalo means you won't ration maps and photos; Holafly works too but costs more here.",
        "<strong>Thailand as part of a Southeast Asia trip:</strong> compare a regional Asia plan against separate country plans — both Saily and Airalo sell them.",
    ],
    net_intro="Thailand's main mobile networks are AIS and True (True merged with DTAC in 2023). Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Thai networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> True, plus one other network listed on its site.",
        "<strong>Holafly:</strong> True / DTAC, with 5G where available.",
    ],
    tips_title="Thailand tips",
    tips=[
        "<strong>Coverage is strong in cities and popular islands</strong>, but can thin out in national parks, on boats and in remote hill country — download offline maps before day trips.",
        "<strong>Many hotels, cafés and co-working spaces have free WiFi.</strong> Use a VPN on those shared networks; see <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Ride-hailing and delivery apps need data</strong>, so make sure your eSIM is working before you leave the airport.",
        "<strong>Keep your home SIM active for bank texts</strong> (with its data roaming off) — useful when you pay for bookings with a home card.",
    ],
    faq=[
        ("What is the best eSIM for Thailand?",
         "On 29 September 2026, Saily was the cheapest or within a cent for 30-day plans up to 10 GB and for every unlimited length it sells in Thailand, with 5 GB for $7.99 and 10 GB for $10.99. Airalo was cheaper for shorter 3- and 7-day plans and for 20 GB, and is the only one of the three selling 50 GB ($27.50)."),
        ("How much is an eSIM for Thailand?",
         "Prices started at $2.99 for 1 GB (Saily, 7 days). A typical 10 GB plan cost about $11, and unlimited data cost about $21 for a week or $49 for 30 days from Saily or Airalo."),
        ("Which network is best in Thailand?",
         "AIS and True are Thailand's main networks. Airalo lists True as its primary network and Holafly lists True / DTAC; Saily doesn't name its Thai partners on its plan page."),
        ("Do Thailand eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp, LINE or FaceTime for calls. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
        ("Is it legal to use a VPN in Thailand?",
         "Using a VPN for privacy and security is legal in Thailand. Using one on hotel and café WiFi is a sensible precaution."),
    ],
    related_href="best-vpn-for-backpacking.html", related_tag="Backpacking", related_title="Best VPN for Backpacking on a Budget",
)

USA = dict(
    slug="best-esim-for-usa", name="USA", name_h1="the USA",
    airalo_url="https://www.airalo.com/united-states-esim", holafly_url="https://esim.holafly.com/esim-usa/",
    sticky_label="USA eSIM · from $3.49 →",
    sticky_sub="Unlimited 7 days $24.99 · 10 GB/30 days $22.99",
    headline="Best eSIM for the USA (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for USA 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="USA eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (T-Mobile, AT&T), how much data you need, and setup.",
    keywords="best eSIM for USA, USA eSIM, United States eSIM, Saily USA, Airalo USA, Holafly USA, USA eSIM unlimited data, eSIM for US travel",
    og_title="Best eSIM for the USA 2026: Saily vs Airalo vs Holafly",
    og_desc="Real USA eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-usa.jpg",
    photo="photo-wifi.jpg", photo_alt="Traveler using a phone on airport WiFi at a departure gate with planes outside",
    qa_label="Trips up to ~2 weeks",
    qa_reason="Cheapest unlimited from 5 to 30 days — and in the US, a week of unlimited costs about the same as 10 GB.",
    qa_plan="Unlimited · 7 days", qa_price="$24.99", qa_cta="Get Saily USA unlimited →",
    qa_trust=["Hotspot allowed", "Activates when you land", "Optional US number"],
    qa_chips=[("Layover or one busy day:", "Saily 1 day unlimited", 3.49, "Saily"), ("Cheapest 30-day 10 GB:", "Airalo", 22.50, "Airalo")],
    takeaways=[
        "<strong>Unlimited is often the better buy in the US:</strong> Saily's 7-day unlimited ($24.99) costs about the same as 10 GB for 30 days ($22.99).",
        "<strong>Cheapest unlimited from 5 to 30 days:</strong> Saily. <strong>Cheapest 30-day 5–20 GB:</strong> Airalo, by about 50 cents; it also sells 50 GB for $42.",
        "<strong>Hawaii is covered</strong> by Saily's US plan. <strong>Alaska is unclear</strong> — confirm with support before an Alaska trip.",
        "<strong>Data-only eSIMs can't receive SMS codes.</strong> Saily offers an optional US number if a service needs one.",
    ],
    lede="The US is big, car-dependent and app-driven: ride-hailing, navigation between cities and mobile tickets all need data. Mobile data costs more here than in most countries, which makes choosing the right plan size matter. Here's what a US eSIM actually costs.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(8.99, 30)], [(8.50, 3), (9.00, 7)]),
        ("5 GB", [(13.99, 30)], [(12.50, 7), (13.00, 15), (13.50, 30)]),
        ("10 GB", [(22.99, 30)], [(21.50, 7), (22.00, 15), (22.50, 30)]),
        ("20 GB", [(36.99, 30)], [(36.00, 15), (36.50, 30)]),
        ("50 GB", [], [(42.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at 30-day validity Airalo is about 50 cents cheaper for 5, 10 and 20 GB, while Saily is cheaper for small plans (3 GB for 30 days at $8.99 versus $9.00 for Airalo's 7-day plan). Airalo's 50 GB for $42 is striking value next to its 20 GB at $36.50.",
    unl=[(3, 11.99, 11.50, HOLAFLY[0]), (5, 17.99, 18.50, HOLAFLY[1]), (7, 24.99, 25.00, HOLAFLY[2]),
         (10, 33.99, 34.00, HOLAFLY[3]), (15, 45.99, 46.00, HOLAFLY[4]), (30, 67.99, 68.00, HOLAFLY[5])],
    unl_note="Saily was the cheapest unlimited option from 5 to 30 days, and also sells a 1-day unlimited plan for $3.49 — handy for a layover. Airalo was cheapest for 3 days. Holafly costs a little more but is the only one to name both AT&T and T-Mobile as its networks.",
    picks=[
        f'<strong>Trips up to about two weeks:</strong> Saily unlimited — the cheapest from 5 to 30 days, and <a href="{SAILY}" target="_blank" rel="sponsored noopener">about the same price as a big fixed plan</a> for a week.',
        "<strong>A month with moderate use:</strong> Airalo's 30-day 10 GB ($22.50) or 50 GB ($42) plans.",
        "<strong>A layover or one busy day:</strong> Saily's 1-day unlimited ($3.49).",
        "<strong>Road trips through rural areas and national parks:</strong> coverage varies by network there, so Holafly's two named networks (AT&T and T-Mobile) are worth the small premium.",
    ],
    net_intro="The three nationwide US networks are AT&T, T-Mobile and Verizon. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its US networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> T-Mobile, plus one other network listed on its site.",
        "<strong>Holafly:</strong> AT&amp;T and T-Mobile, with 5G where available.",
    ],
    tips_title="USA tips",
    tips=[
        "<strong>Coverage is excellent in cities and along interstates</strong>, but national parks, mountain roads and deserts have real dead zones. Download offline maps before long drives.",
        "<strong>Hawaii and Alaska:</strong> Saily's own Hawaii page says its Hawaii plan is the same as its US plan and works across the USA. Alaska is less clear — reviewers disagree on whether US travel eSIMs connect there, and I found no definitive statement from Airalo or Holafly either — so confirm with the provider's support before an Alaska trip.",
        "<strong>Free WiFi is everywhere</strong> — hotels, coffee chains, airports — and so are shared networks worth protecting with a VPN. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Some US services send verification codes by SMS</strong> to a US number. A data-only eSIM can't receive them. Saily offers an optional US phone number with a text plan, but check that the service you need accepts it.",
        "<strong>Tethering a laptop is common on work trips.</strong> Saily states no hotspot restrictions; Holafly allows 1 GB a day of hotspot sharing.",
    ],
    faq=[
        ("What is the best eSIM for the USA?",
         "On 29 September 2026, Saily had the cheapest unlimited plans from 5 to 30 days (for example $24.99 for 7 days), while Airalo was about 50 cents cheaper for 30-day 5, 10 and 20 GB plans and sells 50 GB for $42."),
        ("How much is an eSIM for the USA?",
         "Prices started at $3.99 for 1 GB (Saily, 7 days). A 10 GB plan cost about $22.50–$23 for 30 days, and unlimited data cost about $25 for a week or $68 for 30 days from Saily or Airalo."),
        ("Is unlimited data worth it in the USA?",
         "Often, yes. Because US data is expensive, a week of unlimited data from Saily ($24.99) costs about the same as a 10 GB plan ($22.99), so unlimited is usually the better value for trips of around a week."),
        ("Which network do US travel eSIMs use?",
         "Airalo lists T-Mobile as its primary network and Holafly lists AT&T and T-Mobile. Saily doesn't name its US partners on its plan page."),
        ("Can I get a US phone number with a travel eSIM?",
         "Standard travel eSIMs are data-only. Saily offers an optional US phone number with a call and text plan as an add-on in its app."),
        ("Does a US eSIM work in Hawaii and Alaska?",
         "Saily says its Hawaii plan is the same as its US plan and can be used across the USA, so Hawaii is covered. Alaska coverage is less clear: reviewers disagree, and Airalo and Holafly don't state it clearly either, so confirm with the provider's support before an Alaska trip."),
    ],
    related_href="best-vpn-for-business-travelers.html", related_tag="Business travel", related_title="Best VPN for Business Travelers",
)

TURKEY = dict(
    slug="best-esim-for-turkey", name="Turkey", name_h1="Turkey",
    airalo_url="https://www.airalo.com/turkey-esim", holafly_url="https://esim.holafly.com/esim-turkey/",
    sticky_label="Turkey eSIM · from $3.99 →",
    sticky_sub="5 GB/30 days $9.99 · install before you go",
    headline="Best eSIM for Turkey (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Turkey 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Turkey eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (Turkcell, Türk Telekom), app restrictions, and setup.",
    keywords="best eSIM for Turkey, Turkey eSIM, Türkiye eSIM, Saily Turkey, Airalo Turkey, Holafly Turkey, Turkey eSIM unlimited data, Istanbul eSIM",
    og_title="Best eSIM for Turkey 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Turkey eSIM prices compared, plus what to set up before you arrive.",
    og_image="og-esim-turkey.jpg",
    photo="photo-connected.jpg", photo_alt="Traveler with a laptop, suitcase and passport staying connected at an airport",
    qa_label="Light use, up to 5 GB",
    qa_reason="Cheapest or tied on 30-day plans up to 5 GB. For unlimited, Airalo is cheaper — see below.",
    qa_plan="5 GB · 30 days", qa_price="$9.99", qa_cta="Get Saily Turkey 5 GB →",
    qa_trust=["Install before you arrive", "Hotspot allowed", "180 days to activate"],
    qa_chips=[("Cheapest unlimited:", "Airalo 15 days", 39.00, "Airalo"), ("Heavy use:", "Airalo 50 GB · 30 days", 34.50, "Airalo")],
    takeaways=[
        "<strong>Saily is cheapest or tied</strong> for 30-day plans up to 5 GB ($9.99 for 5 GB).",
        "<strong>Airalo is the cheapest unlimited at every length</strong> — 15 days for $39.00 vs $48.99 at Saily.",
        "<strong>Install your eSIM and VPN before you arrive.</strong> Saily says its app may be limited in Turkey.",
        "<strong>Holafly names Turkcell and Türk Telekom</strong>, which can help coverage outside the big cities.",
    ],
    lede="Istanbul's ferries and trams, Cappadocia balloon bookings and coastal bus connections all go smoother with data. Turkey also has one quirk worth knowing before you fly: some apps and sites can be hard to reach once you're there, so setup order matters.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(6.99, 30)], [(6.00, 3), (6.50, 7)]),
        ("5 GB", [(9.99, 30)], [(9.00, 7), (9.50, 15), (10.00, 30)]),
        ("10 GB", [(15.99, 30)], [(14.50, 7), (15.00, 15), (15.50, 30)]),
        ("20 GB", [(22.99, 30)], [(22.00, 15), (22.50, 30)]),
        ("50 GB", [], [(34.50, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> Saily is a cent cheaper at 5 GB for 30 days and its 3 GB plan lasts a full month; Airalo is about 50 cents cheaper at 10 and 20 GB, and sells 50 GB for $34.50.",
    unl=[(3, None, 11.50, HOLAFLY[0]), (5, 18.99, 18.50, HOLAFLY[1]), (7, 26.99, 24.50, HOLAFLY[2]),
         (10, 34.99, 34.50, HOLAFLY[3]), (15, 48.99, 39.00, HOLAFLY[4]), (30, 71.99, 69.00, HOLAFLY[5])],
    unl_note="Airalo was the cheapest unlimited option at every length in Turkey — by $2.50 for a week and almost $10 for 15 days compared with Saily. Holafly costs more but runs on Turkcell and Türk Telekom.",
    picks=[
        f'<strong>Light use (maps, messaging, some social):</strong> Saily 5 GB for $9.99, valid 30 days — <a href="{SAILY}" target="_blank" rel="sponsored noopener">cheapest or tied among 30-day plans</a>. Airalo\'s 7-day 5 GB ($9.00) is cheaper if your trip is a week.',
        "<strong>Unlimited data:</strong> Airalo — cheapest at every length, with the biggest saving on 15-day plans.",
        "<strong>Heavy fixed use over a month:</strong> Airalo's 50 GB for $34.50.",
        "<strong>Travel beyond the big cities:</strong> Holafly names two networks (Turkcell and Türk Telekom), which can help coverage in rural areas.",
    ],
    net_intro="Turkey's main mobile networks are Turkcell, Vodafone and Türk Telekom. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Turkish networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> Türk Telekom (listed as Turk Telekom / Avea).",
        "<strong>Holafly:</strong> Turkcell and Türk Telekom, with 5G where available.",
    ],
    tips_title="Turkey tips: set up before you arrive",
    tips=[
        "<strong>Install everything at home.</strong> Saily's own Turkey page warns that access to its app may be limited in Turkey because of local restrictions, and advises setting up the eSIM before traveling. The same logic applies to any app you'll rely on.",
        "<strong>Install your VPN app before you go, too.</strong> Access to some websites and services, including some VPN providers' sites, has been restricted in Turkey at times — downloading the app there can be harder than doing it at home. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Coverage is good in cities and along the coast</strong>; in mountain areas and parts of the east, download offline maps before long drives.",
        "<strong>Keep your home SIM active for bank texts</strong> with its data roaming turned off.",
    ],
    faq=[
        ("What is the best eSIM for Turkey?",
         "On 29 September 2026, Saily was cheapest or tied for 30-day plans up to 5 GB (5 GB for $9.99), while Airalo was cheaper for shorter plans, for 10 GB and above, and for unlimited data at every length, for example $39.00 for 15 days against $48.99 at Saily."),
        ("How much is an eSIM for Turkey?",
         "Prices started at $3.99 for 1 GB (Saily, 7 days). A 10 GB plan cost about $15.50–$16 for 30 days, and unlimited data cost from $24.50 for a week at Airalo."),
        ("Can I buy an eSIM once I'm in Turkey?",
         "It's better not to rely on it. Saily says access to its app may be limited in Turkey, so buy and install your eSIM at home over WiFi, then let it activate when you land."),
        ("Which network do Turkey travel eSIMs use?",
         "Airalo lists Türk Telekom; Holafly lists Turkcell and Türk Telekom. Saily doesn't name its Turkish partners on its plan page."),
        ("Can I use a VPN in Turkey?",
         "Travelers commonly use VPNs in Turkey, but access to some VPN providers' websites and apps has been restricted at times, so install and sign in to your VPN before you travel."),
    ],
    related_href="best-vpn-for-streaming-netflix-abroad.html", related_tag="Streaming", related_title="Best VPN for Streaming Netflix &amp; BBC iPlayer Abroad",
)

# ---- Added 9 Oct 2026: prices checked that day in USD on saily.com, airalo.com (currency=USD) and
# esim.holafly.com (USD table, spot-checked live at 7 days). Holafly prices differ by country here.
OCT9 = dict(checked="9 Oct 2026", checked_long="9 October 2026", date="2026-10-09")
EU_ROAMING_FAQ = ("Do I need a travel eSIM if I live in the EU?",
                  "Often not. Under EU roaming rules, many EU mobile plans can be used across the EU at no extra cost, within your operator's fair-use limits. Check your plan first; a travel eSIM makes sense if your allowance is small or you're coming from outside the EU.")

CANADA = dict(
    OCT9, slug="best-esim-for-canada", name="Canada", name_h1="Canada", saily_fup="3 GB",
    airalo_url="https://www.airalo.com/canada-esim", holafly_url="https://esim.holafly.com/esim-canada/",
    sticky_label="Canada eSIM · from $5.29 →",
    sticky_sub="Unlimited 5 days $19.99 · 7 days $28.99",
    headline="Best eSIM for Canada (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Canada 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Canada eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (Bell, Telus), how much data you need, and setup.",
    keywords="best eSIM for Canada, Canada eSIM, Saily Canada, Airalo Canada, Holafly Canada, Canada eSIM unlimited data, eSIM for Canada travel",
    og_title="Best eSIM for Canada 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Canada eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-canada.jpg",
    photo="photo-business.jpg", photo_alt="Business traveler working on a laptop in an airport terminal",
    qa_label="Trips of 5 days to a month",
    qa_reason="Cheapest unlimited from 5 to 30 days. Canadian data is pricey, so 5 days of unlimited costs about the same as 5 GB.",
    qa_plan="Unlimited · 7 days", qa_price="$28.99", qa_cta="Get Saily Canada unlimited →",
    qa_trust=TRUST,
    qa_chips=[("Shorter trip:", "Saily 5 days unlimited", 19.99, "Saily"), ("Cheapest 30-day 10 GB:", "Airalo", 23.00, "Airalo")],
    takeaways=[
        "<strong>Canadian data is expensive, so unlimited often wins:</strong> Saily's 5-day unlimited ($19.99) costs about the same as a 5 GB plan ($17.99).",
        "<strong>Cheapest unlimited from 5 to 30 days: Saily</strong> — $28.99 for a week vs $32.00 at Airalo and $36.50 at Holafly.",
        "<strong>For 10 GB or more over a month, Airalo is cheaper:</strong> 10 GB for $23.00 vs $30.99 at Saily.",
        "<strong>Saily's Canada unlimited is 3 GB a day at full speed</strong>, then up to 1 Mbps — less than the 5 GB a day it offers in many countries.",
    ],
    lede="Canada is huge and spread out: long drives between cities, national parks with patchy signal, and transit apps, ride-hailing and mobile tickets in the cities. Mobile data costs more here than in most of Europe or Asia, so the plan you pick matters. Here's what a Canada eSIM actually costs.",
    fixed=[
        ("1 GB", [(5.29, 7)], [(7.00, 3)]),
        ("3 GB", [(12.99, 30)], [(8.00, 3), (9.00, 7)]),
        ("5 GB", [(17.99, 30)], [(14.00, 7), (15.00, 15), (18.00, 30)]),
        ("10 GB", [(30.99, 30)], [(18.00, 7), (20.00, 15), (23.00, 30)]),
        ("20 GB", [(43.99, 30)], [(34.00, 15), (37.00, 30)]),
        ("50 GB", [], [(84.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> small plans are close, but from 10 GB up Airalo is much cheaper in Canada — $23.00 for 10 GB over 30 days against $30.99 at Saily, and $18.00 if your trip fits a 7-day window. Saily is cheaper for 1 GB, and its 3 GB plan lasts 30 days instead of 3 or 7.",
    unl=[(3, None, 19.00, 19.90), (5, 19.99, 27.00, 28.90), (7, 28.99, 32.00, 36.50),
         (10, 33.99, 35.00, 39.50), (15, 43.99, 45.00, 50.50), (30, 85.99, 86.00, 95.90)],
    unl_note="Saily was the cheapest unlimited option from 5 to 30 days — by $7 for 5 days and $3 for a week — and also sells 20- and 25-day plans ($56.99 and $72.99). Airalo was cheapest for 3 days. Holafly costs the most here, but names two networks, Bell and Telus.",
    picks=[
        f'<strong>Trips of 5 days to a month:</strong> Saily unlimited — the cheapest from 5 to 30 days, and <a href="{SAILY}" target="_blank" rel="sponsored noopener">5 days of unlimited costs about the same as 5 GB</a>.',
        "<strong>A month with moderate use:</strong> Airalo's 30-day 10 GB ($23.00) or 20 GB ($37.00).",
        "<strong>A short city break with light use:</strong> Saily's 1 GB for 7 days ($5.29), or Airalo's 3 GB for 7 days ($9.00).",
        "<strong>Canada and the US on one trip:</strong> a Canada-only plan won't work across the border. Saily and Airalo both sell North America regional plans that include Canada — compare one against two separate country plans.",
        "<strong>Road trips through national parks:</strong> coverage depends on the network outside the cities, so Holafly's two named networks (Bell and Telus) may be worth the premium.",
    ],
    net_intro="Canada's three national networks are Bell, Rogers and Telus. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Canadian networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> Bell.",
        "<strong>Holafly:</strong> Bell and Telus, with 5G where available.",
    ],
    tips_title="Canada tips",
    tips=[
        "<strong>Coverage is strong in cities and along major highways</strong>, but large parts of the north, many back roads and much of the national parks have no signal at all. Download offline maps before long drives and hikes.",
        "<strong>Mobile data is expensive in Canada</strong>, so lean on hotel, café and airport WiFi — with a VPN on shared networks. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Visiting the US too?</strong> Check that your plan covers both countries before you cross. See <a href=\"best-esim-for-usa.html\">the USA eSIM guide</a> for US-only prices.",
        "<strong>Keep your home SIM active for bank texts</strong> with its data roaming turned off.",
    ],
    faq=[
        ("What is the best eSIM for Canada?",
         "On 9 October 2026, Saily had the cheapest unlimited plans from 5 to 30 days (for example $28.99 for 7 days), while Airalo was clearly cheaper for 30-day plans of 10 GB or more, with 10 GB for $23.00 against $30.99 at Saily."),
        ("How much is an eSIM for Canada?",
         "Prices started at $5.29 for 1 GB (Saily, 7 days). A 10 GB plan cost $23.00 for 30 days at Airalo, and unlimited data cost from $19.99 for 5 days or $28.99 for a week at Saily."),
        ("Is unlimited data worth it in Canada?",
         "Often, yes. Because Canadian data is expensive, Saily's 5-day unlimited plan ($19.99) cost about the same as a 5 GB plan ($17.99 at Saily, $18.00 at Airalo). Saily's Canada unlimited plan gives 3 GB a day at full speed, then up to 1 Mbps."),
        ("Which network do Canada travel eSIMs use?",
         "Airalo lists Bell, and Holafly lists Bell and Telus. Saily doesn't name its Canadian partners on its plan page. Bell, Rogers and Telus are Canada's three national networks."),
        ("Does a Canada eSIM work in the USA?",
         "A Canada-only plan doesn't. If you're visiting both, compare a North America regional plan, which Saily and Airalo both sell, against buying a separate US plan."),
        ("Do Canada eSIMs include a phone number?",
         "These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Saily also offers an optional phone number with a call and text plan as an add-on in its app."),
    ],
    related_href="best-esim-for-usa.html", related_tag="eSIM · USA", related_title="Best eSIM for the USA (2026)",
)

ITALY = dict(
    OCT9, slug="best-esim-for-italy", name="Italy", name_h1="Italy",
    airalo_url="https://www.airalo.com/italy-esim", holafly_url="https://esim.holafly.com/esim-italy/",
    sticky_label="Italy eSIM · from $3.99 →",
    sticky_sub="Unlimited 7 days $22.99 · 3 GB/30 days $8.99",
    headline="Best eSIM for Italy (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Italy 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Italy eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (WindTre, Vodafone), how much data you need, and setup.",
    keywords="best eSIM for Italy, Italy eSIM, Saily Italy, Airalo Italy, Holafly Italy, Italy eSIM unlimited data, eSIM for Rome",
    og_title="Best eSIM for Italy 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Italy eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-italy.jpg",
    photo="photo-nomads.jpg", photo_alt="Laptop open on a table at an outdoor cafe, a typical digital nomad remote work setup",
    qa_label="Trips of 5 days to a month",
    qa_reason="Cheapest unlimited from 5 to 30 days — a cent below Airalo — with 5 GB a day at full speed.",
    qa_plan="Unlimited · 7 days", qa_price="$22.99", qa_cta="Get Saily Italy unlimited →",
    qa_trust=TRUST,
    qa_chips=[("Light use:", "Saily 3 GB · 30 days", 8.99, "Saily"), ("Cheapest 30-day 10 GB:", "Airalo", 19.00, "Airalo")],
    takeaways=[
        "<strong>Unlimited: Saily and Airalo are effectively tied</strong> — Saily is a cent cheaper from 5 to 30 days ($22.99 vs $23.00 for a week).",
        "<strong>Fixed data: Airalo is $1–3 cheaper</strong> at 30-day validity (10 GB for $19.00 vs $20.99).",
        "<strong>Holafly is close on price in Italy</strong> — under $1 more for a week — and names Vodafone and WindTre.",
        "<strong>Visiting more than Italy?</strong> A Europe plan can beat separate country plans; Saily's starts at $4.99 for 35 countries.",
    ],
    lede="Train tickets and platform changes, maps through old-town street grids, museum time slots and restaurant bookings — most of an Italy trip runs through your phone. Here's what an Italy eSIM actually costs from the three biggest travel-eSIM brands, and which one fits your trip.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(8.99, 30)], [(7.00, 3), (7.50, 7)]),
        ("5 GB", [(12.99, 30)], [(10.00, 7), (11.00, 15), (12.00, 30)]),
        ("10 GB", [(20.99, 30)], [(17.00, 7), (18.00, 15), (19.00, 30)]),
        ("20 GB", [(28.99, 30)], [(25.00, 15), (26.00, 30)]),
        ("50 GB", [], [(35.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> on fixed data Airalo is cheaper in Italy — about $1 at 5 GB, $2 at 10 GB and $3 at 20 GB for 30 days, and more if your trip fits a 7- or 15-day window. Its 50 GB for $35.00 is the best value per GB. Saily's 3 GB plan is the only small plan here that lasts a full 30 days.",
    unl=[(3, None, 11.00, 11.90), (5, 16.99, 17.00, 17.50), (7, 22.99, 23.00, 23.90),
         (10, 31.99, 32.00, 32.90), (15, 43.99, 44.00, 44.50), (30, 63.99, 64.00, 64.50)],
    unl_note="All three are within about $1 of each other in Italy. Saily is a cent cheaper than Airalo at every length both sell, and also sells 20- and 25-day plans ($54.99 and $59.99); Airalo is the only one with a 3-day plan ($11.00). Holafly is under $1 more and names Vodafone and WindTre as its networks.",
    picks=[
        f'<strong>Most trips of 5 days or more:</strong> Saily unlimited — <a href="{SAILY}" target="_blank" rel="sponsored noopener">a cent cheaper than Airalo</a>, 5 GB a day at full speed, and no hotspot limits.',
        "<strong>Light, fixed use over a month:</strong> Airalo's 30-day 5 GB ($12.00) or 10 GB ($19.00), $1–2 cheaper than Saily's.",
        "<strong>A 2–3 day city break:</strong> Airalo's 3-day unlimited ($11.00), or Saily's 1 GB ($3.99, 7 days) if you mostly need maps.",
        "<strong>Italy as part of a wider Europe trip:</strong> compare a Europe plan — Saily's starts at $4.99 for 35 countries, Airalo's EU + UK plan at $4.00 — against separate country plans.",
    ],
    net_intro="Italy's main mobile networks are TIM, Vodafone, WindTre and Iliad. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Italian networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> WindTre, plus Vodafone and Iliad.",
        "<strong>Holafly:</strong> Vodafone and WindTre, with 5G where available.",
    ],
    tips_title="Italy tips",
    tips=[
        "<strong>Coverage is good in cities and along the main rail lines</strong>; in mountain valleys, on some coastal roads and in small hill towns it can drop. Download offline maps before day trips.",
        "<strong>Save train tickets and museum bookings offline</strong> (or as screenshots) in case you lose signal in a station or tunnel.",
        "<strong>Hotel and café WiFi is common but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Coming from another EU country?</strong> Your home plan may already include roaming in Italy — check before you buy an eSIM.",
    ],
    faq=[
        ("What is the best eSIM for Italy?",
         "On 9 October 2026, Saily had the cheapest unlimited plans from 5 to 30 days, a cent below Airalo (for example $22.99 for 7 days), while Airalo was $1–3 cheaper for 30-day fixed-data plans, with 10 GB for $19.00 against $20.99 at Saily."),
        ("How much is an eSIM for Italy?",
         "Prices started at $3.99 for 1 GB (Saily, 7 days). A 10 GB plan cost $19–21 for 30 days, and unlimited data cost about $23 for a week or $64 for 30 days from any of the three."),
        ("Which network do Italy travel eSIMs use?",
         "Airalo lists WindTre as its primary network, plus Vodafone and Iliad; Holafly lists Vodafone and WindTre. Saily doesn't name its Italian partners on its plan page."),
        EU_ROAMING_FAQ,
        ("Do Italy eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
    ],
    related_href="best-esim-for-spain.html", related_tag="eSIM · Spain", related_title="Best eSIM for Spain (2026)",
)

SPAIN = dict(
    OCT9, slug="best-esim-for-spain", name="Spain", name_h1="Spain",
    airalo_url="https://www.airalo.com/spain-esim", holafly_url="https://esim.holafly.com/esim-spain/",
    sticky_label="Spain eSIM · from $3.99 →",
    sticky_sub="Unlimited 7 days $22.99 · 5 GB/30 days $9.99",
    headline="Best eSIM for Spain (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Spain 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Spain eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (Orange, Movistar, Vodafone), how much data you need, and setup.",
    keywords="best eSIM for Spain, Spain eSIM, Saily Spain, Airalo Spain, Holafly Spain, Spain eSIM unlimited data, eSIM for Barcelona",
    og_title="Best eSIM for Spain 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Spain eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-spain.jpg",
    photo="photo-budget.jpg", photo_alt="Backpackers adjusting travel packs at a budget hostel entrance",
    qa_label="Trips of 5–10 days",
    qa_reason="Cheapest unlimited for 5, 7 and 10 days, with 5 GB a day at full speed and no hotspot limits.",
    qa_plan="Unlimited · 7 days", qa_price="$22.99", qa_cta="Get Saily Spain unlimited →",
    qa_trust=TRUST,
    qa_chips=[("Cheapest 30-day 10 GB:", "Airalo", 14.00, "Airalo"), ("Unlimited for 2 weeks:", "Airalo 15 days", 43.00, "Airalo")],
    takeaways=[
        "<strong>Unlimited for 5–10 days: Saily is cheapest</strong> — $22.99 for a week vs $23.50 at Airalo and $24.50 at Holafly.",
        "<strong>Unlimited for 15 or 30 days: Airalo</strong>, by 99 cents.",
        "<strong>Fixed data: Airalo is $1–3 cheaper</strong> at 30-day validity (10 GB for $14.00 vs $15.99).",
        "<strong>Holafly names four Spanish networks</strong> — Orange, Movistar, Vodafone and Yoigo.",
    ],
    lede="Metro and bus apps in Madrid and Barcelona, high-speed train tickets, restaurant reviews and beach-town maps — Spain is easy with data. Here's what a Spain eSIM actually costs from the three biggest travel-eSIM brands, and which one fits your trip.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(6.99, 30)], [(5.50, 3), (6.00, 7)]),
        ("5 GB", [(9.99, 30)], [(8.00, 7), (8.50, 15), (9.00, 30)]),
        ("10 GB", [(15.99, 30)], [(13.00, 7), (13.50, 15), (14.00, 30)]),
        ("20 GB", [(22.99, 30)], [(19.00, 15), (20.00, 30)]),
        ("50 GB", [], [(39.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> Airalo is cheaper for fixed data in Spain — about $1 at 5 GB, $2 at 10 GB and $3 at 20 GB for 30 days — and sells 50 GB for $39.00. Saily's 3 GB plan is the only small plan that lasts a full 30 days.",
    unl=[(3, None, 11.00, 11.90), (5, 16.99, 17.00, 18.50), (7, 22.99, 23.50, 24.50),
         (10, 31.99, 32.00, 33.50), (15, 43.99, 43.00, 45.90), (30, 63.99, 63.00, 66.50)],
    unl_note="Saily was cheapest for 5, 7 and 10 days and also sells 20- and 25-day plans ($54.99 and $59.99); Airalo was cheapest for 3, 15 and 30 days, by up to 99 cents. Holafly costs $1–3.50 more but names four Spanish networks.",
    picks=[
        f'<strong>Trips of 5–10 days:</strong> Saily unlimited — <a href="{SAILY}" target="_blank" rel="sponsored noopener">the cheapest at those lengths</a>, with 5 GB a day at full speed and no hotspot limits.',
        "<strong>Two weeks or a month of unlimited:</strong> Airalo's 15-day ($43.00) or 30-day ($63.00) plans.",
        "<strong>Light, fixed use:</strong> Airalo's 30-day 5 GB ($9.00) or 10 GB ($14.00).",
        "<strong>Spain as part of a wider Europe trip:</strong> compare a Europe plan — Saily's starts at $4.99 for 35 countries, Airalo's EU + UK plan at $4.00 — against separate country plans.",
    ],
    net_intro="Spain's main mobile networks include Movistar, Orange, Vodafone and Yoigo. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Spanish networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> Orange.",
        "<strong>Holafly:</strong> Orange, Movistar, Vodafone and Yoigo, with 5G where available.",
    ],
    tips_title="Spain tips",
    tips=[
        "<strong>Coverage is strong in cities and along the coasts</strong>; in the interior, mountain areas and on some rural roads it can thin out. Download offline maps before road trips.",
        "<strong>Save train tickets offline</strong> — high-speed lines run through long tunnels where signal drops.",
        "<strong>Hotel, café and beach-bar WiFi is everywhere but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Coming from another EU country?</strong> Your home plan may already include roaming in Spain — check before you buy an eSIM.",
    ],
    faq=[
        ("What is the best eSIM for Spain?",
         "On 9 October 2026, Saily had the cheapest unlimited plans for 5 to 10 days ($22.99 for 7 days), Airalo was cheapest for 15- and 30-day unlimited by 99 cents, and Airalo was $1–3 cheaper for 30-day fixed-data plans, with 10 GB for $14.00 against $15.99 at Saily."),
        ("How much is an eSIM for Spain?",
         "Prices started at $3.99 for 1 GB (Saily, 7 days). A 10 GB plan cost $14–16 for 30 days, and unlimited data cost about $23 for a week or $63–64 for 30 days from Saily or Airalo."),
        ("Which network do Spain travel eSIMs use?",
         "Airalo lists Orange; Holafly lists Orange, Movistar, Vodafone and Yoigo. Saily doesn't name its Spanish partners on its plan page."),
        EU_ROAMING_FAQ,
        ("Do Spain eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
    ],
    related_href="best-esim-for-italy.html", related_tag="eSIM · Italy", related_title="Best eSIM for Italy (2026)",
)

# ---- Europe regional plans, checked 9 Oct 2026: saily.com/esim-europe (35 countries), airalo.com/europe-esim
# (41 countries) and /eu-plus-uk-esim (28), esim.holafly.com/esim-europe (33; 7 days spot-checked live).
Y, N = "✓", "—"
COVERAGE_ROWS = [
    ("Countries covered", "35", "41", "33", "28"),
    ("All 27 EU countries", Y, Y, Y, Y),
    ("United Kingdom", Y, Y, Y, Y),
    ("Switzerland", Y, Y, Y, N),
    ("Norway, Iceland", Y, Y, Y, N),
    ("Turkey", Y, Y, N, N),
    ("Albania, Bosnia, Montenegro, North Macedonia, Serbia", N, Y, N, N),
    ("Kosovo", N, N, N, N),
    ("Ukraine, Georgia", N, Y, N, N),
    ("Andorra", N, N, Y, N),
]
EUROPE_COVERAGE = """
      <h2 id="countries-covered">Which countries are covered</h2>
      <p>"Europe" means something different to each provider, and the differences are mostly outside the EU. Check every country on your route before you buy.</p>
      <div class="table-wrap glance">
        <table class="fit cov">
          <thead><tr><th>Country</th><th>Saily Europe</th><th>Airalo Europe</th><th>Holafly Europe</th><th>Airalo EU+UK</th></tr></thead>
          <tbody>
""" + "\n".join(f"            <tr><td>{r[0]}</td>" + "".join(f"<td>{v}</td>" for v in r[1:]) + "</tr>" for r in COVERAGE_ROWS) + """
          </tbody>
        </table>
      </div>
      <p class="price-note">From each provider's own country list, checked 9 October 2026.</p>
      <p><strong>Visiting the Balkans, including Kosovo?</strong> None of the Europe-wide plans covers Kosovo. Saily sells a separate Balkans plan covering Albania, Bosnia and Herzegovina, Bulgaria, Croatia, Greece, Kosovo, Montenegro, North Macedonia and Serbia, from $5.99 for 1 GB.</p>
"""

EUROPE = dict(
    OCT9, slug="best-esim-for-europe", name="Europe", name_h1="Europe",
    airalo_url="https://www.airalo.com/europe-esim", holafly_url="https://esim.holafly.com/esim-europe/",
    sticky_label="Europe eSIM · from $4.99 →",
    sticky_sub="35 countries · unlimited week $26.99",
    headline="Best eSIM for Europe (2026): Saily vs Airalo vs Holafly, Prices and Coverage Compared",
    title="Best eSIM for Europe 2026: 35–41 Countries Compared, Real Prices | TravelConnectly",
    desc="One eSIM for all of Europe? Saily, Airalo and Holafly Europe plans compared on real, dated prices and on which of 33–41 countries each covers (UK, Switzerland, Turkey, the Balkans).",
    keywords="best eSIM for Europe, Europe eSIM, Saily Europe, Airalo Europe, Holafly Europe, Europe eSIM unlimited data, eSIM for Europe and UK, Balkans eSIM",
    og_title="Best eSIM for Europe 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Europe eSIM prices and country coverage compared, plus when a single-country plan is cheaper.",
    og_image="og-esim-europe.jpg",
    photo="photo-longterm.jpg", photo_alt="Two backpackers with large travel backpacks walking down a hostel corridor",
    qa_label="One-week trip, several countries",
    qa_reason="Cheapest Europe-wide unlimited week (by a cent), 35 countries including the UK, Switzerland and Turkey, 5 GB a day at full speed.",
    qa_plan="Unlimited · 7 days", qa_price="$26.99", qa_cta="Get Saily Europe unlimited →",
    qa_trust=["35 countries", "Hotspot allowed", "Activates in your first country"],
    qa_chips=[("Only EU + UK?", "Airalo EU + UK 7 days", 23.50, "Airalo", "https://www.airalo.com/eu-plus-uk-esim"),
              ("Longer trip:", "Airalo Europe 15 days unlimited", 49.00, "Airalo")],
    takeaways=[
        "<strong>Coverage differs more than price:</strong> Airalo covers 41 countries including the western Balkans and Ukraine; Saily covers 35 including Turkey; Holafly covers 33.",
        "<strong>Saily is cheapest for a 7-day unlimited plan</strong> ($26.99) and 30-day 5 GB ($19.49), each by a cent. Airalo is cheaper for most other lengths and sizes.",
        "<strong>Only visiting EU countries and the UK?</strong> Airalo's EU + UK plan is cheaper still — $23.50 for a week of unlimited.",
        "<strong>Mostly one country?</strong> A single-country plan is often cheaper — Saily Italy unlimited is $22.99 a week vs $26.99 for Europe.",
    ],
    lede="One eSIM for a whole trip is the main appeal of a Europe plan: it switches on in your first country and keeps working as you cross borders by train, bus or ferry. But each provider's \"Europe\" covers a different list of countries, and a regional plan isn't always the cheapest option. Here's what each costs and covers.",
    fixed=[
        ("1 GB", [(4.99, 7)], [(5.00, 3)]),
        ("3 GB", [(12.49, 30)], [(10.00, 3), (11.00, 7)]),
        ("5 GB", [(19.49, 30)], [(18.50, 7), (19.00, 15), (19.50, 30)]),
        ("10 GB", [(35.99, 30)], [(26.00, 7), (28.00, 15), (31.00, 30)]),
        ("20 GB", [], [(47.00, 15), (48.00, 30)]),
        ("50 GB", [(95.99, 90)], [(70.00, 30), (100.00, 90)]),
    ],
    fixed_note="<strong>What that means:</strong> Saily is a cent cheaper for 5 GB over 30 days and its 3 GB plan lasts a full month, but Airalo is about $5 cheaper at 10 GB and sells 20 GB, which Saily's Europe plan doesn't. For long trips, Saily's 50 GB lasts 90 days for $95.99; Airalo's 50 GB is $70.00 for 30 days or $100.00 for 90, and it also sells 100 GB for 180 days ($185.00). Airalo's EU + UK plan is cheaper again if you stay inside the EU and the UK, for example 10 GB for 30 days at $24.00.",
    unl=[(3, None, 11.50, 11.90), (5, None, 19.50, 20.50), (7, 26.99, 27.00, 27.50),
         (10, 35.99, 35.00, 37.50), (15, 49.99, 49.00, 51.50), (30, 71.99, 71.00, 76.50)],
    unl_note="Across the three Europe-wide plans, Saily was cheapest for 7 days by a cent and Airalo for every other length, by up to $1. Saily also sells 20- and 25-day plans ($59.99 and $65.99). Holafly costs a little more. If you're only visiting EU countries and the UK, Airalo's EU + UK unlimited plans are cheaper: $23.50 for 7 days, $39.00 for 15 and $58.00 for 30.",
    picks=[
        f'<strong>A week across several countries, including the UK, Switzerland or Turkey:</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily Europe unlimited</a> — the cheapest Europe-wide week, with no hotspot limits.',
        "<strong>Only EU countries and the UK:</strong> Airalo's EU + UK plan is the cheapest option at most lengths.",
        "<strong>Including the western Balkans, Ukraine or Georgia:</strong> Airalo Europe (41 countries) is the only one of the three that covers them.",
        f'<strong>Kosovo, Albania and the Balkans:</strong> Saily\'s separate Balkans plan is the only one I found that covers Kosovo.',
        "<strong>Most of the trip in one country:</strong> a single-country plan is usually cheaper — see the <a href=\"best-esim-for-italy.html\">Italy</a>, <a href=\"best-esim-for-spain.html\">Spain</a> and <a href=\"best-esim-for-turkey.html\">Turkey</a> guides.",
    ],
    net_intro="Regional plans roam on local networks in each country:",
    networks=[
        "<strong>Saily:</strong> doesn't name networks on its Europe page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> names one to three networks per country in its coverage list — for example Orange and Bouygues in France, and EE, Three and Virgin Media O2 in the UK.",
        "<strong>Holafly:</strong> doesn't name networks on its Europe page; 4G/LTE and 5G where available.",
    ],
    tips_title="Europe tips",
    tips=[
        "<strong>EU residents may not need a travel eSIM at all.</strong> Under EU roaming rules, many EU mobile plans work across the EU at no extra cost, within fair-use limits — but not always in the UK, Switzerland, Turkey or the Balkans.",
        "<strong>Turn off data roaming on ferries and cruise ships</strong> unless you're sure your plan covers the onboard network — ships often use their own maritime network, which isn't a local network.",
        "<strong>Saily's regional plan starts in the first covered country you reach</strong>, so install it at home and it activates when you land.",
        "<strong>Train, hotel and café WiFi is everywhere but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
    ],
    faq=[
        ("What is the best eSIM for Europe?",
         "It depends on your route. On 9 October 2026, Saily had the cheapest Europe-wide 7-day unlimited plan ($26.99) and covers 35 countries including the UK, Switzerland and Turkey. Airalo's Europe plan covers the most countries (41, including the western Balkans and Ukraine) and was cheaper at most other lengths, and its EU + UK plan was cheapest if you only visit the EU and the UK."),
        ("How much is an eSIM for Europe?",
         "Prices started at $4.99 for 1 GB (Saily Europe, 7 days). A week of unlimited data cost about $27 on a Europe-wide plan, or $23.50 on Airalo's EU + UK plan. 10 GB for 30 days cost $31.00 at Airalo and $35.99 at Saily."),
        ("Does a Europe eSIM work in the UK and Switzerland?",
         "Yes, all three Europe-wide plans compared here — Saily, Airalo and Holafly — include the United Kingdom and Switzerland. Airalo's cheaper EU + UK plan includes the UK but not Switzerland."),
        ("Does a Europe eSIM cover Turkey and the Balkans?",
         "Saily's and Airalo's Europe plans include Turkey; Holafly's doesn't. Only Airalo's Europe plan includes Albania, Bosnia and Herzegovina, Montenegro, North Macedonia and Serbia. None of the three covers Kosovo, but Saily's separate Balkans plan does."),
        ("Is a Europe eSIM cheaper than a single-country eSIM?",
         "Not always. If most of your trip is in one country, a single-country plan is often cheaper: for example, Saily's Italy unlimited plan cost $22.99 for 7 days against $26.99 for its Europe plan."),
        ("Is there one eSIM that works in all of Europe?",
         "Not quite. Of the plans I checked, Airalo's Europe plan covers the most countries (41), Saily's covers 35 and Holafly's 33, and none of them covers Kosovo. Check every country on your route against each provider's list before you buy."),
        ("Does a Europe eSIM keep working when I cross a border?",
         "Yes — that's the point of a regional plan: one eSIM and one package across every covered country. Saily's Europe plan activates automatically when you arrive in the first covered country."),
        ("How much is a Europe eSIM for 2 weeks?",
         "For 15 days of unlimited data on a Europe-wide plan, Airalo cost $49.00, Saily $49.99 ($44.99 with my code TRAVELCONNECTLY) and Holafly $51.50 (checked 9 October 2026). If you only visit EU countries and the UK, Airalo's EU + UK plan cost $39.00 for 15 days."),
        ("What is the cheapest eSIM for Europe?",
         "For small amounts of data, Airalo's EU + UK plan started at $4.00 for 1 GB (3 days) and Saily's Europe plan at $4.99 (7 days). For 10 GB over 30 days, Airalo's EU + UK plan was cheapest at $24.00; on Europe-wide plans Airalo cost $31.00 and Saily $35.99 ($32.39 with my code)."),
        EU_ROAMING_FAQ,
    ],
    coverage_html=EUROPE_COVERAGE,
    related_href="best-esim-for-italy.html", related_tag="eSIM · Italy", related_title="Best eSIM for Italy (2026)",
)

# ---- Added 10 Oct 2026: prices checked that day in USD on saily.com, airalo.com (currency=USD) and
# esim.holafly.com (USD table, spot-checked live at 7 days).
OCT10 = dict(checked="10 Oct 2026", checked_long="10 October 2026", date="2026-10-10")

UK = dict(
    OCT10, slug="best-esim-for-uk", name="UK", name_h1="the UK",
    airalo_url="https://www.airalo.com/united-kingdom-esim", holafly_url="https://esim.holafly.com/esim-united-kingdom/",
    sticky_label="UK eSIM · from $4.49 →",
    sticky_sub="10 GB/30 days $18.99 · unlimited week $26.99",
    headline="Best eSIM for the UK (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for UK 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="UK eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (EE and others), EU roaming after Brexit, and setup.",
    keywords="best eSIM for UK, UK eSIM, United Kingdom eSIM, Saily UK, Airalo UK, Holafly UK, UK eSIM unlimited data, eSIM for London",
    og_title="Best eSIM for the UK 2026: Saily vs Airalo vs Holafly",
    og_desc="Real UK eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-uk.jpg",
    photo="photo-wifi-risk.jpg", photo_alt="Travelers using laptops and tablets on shared public WiFi in a crowded airport terminal",
    qa_label="Most 1–3 week trips",
    qa_reason="Cheapest or tied on every 30-day plan from 3 to 20 GB, and the cheapest unlimited week.",
    qa_plan="10 GB · 30 days", qa_price="$18.99", qa_cta="Get Saily UK 10 GB →",
    qa_trust=TRUST,
    qa_chips=[("Unlimited week:", "Saily 7 days", 26.99, "Saily"), ("Heavy use:", "Airalo 50 GB · 30 days", 39.00, "Airalo")],
    takeaways=[
        "<strong>Saily is cheapest by a cent on every 30-day plan from 5 to 20 GB</strong> — 10 GB is $18.99 vs $19.00 at Airalo.",
        "<strong>Unlimited:</strong> Saily is cheapest for a week ($26.99); Airalo is cheaper at every other length, by up to $3.",
        "<strong>Heavy users:</strong> Airalo's 50 GB for $39.00 is the best value per GB.",
        "<strong>Coming from the EU?</strong> Since Brexit, free EU roaming doesn't automatically cover the UK — check your plan.",
    ],
    lede="Contactless transport, train tickets, ride-hailing and walking directions all run through your phone in the UK, and since Brexit an EU phone plan may not cover it for free. Here's what a UK eSIM actually costs from the three biggest travel-eSIM brands, and which one fits your trip.",
    fixed=[
        ("1 GB", [(4.49, 7)], [(4.00, 3)]),
        ("3 GB", [(8.99, 30)], [(8.50, 3), (9.00, 7)]),
        ("5 GB", [(12.99, 30)], [(12.00, 7), (12.50, 15), (13.00, 30)]),
        ("10 GB", [(18.99, 30)], [(18.00, 7), (18.50, 15), (19.00, 30)]),
        ("20 GB", [(30.99, 30)], [(30.00, 15), (31.00, 30)]),
        ("50 GB", [], [(39.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at 30-day validity the two are effectively the same price, with Saily a cent cheaper. Airalo is up to $1 cheaper if your trip fits a 7- or 15-day window, and it's the only one selling 50 GB — $39.00, only $8 more than its 20 GB plan.",
    unl=[(3, None, 11.50, 11.90), (5, 18.99, 18.50, 20.50), (7, 26.99, 27.00, 27.50),
         (10, 34.99, 34.50, 37.50), (15, 48.99, 48.00, 51.50), (30, 71.99, 69.00, 76.50)],
    unl_note="Saily was cheapest for 7 days, by a cent, and also sells 20- and 25-day plans ($59.99 and $65.99). Airalo was cheapest at every other length, by up to $3. Holafly costs a little more but names several UK networks.",
    picks=[
        f'<strong>Most travelers (1–3 weeks):</strong> Saily 5 GB or 10 GB — <a href="{SAILY}" target="_blank" rel="sponsored noopener">a cent cheaper than Airalo</a> at 30-day validity, and it activates when you land.',
        "<strong>A week with heavy use:</strong> Saily's 7-day unlimited ($26.99).",
        "<strong>A month of heavy use:</strong> Airalo's 50 GB for $39.00, or its 30-day unlimited ($69.00).",
        "<strong>The UK plus mainland Europe:</strong> a Europe plan that includes the UK may beat two country plans — see <a href=\"best-esim-for-europe.html\">the Europe eSIM guide</a>.",
    ],
    net_intro="The UK's main mobile networks are EE, Virgin Media O2 and VodafoneThree (Vodafone and Three merged in 2025). Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its UK networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> EE.",
        "<strong>Holafly:</strong> lists Orange UK, T-Mobile UK, H3G UK, Virgin Media O2 UK and Vodafone UK, with 5G where available.",
    ],
    tips_title="UK tips",
    tips=[
        "<strong>Coverage is strong in cities and along main roads and rail lines</strong>; in the Scottish Highlands, parts of Wales and other rural areas it can drop. Download offline maps before road trips.",
        "<strong>EU residents: check your roaming terms.</strong> After Brexit, free EU roaming doesn't automatically include the UK; some EU operators still include it, others charge.",
        "<strong>Hotel, café and station WiFi is everywhere but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Keep your home SIM active for bank texts</strong> with its data roaming turned off.",
    ],
    faq=[
        ("What is the best eSIM for the UK?",
         "On 10 October 2026, Saily was a cent cheaper than Airalo on every 30-day plan from 5 to 20 GB (10 GB for $18.99) and cheapest for a 7-day unlimited plan ($26.99). Airalo was cheaper for other unlimited lengths and is the only one of the three selling 50 GB ($39.00)."),
        ("How much is an eSIM for the UK?",
         "Prices started at $4.00 for 1 GB (Airalo, 3 days). A 10 GB plan cost about $19 for 30 days, and unlimited data cost about $27 for a week or $69–72 for 30 days from Saily or Airalo."),
        ("Does my EU phone plan work in the UK?",
         "Not automatically. Since Brexit, the UK isn't covered by EU roaming rules, so whether your EU plan includes it depends on your operator. Check before you travel; a travel eSIM is a simple fallback."),
        ("Which network do UK travel eSIMs use?",
         "Airalo lists EE. Holafly lists several UK networks. Saily doesn't name its UK partners on its plan page."),
        ("Do UK eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
    ],
    related_href="best-esim-for-europe.html", related_tag="eSIM · Europe", related_title="Best eSIM for Europe (2026)",
)

FRANCE = dict(
    OCT10, slug="best-esim-for-france", name="France", name_h1="France",
    airalo_url="https://www.airalo.com/france-esim", holafly_url="https://esim.holafly.com/esim-france/",
    sticky_label="France eSIM · from $3.99 →",
    sticky_sub="5 GB/30 days $10.99 · 10 GB $16.99",
    headline="Best eSIM for France (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for France 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="France eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (Orange, SFR, Bouygues, Free), how much data you need, and setup.",
    keywords="best eSIM for France, France eSIM, Saily France, Airalo France, Holafly France, France eSIM unlimited data, eSIM for Paris",
    og_title="Best eSIM for France 2026: Saily vs Airalo vs Holafly",
    og_desc="Real France eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-france.jpg",
    photo="photo-streaming.jpg", photo_alt="Travelers relaxing on hostel bunk beds during downtime abroad",
    qa_label="Most 1–3 week trips",
    qa_reason="A cent cheaper than Airalo on every 30-day plan from 5 to 20 GB, and it switches on when you land.",
    qa_plan="10 GB · 30 days", qa_price="$16.99", qa_cta="Get Saily France 10 GB →",
    qa_trust=TRUST,
    qa_chips=[("Unlimited week:", "Airalo 7 days", 23.50, "Airalo"), ("Heavy use:", "Airalo 50 GB · 30 days", 35.00, "Airalo")],
    takeaways=[
        "<strong>Fixed data: Saily is a cent cheaper</strong> on every 30-day plan from 5 to 20 GB (10 GB for $16.99).",
        "<strong>Unlimited: Airalo is cheaper at most lengths</strong>, by 49 cents to $1 — $23.50 for a week vs $23.99 at Saily.",
        "<strong>Heavy users:</strong> Airalo's 50 GB for $35.00 is the best value per GB.",
        "<strong>Holafly names all four French networks</strong> — Orange, SFR, Bouygues Télécom and Free — but costs more.",
    ],
    lede="Metro and train apps, museum time slots, restaurant bookings and maps through Paris and the countryside — France is easier with data. Here's what a France eSIM actually costs from the three biggest travel-eSIM brands, and which one fits your trip.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(8.99, 30)], [(7.00, 3), (7.50, 7)]),
        ("5 GB", [(10.99, 30)], [(10.00, 7), (10.50, 15), (11.00, 30)]),
        ("10 GB", [(16.99, 30)], [(16.00, 7), (16.50, 15), (17.00, 30)]),
        ("20 GB", [(22.99, 30)], [(22.50, 15), (23.00, 30)]),
        ("50 GB", [], [(35.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at 30-day validity the two are effectively the same price, with Saily a cent cheaper. Airalo is up to $1 cheaper if your trip fits a 7- or 15-day window, and it's the only one selling 50 GB ($35.00).",
    unl=[(3, None, 11.00, 11.90), (5, 17.99, 17.00, 20.50), (7, 23.99, 23.50, 27.50),
         (10, 29.99, 29.00, 36.50), (15, 41.99, 42.00, 50.50), (30, 59.99, 59.00, 73.90)],
    unl_note="Airalo was cheapest for 3, 5, 7, 10 and 30 days, by 49 cents to $1; Saily was a cent cheaper for 15 days and also sells 20- and 25-day plans ($48.99 and $54.99). Holafly costs noticeably more in France — about $4 more for a week.",
    picks=[
        f'<strong>Most travelers (1–3 weeks):</strong> Saily 5 GB or 10 GB — <a href="{SAILY}" target="_blank" rel="sponsored noopener">a cent cheaper than Airalo</a> at 30-day validity, and it activates when you land.',
        "<strong>Unlimited data for a week:</strong> Airalo ($23.50), 49 cents less than Saily.",
        "<strong>A month of heavy use:</strong> Airalo's 50 GB for $35.00.",
        "<strong>France plus other European countries:</strong> compare a Europe plan — see <a href=\"best-esim-for-europe.html\">the Europe eSIM guide</a>.",
    ],
    net_intro="France's four mobile networks are Orange, SFR, Bouygues Télécom and Free Mobile. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its French networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> didn't name a French operator on its plan page.",
        "<strong>Holafly:</strong> Orange, SFR, Bouygues Télécom and Free Mobile, with 5G where available.",
    ],
    tips_title="France tips",
    tips=[
        "<strong>Coverage is strong in cities and along motorways and main rail lines</strong>; in mountain areas and some rural regions it can drop. Download offline maps before road trips.",
        "<strong>Save train and museum tickets offline</strong> in case you lose signal in a station or the metro.",
        "<strong>Hotel and café WiFi is common but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Coming from another EU country?</strong> Your home plan may already include roaming in France — check before you buy an eSIM.",
    ],
    faq=[
        ("What is the best eSIM for France?",
         "On 10 October 2026, Saily was a cent cheaper than Airalo on every 30-day plan from 5 to 20 GB (10 GB for $16.99), while Airalo was cheaper for most unlimited lengths ($23.50 for 7 days) and is the only one of the three selling 50 GB ($35.00)."),
        ("How much is an eSIM for France?",
         "Prices started at $3.99 for 1 GB (Saily, 7 days). A 10 GB plan cost about $17 for 30 days, and unlimited data cost about $24 for a week or $59–60 for 30 days from Saily or Airalo."),
        ("Which network do France travel eSIMs use?",
         "Holafly lists Orange, SFR, Bouygues Télécom and Free Mobile. Saily and Airalo don't name their French partners on their plan pages."),
        EU_ROAMING_FAQ,
        ("Do France eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
    ],
    related_href="best-esim-for-europe.html", related_tag="eSIM · Europe", related_title="Best eSIM for Europe (2026)",
)

GREECE = dict(
    OCT10, slug="best-esim-for-greece", name="Greece", name_h1="Greece",
    airalo_url="https://www.airalo.com/greece-esim", holafly_url="https://esim.holafly.com/esim-greece/",
    sticky_label="Greece eSIM · from $4.49 →",
    sticky_sub="Unlimited 5 days $18.99 · 7 days $26.99",
    headline="Best eSIM for Greece (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Greece 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Greece eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (Nova, Vodafone), island and ferry tips, and setup.",
    keywords="best eSIM for Greece, Greece eSIM, Saily Greece, Airalo Greece, Holafly Greece, Greece eSIM unlimited data, eSIM for Greek islands",
    og_title="Best eSIM for Greece 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Greece eSIM prices compared, plus island and ferry tips and how to set it up.",
    og_image="og-esim-greece.jpg",
    photo="photo-solo.jpg", photo_alt="Solo female traveler with a backpack checking her phone in a train station",
    qa_label="A week of island-hopping",
    qa_reason="Cheapest unlimited for 5 and 7 days (by a cent), 5 GB a day at full speed, and no hotspot limits.",
    qa_plan="Unlimited · 7 days", qa_price="$26.99", qa_cta="Get Saily Greece unlimited →",
    qa_trust=TRUST,
    qa_chips=[("Cheapest 30-day 10 GB:", "Airalo", 20.00, "Airalo"), ("Unlimited for 2 weeks:", "Airalo 15 days", 48.00, "Airalo")],
    takeaways=[
        "<strong>Unlimited for 5–7 days: Saily is cheapest</strong> by a cent — $26.99 for a week vs $27.00 at Airalo.",
        "<strong>Fixed data and longer unlimited: Airalo is cheaper</strong> — 10 GB for 30 days is $20.00 vs $22.99 at Saily.",
        "<strong>Heavy users:</strong> Airalo's 50 GB for $42.00 is the best value per GB.",
        "<strong>On ferries, turn data roaming off</strong> unless you're sure your plan covers the onboard network.",
    ],
    lede="Ferry times, island maps, beach-bar bookings and translation all go smoother with data in Greece. Here's what a Greece eSIM actually costs from the three biggest travel-eSIM brands, which one fits your trip, and what to know before you board a ferry.",
    fixed=[
        ("1 GB", [(4.49, 7)], [(4.00, 3)]),
        ("3 GB", [(9.99, 30)], [(8.50, 3), (9.00, 7)]),
        ("5 GB", [(13.99, 30)], [(11.00, 7), (11.50, 15), (12.00, 30)]),
        ("10 GB", [(22.99, 30)], [(19.00, 7), (19.50, 15), (20.00, 30)]),
        ("20 GB", [(35.99, 30)], [(35.00, 15), (35.50, 30)]),
        ("50 GB", [], [(42.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> Airalo is cheaper for fixed data in Greece — about $2 at 5 GB and $3 at 10 GB for 30 days — and its 50 GB for $42.00 costs only $6.50 more than its 20 GB plan. Saily's 3 GB plan is the only small plan here that lasts a full 30 days.",
    unl=[(3, None, 11.50, 11.90), (5, 18.99, 19.00, 20.50), (7, 26.99, 27.00, 27.50),
         (10, 34.99, 34.00, 37.50), (15, 48.99, 48.00, 51.50), (30, 71.99, 69.00, 76.50)],
    unl_note="Saily was cheapest for 5 and 7 days, by a cent, and also sells 20- and 25-day plans ($59.99 and $65.99). Airalo was cheapest for 3, 10, 15 and 30 days, by up to $3. Holafly costs a little more but names both Vodafone and Nova.",
    picks=[
        f'<strong>A 5–7 day trip with lots of maps, photos and video:</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily unlimited</a> — the cheapest at those lengths, with no hotspot limits.',
        "<strong>Moderate use over a longer trip:</strong> Airalo's 30-day 5 GB ($12.00) or 10 GB ($20.00).",
        "<strong>Two weeks or more of unlimited:</strong> Airalo's 15-day ($48.00) or 30-day ($69.00) plans.",
        "<strong>Greece plus other European countries:</strong> compare a Europe plan — see <a href=\"best-esim-for-europe.html\">the Europe eSIM guide</a>.",
    ],
    net_intro="Greece's main mobile networks are Cosmote, Vodafone and Nova. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Greek networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> Nova, plus Vodafone.",
        "<strong>Holafly:</strong> Vodafone and Nova, with 5G where available.",
    ],
    tips_title="Greece tips",
    tips=[
        "<strong>Coverage is good in towns and on popular islands</strong>, but can be patchy on smaller islands, in mountain villages and on remote beaches. Download offline maps and ferry tickets before day trips.",
        "<strong>Turn off data roaming on ferries</strong> unless you're sure your plan covers the onboard network — ships can connect phones to their own maritime network, which isn't a local network.",
        "<strong>Hotel, café and beach-bar WiFi is common but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Coming from another EU country?</strong> Your home plan may already include roaming in Greece — check before you buy an eSIM.",
    ],
    faq=[
        ("What is the best eSIM for Greece?",
         "On 10 October 2026, Saily had the cheapest unlimited plans for 5 and 7 days ($26.99 for a week), while Airalo was cheaper for fixed-data plans (10 GB for 30 days at $20.00 against $22.99 at Saily) and for unlimited plans of 10 days or more."),
        ("How much is an eSIM for Greece?",
         "Prices started at $4.00 for 1 GB (Airalo, 3 days). A 10 GB plan cost $20–23 for 30 days, and unlimited data cost about $27 for a week or $69–72 for 30 days from Saily or Airalo."),
        ("Do eSIMs work on Greek ferries and islands?",
         "On the islands, yes, wherever there's local coverage, though it can be patchy on smaller islands. At sea, phones can connect to a ship's own maritime network, which travel eSIMs generally don't treat as a local network, so turn data roaming off on board unless your plan says otherwise."),
        ("Which network do Greece travel eSIMs use?",
         "Airalo lists Nova and Vodafone; Holafly lists Vodafone and Nova. Saily doesn't name its Greek partners on its plan page."),
        EU_ROAMING_FAQ,
    ],
    related_href="best-esim-for-europe.html", related_tag="eSIM · Europe", related_title="Best eSIM for Europe (2026)",
)

MEXICO = dict(
    OCT10, slug="best-esim-for-mexico", name="Mexico", name_h1="Mexico", saily_fup="3 GB",
    airalo_url="https://www.airalo.com/mexico-esim", holafly_url="https://esim.holafly.com/esim-mexico/",
    sticky_label="Mexico eSIM · from $4.99 →",
    sticky_sub="3 GB valid 30 days $9.99 · install before you go",
    headline="Best eSIM for Mexico (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Mexico 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Mexico eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (Telcel, Movistar, AT&T), how much data you need, and setup.",
    keywords="best eSIM for Mexico, Mexico eSIM, Saily Mexico, Airalo Mexico, Holafly Mexico, Mexico eSIM unlimited data, eSIM for Cancun",
    og_title="Best eSIM for Mexico 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Mexico eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-mexico.jpg",
    photo="photo-backpacking.jpg", photo_alt="Hostel dormitory with bunk beds and backpacks, typical budget backpacking accommodation",
    qa_provider="Airalo",
    qa_label="Most trips",
    qa_reason="Cheapest on every 30-day plan from 5 GB up and on every unlimited length I checked.",
    qa_plan="10 GB · 30 days", qa_price="$18.50", qa_cta="See Airalo's Mexico plans →",
    qa_trust=["Movistar + AT&amp;T", "Unlimited from $10.50", "50 GB for $45"],
    qa_chips=[("Light use, 30 days:", "Saily 3 GB", 9.99, "Saily"), ("Want Telcel?", "Holafly 7 days unlimited", 24.50, "Holafly")],
    takeaways=[
        "<strong>Airalo is cheapest in Mexico</strong> — on every 30-day plan from 5 GB up (10 GB for $18.50 vs $23.99 at Saily) and on every unlimited length.",
        "<strong>Saily's 3 GB plan is the only small plan that lasts 30 days</strong> ($9.99) — handy for light use on a longer stay.",
        "<strong>Holafly is the only one that names Telcel</strong>, Mexico's largest network, and costs about $1 more than Airalo for a week.",
        "<strong>Saily's Mexico unlimited is 3 GB a day at full speed</strong>, then up to 1 Mbps.",
    ],
    lede="Ride-hailing, maps between ruins and beaches, restaurant reviews and translation all lean on mobile data in Mexico. Here's what a Mexico eSIM actually costs from the three biggest travel-eSIM brands — and here, the cheapest isn't the one I earn a commission from.",
    fixed=[
        ("1 GB", [(4.99, 7)], [(4.00, 3)]),
        ("3 GB", [(9.99, 30)], [(7.50, 3), (8.50, 7)]),
        ("5 GB", [(14.99, 30)], [(12.00, 7), (12.50, 15), (13.00, 30)]),
        ("10 GB", [(23.99, 30)], [(17.00, 7), (17.50, 15), (18.50, 30)]),
        ("20 GB", [(37.99, 30)], [(29.50, 15), (31.00, 30)]),
        ("50 GB", [], [(45.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> Airalo is clearly cheaper for fixed data in Mexico — about $2 at 5 GB, $5.50 at 10 GB and $7 at 20 GB for 30 days — and sells 50 GB for $45.00. Saily's only edge is its 3 GB plan lasting a full 30 days.",
    unl=[(3, None, 10.50, 11.50), (5, 17.99, 17.50, 18.50), (7, 24.99, 23.50, 24.50),
         (10, 31.99, 31.50, 32.90), (15, 43.99, 43.00, 44.90), (30, 71.99, 62.00, 66.50)],
    unl_note="Airalo was the cheapest unlimited option at every length, from 50 cents cheaper for 5 days to $10 cheaper than Saily for 30 days. Holafly was second-cheapest for a week ($24.50) and is the only one that names Telcel as a network. Saily also sells 20- and 25-day plans ($59.99 and $65.99).",
    picks=[
        "<strong>Most travelers:</strong> Airalo — cheapest for fixed data from 5 GB and for unlimited at every length. I don't earn a commission from Airalo.",
        f'<strong>Light use on a longer stay:</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily\'s 3 GB plan</a> ($9.99) is the only small plan that lasts 30 days.',
        "<strong>Travel beyond the main tourist areas:</strong> Holafly names Telcel, Mexico's largest network, for about $1 more than Airalo for a week.",
        "<strong>Mexico plus the US or Canada:</strong> compare a North America plan against two country plans — see <a href=\"best-esim-for-usa.html\">the USA eSIM guide</a>.",
    ],
    net_intro="Mexico's main mobile networks are Telcel, AT&amp;T and Movistar. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Mexican networks on its plan page; it lists 3G/4G/LTE/5G depending on the local network.",
        "<strong>Airalo:</strong> Movistar, plus AT&amp;T.",
        "<strong>Holafly:</strong> Movistar and Telcel, with 5G where available.",
    ],
    tips_title="Mexico tips",
    tips=[
        "<strong>Coverage is strong in cities and resort areas</strong>, but can be patchy on rural roads, in the mountains and around some archaeological sites. Download offline maps before day trips.",
        "<strong>Ride-hailing and delivery apps need data</strong>, so check your eSIM works before you leave the airport.",
        "<strong>Hotel and café WiFi is common but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Keep your home SIM active for bank texts</strong> with its data roaming turned off.",
    ],
    faq=[
        ("What is the best eSIM for Mexico?",
         "On 10 October 2026, Airalo was the cheapest for most trips: 10 GB for 30 days cost $18.50 against $23.99 at Saily, and Airalo had the cheapest unlimited plan at every length, for example $23.50 for 7 days. Saily's 3 GB plan ($9.99) was the only small plan valid for 30 days."),
        ("How much is an eSIM for Mexico?",
         "Prices started at $4.00 for 1 GB (Airalo, 3 days). A 10 GB plan cost $18.50 for 30 days at Airalo, and unlimited data cost from $23.50 for a week."),
        ("Which network do Mexico travel eSIMs use?",
         "Airalo lists Movistar and AT&T; Holafly lists Movistar and Telcel. Saily doesn't name its Mexican partners on its plan page. Telcel is Mexico's largest network."),
        ("Do Mexico eSIMs include a phone number?",
         "These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Saily also offers an optional phone number with a call and text plan as an add-on in its app."),
    ],
    related_href="best-esim-for-usa.html", related_tag="eSIM · USA", related_title="Best eSIM for the USA (2026)",
)

# ---- Added 12 Oct 2026: prices checked that day in USD on saily.com (coupon cookie cleared, list prices),
# airalo.com (currency=USD) and esim.holafly.com (USD table, spot-checked live at 7 days).
OCT12 = dict(checked="12 Oct 2026", checked_long="12 October 2026", date="2026-10-12")

CHINA = dict(
    OCT12, slug="best-esim-for-china", name="China", name_h1="China",
    airalo_url="https://www.airalo.com/china-esim", holafly_url="https://esim.holafly.com/esim-china/",
    sticky_label="China eSIM · from $4.49 →", sticky_sub="",
    headline="Best eSIM for China (2026): Saily vs Airalo vs Holafly, Prices and Blocked Apps",
    title="Best eSIM for China 2026: Saily vs Airalo vs Holafly, Google & WhatsApp | TravelConnectly",
    desc="China eSIM prices compared from each provider's site: Saily, Airalo and Holafly plans, which say Google, WhatsApp and Instagram work, networks, and what to set up before you fly.",
    keywords="best eSIM for China, China eSIM, eSIM China Google WhatsApp, Saily China, Airalo China, Holafly China, China eSIM VPN, China travel internet",
    og_title="Best eSIM for China 2026: Saily vs Airalo vs Holafly",
    og_desc="Real China eSIM prices, which ones say blocked apps work, and what to install before you fly.",
    og_image="og-esim-china.jpg",
    photo="photo-freevpn.jpg", photo_alt="Two travelers using a phone and reading in an airport waiting area",
    qa_label="Most 1–3 week trips",
    qa_reason="With my code, the cheapest 30-day plans from 5 GB, on China Telecom and China Unicom — and Saily says Google and Instagram work through its app's virtual location.",
    qa_plan="10 GB · 30 days", qa_price="$26.99", qa_cta="Get Saily China 10 GB →",
    qa_trust=["China Telecom + Unicom", "Hotspot allowed", "Set up before you fly"],
    qa_chips=[("WhatsApp without a VPN:", "Holafly 7 days", 27.50, "Holafly"), ("Unlimited week (list price):", "Airalo 7 days", 27.00, "Airalo")],
    takeaways=[
        "<strong>Google, WhatsApp and Instagram are blocked in China</strong> — how each eSIM handles that matters as much as price.",
        "<strong>Holafly says WhatsApp, Google and Instagram work without a VPN.</strong> Saily says Google and Instagram work through its app's virtual location, but WhatsApp needs a VPN. Airalo's page doesn't say.",
        "<strong>At list price Airalo is 49 cents to $4 cheaper</strong> on most plans; with my 10% code, Saily is cheapest for 30-day plans from 5 GB.",
        "<strong>Install everything before you fly</strong> — eSIM, VPN and apps. Saily warns its own app may be hard to reach inside China.",
    ],
    lede="Maps, translation, payments and ride-hailing all run on your phone in China — but Google, WhatsApp, Instagram and many Western apps are blocked there. Here's what a China eSIM costs, which providers say you can reach those apps, and what to set up before you fly.",
    fixed=[
        ("1 GB", [(4.49, 7)], [(4.00, 3)]),
        ("3 GB", [(10.99, 30)], [(9.50, 3), (10.50, 7)]),
        ("5 GB", [(15.99, 30)], [(14.50, 7), (15.00, 15), (15.50, 30)]),
        ("10 GB", [(26.99, 30)], [(24.50, 7), (25.50, 15), (26.50, 30)]),
        ("20 GB", [(39.99, 30)], [(39.00, 15), (40.00, 30)]),
        ("50 GB", [], [(49.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at list price the two are within 50 cents for 5–20 GB over 30 days; with my 10% code, Saily is cheaper on all of them. Airalo is the only one selling 50 GB ($49.00), and its 7-day plans are cheaper if your trip fits that window.",
    unl=[(3, None, 11.50, 11.90), (5, 22.99, 19.00, 20.50), (7, 29.99, 27.00, 27.50),
         (10, 35.99, 35.00, 37.50), (15, 49.99, 49.00, 51.50), (30, 72.99, 69.00, 76.50)],
    unl_note="At list price Airalo was the cheapest unlimited option at every length, by $1 to $4 against Saily; Holafly was in between for 5 and 7 days. With my code, Saily is cheaper from 7 days up — by a cent for a week and by $2.61 to $4 for 10 days or more. Saily also sells 20- and 25-day plans ($60.99 and $66.99).",
    picks=[
        "<strong>You need WhatsApp to just work:</strong> Holafly is the only one of the three that says WhatsApp, Google and Instagram work without a separate VPN, and says its China eSIM includes a VPN at no extra cost. I don't earn a commission from Holafly.",
        f'<strong>Best value for most trips:</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily with my code</a> — cheapest for 30-day plans from 5 GB, Google and Instagram through its virtual location; set up a VPN before you go for WhatsApp.',
        "<strong>Lowest list price for unlimited:</strong> Airalo, though its China page doesn't say whether blocked apps work.",
        "<strong>Hong Kong on the same trip:</strong> it needs a separate plan — mainland China plans don't cover it.",
    ],
    net_intro="China's three mobile networks are China Mobile, China Telecom and China Unicom. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> China Telecom and China Unicom; 5G where available, 4G/LTE elsewhere.",
        "<strong>Airalo:</strong> China Unicom.",
        "<strong>Holafly:</strong> China Mobile (listed as CMCC).",
    ],
    tips_title="China tips: set up before you fly",
    tips=[
        "<strong>Install your eSIM, a VPN and your key apps at home.</strong> VPN websites and many app downloads aren't reachable from inside China, and Saily warns its own app may be limited there.",
        "<strong>About VPNs:</strong> as Saily's China page puts it, VPNs aren't completely banned in China, but their use is restricted and unrestricted access is limited to licensed businesses. Hotel and café WiFi is subject to the same blocks, so plan how you'll reach WhatsApp and Google before you go — see <a href=\"best-vpn-for-airport-hotel-wifi.html\">the VPN guide for hotel and airport WiFi</a>.",
        "<strong>Set up Alipay or WeChat Pay before you travel.</strong> Mobile payments are used almost everywhere, and both apps accept many foreign cards.",
        "<strong>Hong Kong needs a separate plan.</strong> Saily and Holafly both say their mainland China plans don't work there.",
    ],
    faq=[
        ("Do I need a VPN in China if I have an eSIM?",
         "It depends on the eSIM. Holafly says WhatsApp, Google and Instagram work with its China eSIM without installing a separate VPN, and that a VPN is included. Saily says Google and Instagram work through its app's virtual location feature, but WhatsApp needs a VPN. Airalo's China page doesn't say. Whatever you choose, install your apps before you travel."),
        ("What is the best eSIM for China?",
         "On 12 October 2026, Airalo had the lowest list prices for most plans (10 GB for 30 days at $26.50, an unlimited week at $27.00). With my 10% code, Saily was cheaper for 30-day plans from 5 GB (10 GB for $24.29). Holafly costs a little more but is the only one that says WhatsApp works without a VPN."),
        ("How much is an eSIM for China?",
         "Prices started at $4.00 for 1 GB (Airalo, 3 days). A 10 GB plan cost $26.50–$26.99 for 30 days, and unlimited data cost about $27–30 for a week."),
        ("Does a China eSIM work in Hong Kong?",
         "No. Saily and Holafly both say their mainland China plans don't work in Hong Kong, so buy a separate Hong Kong plan."),
        ("Which network do China travel eSIMs use?",
         "Saily lists China Telecom and China Unicom, Airalo lists China Unicom, and Holafly lists China Mobile (CMCC)."),
    ],
    related_href="best-esim-for-japan.html", related_tag="eSIM · Japan", related_title="Best eSIM for Japan (2026)",
)

KOREA = dict(
    OCT12, slug="best-esim-for-south-korea", name="South Korea", name_h1="South Korea",
    airalo_url="https://www.airalo.com/south-korea-esim", holafly_url="https://esim.holafly.com/esim-south-korea/",
    sticky_label="South Korea eSIM · from $3.99 →", sticky_sub="",
    headline="Best eSIM for South Korea (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for South Korea 2026: Saily vs Airalo vs Holafly Prices | TravelConnectly",
    desc="South Korea eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (SK Telecom, LG U+), maps tips and setup.",
    keywords="best eSIM for South Korea, Korea eSIM, Saily Korea, Airalo Korea, Holafly Korea, South Korea eSIM unlimited data, eSIM for Seoul",
    og_title="Best eSIM for South Korea 2026: Saily vs Airalo vs Holafly",
    og_desc="Real South Korea eSIM prices compared, plus the map apps that actually work there.",
    og_image="og-esim-south-korea.jpg",
    photo="photo-esim.jpg", photo_alt="Traveler using a smartphone on mobile data while waiting on a train platform",
    qa_label="Most 1–3 week trips",
    qa_reason="A cent cheaper than Airalo on every 30-day plan from 5 to 20 GB, and the cheapest unlimited from 5 to 15 days.",
    qa_plan="10 GB · 30 days", qa_price="$18.99", qa_cta="Get Saily South Korea 10 GB →",
    qa_trust=TRUST,
    qa_chips=[("Unlimited week:", "Saily 7 days", 26.99, "Saily"), ("Heavy use:", "Airalo 50 GB · 30 days", 49.00, "Airalo")],
    takeaways=[
        "<strong>Saily is a cent cheaper</strong> on every 30-day plan from 5 to 20 GB (10 GB for $18.99).",
        "<strong>Unlimited: Saily is cheapest from 5 to 15 days</strong> — $26.99 for a week vs $27.50 at Holafly and $29.00 at Airalo.",
        "<strong>Google Maps is limited in Korea</strong> — download Naver Map or KakaoMap for walking and transit directions.",
        "<strong>Holafly names SK Telecom and LG U+</strong>; Airalo lists SK Telecom.",
    ],
    lede="Subway transfers, map directions, café hopping and translating menus — South Korea runs on fast mobile data. Here's what a South Korea eSIM actually costs from the three biggest travel-eSIM brands, and which one fits your trip.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(8.99, 30)], [(8.00, 3), (9.00, 7)]),
        ("5 GB", [(10.99, 30)], [(10.00, 7), (10.50, 15), (11.00, 30)]),
        ("10 GB", [(18.99, 30)], [(18.00, 7), (18.50, 15), (19.00, 30)]),
        ("20 GB", [(29.99, 30)], [(29.00, 15), (30.00, 30)]),
        ("50 GB", [], [(49.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at 30-day validity Saily is a cent cheaper on every size from 5 to 20 GB, and its 3 GB plan lasts a full month. Airalo is up to $1 cheaper if your trip fits a 7- or 15-day window, and it's the only one selling 50 GB ($49.00).",
    unl=[(3, None, 12.00, 12.50), (5, 18.99, 20.00, 20.50), (7, 26.99, 29.00, 27.50),
         (10, 34.99, 35.00, 36.50), (15, 48.99, 49.00, 50.50), (30, 71.99, 69.00, 73.90)],
    unl_note="Saily was cheapest from 5 to 15 days — by $2.01 against Airalo for a week — and also sells 20- and 25-day plans ($59.99 and $65.99). Airalo was cheapest for 3 and 30 days. Holafly was cheaper than Airalo for a week and names two Korean networks.",
    picks=[
        f'<strong>Most travelers (1–3 weeks):</strong> Saily 5 GB or 10 GB — <a href="{SAILY}" target="_blank" rel="sponsored noopener">a cent cheaper than Airalo</a>, valid 30 days, and it activates when you land.',
        "<strong>Heavy use for a week or two:</strong> Saily unlimited — the cheapest from 5 to 15 days.",
        "<strong>A month of heavy use:</strong> Airalo's 50 GB ($49.00) or 30-day unlimited ($69.00).",
        "<strong>Korea plus Japan:</strong> compare a regional Asia plan against two country plans — see the <a href=\"best-esim-for-japan.html\">Japan guide</a>.",
    ],
    net_intro="South Korea's three mobile networks are SK Telecom, KT and LG U+. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> didn't name its Korean networks on its plan page.",
        "<strong>Airalo:</strong> SK Telecom.",
        "<strong>Holafly:</strong> SK Telecom and LG U+, with 5G where available.",
    ],
    tips_title="South Korea tips",
    tips=[
        "<strong>Use Naver Map or KakaoMap.</strong> Google Maps shows maps in Korea but often can't give walking or driving directions; the Korean map apps can.",
        "<strong>Coverage is excellent in cities, including the subway</strong>, and good across most of the country; download offline maps before hiking in national parks.",
        "<strong>Café, subway and hotel WiFi is everywhere but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-airport-hotel-wifi.html\">the best VPN for hotel and airport WiFi</a>.",
        "<strong>Keep your home SIM active for bank texts</strong> with its data roaming turned off.",
    ],
    faq=[
        ("What is the best eSIM for South Korea?",
         "On 12 October 2026, Saily was a cent cheaper than Airalo on every 30-day plan from 5 to 20 GB (10 GB for $18.99) and had the cheapest unlimited plans from 5 to 15 days ($26.99 for a week). Airalo was cheaper for 3- and 30-day unlimited and is the only one of the three selling 50 GB."),
        ("How much is an eSIM for South Korea?",
         "Prices started at $3.99 for 1 GB (Saily, 7 days). A 10 GB plan cost about $19 for 30 days, and unlimited data cost from $26.99 for a week."),
        ("Does Google Maps work in South Korea?",
         "Partly. You can see maps, but walking and driving directions are limited, so most travelers use Naver Map or KakaoMap. Both work on a travel eSIM."),
        ("Which network do South Korea travel eSIMs use?",
         "Airalo lists SK Telecom; Holafly lists SK Telecom and LG U+. Saily doesn't name its Korean partners on its plan page."),
        ("Do South Korea eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use KakaoTalk, WhatsApp or other internet calling. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
    ],
    related_href="best-esim-for-japan.html", related_tag="eSIM · Japan", related_title="Best eSIM for Japan (2026)",
)

BALI = dict(
    OCT12, slug="best-esim-for-bali", name="Bali", name_h1="Bali &amp; Indonesia", plan_name="Indonesia",
    airalo_url="https://www.airalo.com/indonesia-esim", holafly_url="https://esim.holafly.com/esim-indonesia/",
    sticky_label="Bali eSIM · from $4.79 →", sticky_sub="",
    headline="Best eSIM for Bali & Indonesia (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Bali 2026: Saily vs Airalo vs Holafly Indonesia Prices | TravelConnectly",
    desc="Bali and Indonesia eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (Telkomsel, Indosat, XL), coverage and setup.",
    keywords="best eSIM for Bali, Bali eSIM, Indonesia eSIM, Saily Indonesia, Airalo Indonesia, Holafly Indonesia, Bali eSIM unlimited data, eSIM for Bali digital nomad",
    og_title="Best eSIM for Bali 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Bali and Indonesia eSIM prices compared, plus coverage and setup tips.",
    og_image="og-esim-bali.jpg",
    photo="photo-nomads.jpg", photo_alt="Laptop open on a table at an outdoor cafe, a typical digital nomad remote work setup",
    qa_label="A week in Bali",
    qa_reason="Cheapest unlimited for 5 and 7 days (by a cent), on Telkomsel — which Saily says covers Bali and most Indonesian islands.",
    qa_plan="Unlimited · 7 days", qa_price="$26.99", qa_cta="Get Saily Indonesia unlimited →",
    qa_trust=["Telkomsel network", "Hotspot allowed", "Activates when you land"],
    qa_chips=[("Cheapest 30-day 10 GB:", "Airalo", 21.00, "Airalo"), ("Long stay:", "Airalo 50 GB · 30 days", 49.00, "Airalo")],
    takeaways=[
        "<strong>Unlimited for 5–7 days: Saily is cheapest</strong> by a cent — $26.99 for a week vs $27.00 at Airalo and $27.50 at Holafly.",
        "<strong>Fixed data: Airalo is 49 cents to $1 cheaper</strong> at list price; with my 10% code, Saily is cheaper (10 GB for $19.79).",
        "<strong>Bali is covered by Indonesia plans.</strong> Saily runs on Telkomsel; Airalo lists 3, Indosat and Telkomsel; Holafly lists XL and Telkomsel.",
        "<strong>Long stays:</strong> Airalo's 50 GB for $49.00 is the best value per GB.",
    ],
    lede="Grab and Gojek rides, villa check-ins, scooter navigation and beach-club bookings all run through your phone in Bali. Travel eSIMs sell an Indonesia plan that covers Bali — here's what each costs and which fits your trip.",
    fixed=[
        ("1 GB", [(4.79, 7)], [(4.50, 3)]),
        ("3 GB", [(8.99, 30)], [(8.00, 3), (8.50, 7)]),
        ("5 GB", [(13.99, 30)], [(12.00, 7), (13.00, 15), (13.50, 30)]),
        ("10 GB", [(21.99, 30)], [(19.00, 7), (20.00, 15), (21.00, 30)]),
        ("20 GB", [(35.99, 30)], [(34.00, 15), (35.00, 30)]),
        ("50 GB", [], [(49.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> at list price Airalo is 49 cents to $1 cheaper at 30-day validity and up to $3 cheaper on 7- and 15-day plans; with my 10% code, Saily's 30-day plans come out cheaper. Saily's 3 GB plan is the only small plan that lasts a full month.",
    unl=[(3, None, 11.00, 11.90), (5, 18.99, 19.00, 20.50), (7, 26.99, 27.00, 27.50),
         (10, 34.99, 34.00, 37.50), (15, 48.99, 48.00, 51.50), (30, 71.99, 69.00, 76.50)],
    unl_note="Saily was cheapest for 5 and 7 days by a cent, and also sells 20- and 25-day plans ($59.99 and $65.99). Airalo was cheapest for 3, 10, 15 and 30 days, by up to $3. Holafly costs a little more.",
    picks=[
        f'<strong>A week of heavy use (maps, video, hotspot):</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily unlimited</a> — the cheapest for 5–7 days, with no hotspot limits.',
        "<strong>Moderate use:</strong> Airalo's 30-day 5 GB ($13.50) or 10 GB ($21.00) — or Saily's, which come out cheaper with my code.",
        "<strong>Digital nomads staying a month:</strong> Airalo's 50 GB ($49.00) or 30-day unlimited ($69.00).",
        "<strong>Bali plus other countries:</strong> check every stop is covered — a regional Asia plan may beat separate country plans.",
    ],
    net_intro="Indonesia's main mobile networks are Telkomsel, Indosat Ooredoo Hutchison (which includes 3) and XL. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> Telkomsel, with 4G/LTE and 5G.",
        "<strong>Airalo:</strong> 3 (Hutchison), plus Indosat and Telkomsel.",
        "<strong>Holafly:</strong> XL and Telkomsel, with 5G where available.",
    ],
    tips_title="Bali tips",
    tips=[
        "<strong>Coverage is strong in the main tourist areas</strong>, but can drop in the mountains, on smaller islands and at remote beaches. Download offline maps before day trips.",
        "<strong>Grab and Gojek need data</strong> for rides and food delivery, so check your eSIM works before you leave the airport.",
        "<strong>Villa and café WiFi is common but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-digital-nomads.html\">the best VPN for digital nomads</a>.",
        "<strong>Keep your home SIM active for bank texts</strong> with its data roaming turned off.",
    ],
    faq=[
        ("Does an eSIM work in Bali?",
         "Yes. Bali is part of Indonesia, so an Indonesia eSIM covers it. Saily says its Indonesia plan covers Jakarta, Bali and most Indonesian islands on Telkomsel's 4G and 5G networks."),
        ("What is the best eSIM for Bali?",
         "On 12 October 2026, Saily had the cheapest unlimited plans for 5 and 7 days ($26.99 for a week), while Airalo was 49 cents to $1 cheaper for 30-day fixed plans at list price. With my 10% code, Saily's 30-day plans were cheaper too."),
        ("How much is an eSIM for Bali?",
         "Prices started at $4.50 for 1 GB (Airalo, 3 days). A 10 GB plan cost $21–22 for 30 days, and unlimited data cost about $27 for a week."),
        ("Which network do Bali travel eSIMs use?",
         "Saily uses Telkomsel; Airalo lists 3 (Hutchison) plus Indosat and Telkomsel; Holafly lists XL and Telkomsel."),
        ("Do Bali eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp or other internet calling. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
    ],
    related_href="best-esim-for-thailand.html", related_tag="eSIM · Thailand", related_title="Best eSIM for Thailand (2026)",
)

PORTUGAL = dict(
    OCT12, slug="best-esim-for-portugal", name="Portugal", name_h1="Portugal",
    airalo_url="https://www.airalo.com/portugal-esim", holafly_url="https://esim.holafly.com/esim-portugal/",
    sticky_label="Portugal eSIM · from $3.99 →", sticky_sub="",
    headline="Best eSIM for Portugal (2026): Saily vs Airalo vs Holafly, Prices Compared",
    title="Best eSIM for Portugal 2026: Saily vs Airalo vs Holafly Prices Compared | TravelConnectly",
    desc="Portugal eSIM prices compared from each provider's site: Saily, Airalo and Holafly fixed-data and unlimited plans, networks (MEO, NOS, Vodafone), EU roaming and setup.",
    keywords="best eSIM for Portugal, Portugal eSIM, Saily Portugal, Airalo Portugal, Holafly Portugal, Portugal eSIM unlimited data, eSIM for Lisbon",
    og_title="Best eSIM for Portugal 2026: Saily vs Airalo vs Holafly",
    og_desc="Real Portugal eSIM prices compared, plus how much data you need and how to set it up.",
    og_image="og-esim-portugal.jpg",
    photo="photo-longterm.jpg", photo_alt="Two backpackers with large travel backpacks walking down a hostel corridor",
    qa_provider="Airalo",
    qa_label="Most trips",
    qa_reason="Cheapest on every 30-day plan — 10 GB is $11.00 vs $16.99 at Saily — and 50 GB for $35.",
    qa_plan="10 GB · 30 days", qa_price="$11.00", qa_cta="See Airalo's Portugal plans →",
    qa_trust=["NOS + MEO + Vodafone", "50 GB for $35", "7- and 15-day plans"],
    qa_chips=[("Unlimited week:", "Saily 7 days", 26.99, "Saily"), ("Light use, 30 days:", "Saily 3 GB", 7.99, "Saily")],
    takeaways=[
        "<strong>Airalo is much cheaper for fixed data in Portugal</strong> — 10 GB for 30 days is $11.00 vs $16.99 at Saily ($15.29 with my code).",
        "<strong>Unlimited for 5–7 days: Saily is a cent cheaper</strong> ($26.99 for a week); Airalo is cheaper from 10 days up at list price.",
        "<strong>All three name Portugal's main networks</strong> — MEO, NOS and Vodafone.",
        "<strong>Coming from the EU?</strong> Your home plan may already cover Portugal.",
    ],
    lede="Trams and trains in Lisbon and Porto, coastal drives in the Algarve and café work days — Portugal is easy with data. Here's what a Portugal eSIM actually costs, and for most trips the cheapest isn't the one I earn a commission from.",
    fixed=[
        ("1 GB", [(3.99, 7)], [(4.00, 3)]),
        ("3 GB", [(7.99, 30)], [(6.00, 3), (6.50, 7)]),
        ("5 GB", [(9.99, 30)], [(7.50, 7), (8.00, 15), (9.00, 30)]),
        ("10 GB", [(16.99, 30)], [(10.00, 7), (10.50, 15), (11.00, 30)]),
        ("20 GB", [(27.99, 30)], [(18.50, 15), (19.00, 30)]),
        ("50 GB", [], [(35.00, 30)]),
    ],
    fixed_note="<strong>What that means:</strong> Airalo is far cheaper for fixed data in Portugal — $5.99 less for 10 GB and $8.99 less for 20 GB over 30 days, and still cheaper even with my 10% Saily code. Saily's 3 GB plan is the only small plan that lasts 30 days.",
    unl=[(3, None, 11.50, 11.90), (5, 18.99, 19.00, 20.50), (7, 26.99, 27.00, 27.50),
         (10, 34.99, 34.50, 36.50), (15, 48.99, 48.00, 50.50), (30, 71.99, 69.00, 73.90)],
    unl_note="Saily was a cent cheaper for 5 and 7 days and also sells 20- and 25-day plans ($59.99 and $65.99); Airalo was cheapest for 3, 10, 15 and 30 days, by up to $3. With my code, Saily's unlimited is cheaper at every length it sells.",
    picks=[
        "<strong>Most travelers:</strong> Airalo — 5 GB ($9.00) or 10 GB ($11.00) for 30 days, far cheaper than Saily for fixed data. I don't earn a commission from Airalo.",
        f'<strong>Heavy use for a week:</strong> <a href="{SAILY}" target="_blank" rel="sponsored noopener">Saily unlimited</a> — a cent cheaper than Airalo, and $2.71 cheaper with my code.',
        "<strong>A month of heavy use:</strong> Airalo's 50 GB ($35.00).",
        "<strong>Portugal plus Spain or more of Europe:</strong> compare a Europe plan — see <a href=\"best-esim-for-europe.html\">the Europe eSIM guide</a>.",
    ],
    net_intro="Portugal's three main mobile networks are MEO, NOS and Vodafone. Travel eSIMs roam on one or more of them:",
    networks=[
        "<strong>Saily:</strong> MEO, Vodafone and NOS.",
        "<strong>Airalo:</strong> NOS, plus Vodafone and MEO.",
        "<strong>Holafly:</strong> MEO, NOS and Vodafone, with 5G where available.",
    ],
    tips_title="Portugal tips",
    tips=[
        "<strong>Coverage is strong in cities and along the coast</strong>; in the mountainous interior and on some rural roads it can thin out. Download offline maps before road trips.",
        "<strong>Save train tickets offline</strong> in case you lose signal in a station or tunnel.",
        "<strong>Café and coworking WiFi is everywhere but shared</strong> — use a VPN on it. See <a href=\"best-vpn-for-digital-nomads.html\">the best VPN for digital nomads</a>.",
        "<strong>Coming from another EU country?</strong> Your home plan may already include roaming in Portugal — check before you buy an eSIM.",
    ],
    faq=[
        ("What is the best eSIM for Portugal?",
         "On 12 October 2026, Airalo was the cheapest for fixed data — 10 GB for 30 days cost $11.00 against $16.99 at Saily — and for unlimited plans of 10 days or more. Saily was a cent cheaper for 5- and 7-day unlimited plans."),
        ("How much is an eSIM for Portugal?",
         "Prices started at $3.99 for 1 GB (Saily, 7 days). 10 GB cost $11.00 for 30 days at Airalo, and unlimited data cost about $27 for a week."),
        ("Which network do Portugal travel eSIMs use?",
         "All three name Portugal's main networks: Saily and Holafly list MEO, NOS and Vodafone, and Airalo lists NOS plus Vodafone and MEO."),
        EU_ROAMING_FAQ,
        ("Do Portugal eSIMs include a phone number?",
         "No. These are data-only eSIMs, so use WhatsApp, FaceTime or other internet calling. Keep your home SIM active for texts such as bank codes, with its data roaming turned off."),
    ],
    related_href="best-esim-for-spain.html", related_tag="eSIM · Spain", related_title="Best eSIM for Spain (2026)",
)

ALL_PAGES = (JAPAN, THAILAND, USA, TURKEY, CANADA, ITALY, SPAIN, UK, FRANCE, GREECE, MEXICO, CHINA, KOREA, BALI, PORTUGAL, EUROPE)

if __name__ == "__main__":
    for country in ALL_PAGES:
        page(country)
