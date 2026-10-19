"""Homepage: eSIM-first hero (destination picker + cheapest unlimited week board). Idempotent.

Prices come from the published country guides (checked 29 Sep 2026 for Japan/Thailand/USA/Turkey,
9 Oct 2026 for Canada/Italy/Spain/Europe).
"""
import os
import re
import sys

os.chdir(sys.argv[1])
SAILY = "https://go.saily.site/aff_c?offer_id=101&aff_id=16029&coupon=travelconnectly&aff_sub=index&aff_sub2=board"

# slug, name, starting price (cheapest plan of any kind), cheapest 7-day unlimited (price, provider)
DEST = [
    ("europe", "Europe", "from $4.99", 26.99, "Saily"),
    ("usa", "USA", "from $3.49", 24.99, "Saily"),
    ("japan", "Japan", "from $3.99", 26.50, "Airalo"),
    ("thailand", "Thailand", "from $2.99", 20.99, "Saily"),
    ("italy", "Italy", "from $3.99", 22.99, "Saily"),
    ("spain", "Spain", "from $3.99", 22.99, "Saily"),
    ("turkey", "Turkey", "from $3.99", 24.50, "Airalo"),
    ("canada", "Canada", "from $5.29", 28.99, "Saily"),
    ("uk", "UK", "from $4.00", 26.99, "Saily"),
    ("france", "France", "from $3.99", 23.50, "Airalo"),
    ("greece", "Greece", "from $4.00", 26.99, "Saily"),
    ("mexico", "Mexico", "from $4.00", 23.50, "Airalo"),
    ("china", "China", "from $4.00", 27.00, "Airalo"),
    ("south-korea", "South Korea", "from $3.99", 26.99, "Saily"),
    ("bali", "Bali", "from $4.50", 26.99, "Saily"),
    ("portugal", "Portugal", "from $3.99", 26.99, "Saily"),
    ("dubai", "Dubai", "from $4.00", 27.50, "Airalo"),
    ("vietnam", "Vietnam", "from $3.99", 26.99, "Saily"),
    ("australia", "Australia", "from $3.99", 26.50, "Airalo"),
    ("germany", "Germany", "from $4.00", 23.99, "Saily"),
    ("philippines", "Philippines", "from $3.99", 26.99, "Saily"),
    ("singapore", "Singapore", "from $3.99", 26.99, "Saily"),
    ("malaysia", "Malaysia", "from $3.99", 26.99, "Saily"),
    ("asia", "Asia", "from $4.00", 26.00, "Airalo"),
]

CSS = """
/* ---- eSIM-first hero ---- */
.dest-label{ font-family:'IBM Plex Mono',monospace; font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--amber); margin:0 0 10px; }
.dest-grid{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin-bottom:18px; }
.dest-grid a{ display:flex; flex-direction:column; justify-content:center; gap:2px; min-height:58px; padding:10px 12px; background:var(--navy-panel); border:1px solid #2A4563; border-radius:12px; color:var(--text-light); text-decoration:none; transition:border-color .15s; }
.dest-grid a:hover{ border-color:var(--teal); }
.dest-grid b{ font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:600; }
.dest-grid span{ font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:var(--teal); }
.hero-links{ display:flex; flex-wrap:wrap; gap:8px 22px; margin-bottom:30px; }
.hero-links a{ min-height:44px; display:inline-flex; align-items:center; }
.esim-board .board-cols, .esim-board .board-row{ grid-template-columns:1.3fr 0.9fr 0.9fr; }
.esim-board a.board-row{ color:var(--text-light); text-decoration:none; }
.esim-board a.board-row:hover{ background:rgba(63,217,199,.06); }
.esim-board .board-row b{ font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:0.95rem; }
.esim-board .price{ color:var(--teal); font-weight:600; }
.esim-board .p-saily{ color:var(--saily-purple-text); }
.esim-board .p-other{ color:var(--text-muted); }
.esim-board .board-coupon{ margin:10px 0 0; text-align:center; font-size:0.82rem; color:var(--amber); }
.esim-board .board-coupon b{ font-family:'IBM Plex Mono',monospace; letter-spacing:0.04em; }
.esim-board .board-note{ margin:12px 0 0; font-size:0.76rem; line-height:1.5; color:var(--text-muted); }
@media (max-width:560px){
  .dest-grid{ grid-template-columns:repeat(2,minmax(0,1fr)); }
  .hero{ padding-top:28px; }
  .hero h1{ font-size:1.95rem; margin:12px 0 14px; }
  .hero p.lead{ font-size:0.98rem; margin-bottom:20px; }
}
"""


def hero():
    chips = "\n".join(
        f'          <a href="best-esim-for-{s}.html"><b>{n}</b><span>{sub}</span></a>' for s, n, sub, _, _ in DEST)
    rows = "\n".join(
        f'        <a class="board-row" href="best-esim-for-{s}.html"><b>{n}</b><span class="price">${p:.2f}</span>'
        f'<span class="{"p-saily" if prov == "Saily" else "p-other"}">{prov}</span></a>' for s, n, _, p, prov in DEST)
    return f"""  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <div class="eyebrow">eSIM &amp; VPN GUIDES FOR TRAVELERS</div>
        <h1>Stay connected abroad<br>without <span>overpaying</span>.</h1>
        <p class="lead">Real eSIM prices for your destination, checked on each provider's own site and dated — plus the VPN that keeps hotel and airport WiFi safe.</p>
        <div class="dest-label" id="dest-l">Where are you going?</div>
        <div class="dest-grid" role="group" aria-labelledby="dest-l">
{chips}
        </div>
        <div class="hero-links">
          <a href="esim-data-calculator.html" class="link read-more">How much data do I need? →</a>
          <a href="#reviews" class="link read-more">Need a VPN? NordVPN vs Surfshark ↓</a>
        </div>
        <div class="stat-strip">
          <div><span class="n">{len(DEST)}</span><span class="l">destinations with dated eSIM prices</span></div>
          <div><span class="n">31</span><span class="l">travel guides published</span></div>
          <div><span class="n sm">Oct 2026</span><span class="l">eSIM prices last checked</span></div>
          <div><span class="n">0</span><span class="l">sponsored placements — rankings are never paid for</span></div>
        </div>
      </div>

      <div class="board esim-board">
        <div class="board-head">
          <div class="mono">Cheapest unlimited week</div>
          <div class="board-status"><span class="dot"></span> CHECKED SEP–OCT 2026</div>
        </div>
        <div class="board-cols"><span>Destination</span><span>7 days</span><span>Provider</span></div>
{rows}
        <div class="board-foot">
          <a href="{SAILY}" target="_blank" rel="sponsored noopener" class="btn btn-saily">See Saily's eSIM plans</a>
        </div>
        <p class="board-coupon">10% off with code <b>TRAVELCONNECTLY</b> · applied automatically</p>
        <p class="board-note">Cheapest 7-day unlimited plan among Saily, Airalo and Holafly in each guide, at list prices before any discount (Europe and Asia: regional plans). Cheaper still: Maya Mobile's global plan, $19.99 for 7 days in any country. I earn a commission from Saily and Maya, not from Airalo.</p>
      </div>
    </div>
  </section>"""


t = open("index.html", encoding="utf-8").read()
orig = t
t = re.sub(r'  <section class="hero">.*?</section>', lambda m: hero(), t, count=1, flags=re.S)
if "/* ---- eSIM-first hero ---- */" not in t:
    t = t.replace("</style>", CSS + "</style>", 1)
elif ".esim-board .board-coupon" not in t:
    # Hero CSS from an earlier run is already there; add only the coupon styles.
    t = t.replace("</style>", "\n".join(l for l in CSS.splitlines() if "board-coupon" in l) + "\n</style>", 1)

TITLE = "Best eSIM &amp; VPN for Travelers 2026: Real Prices Compared | TravelConnectly"
DESC = ("Real, dated eSIM prices for Europe, the USA, Japan, Thailand and more — Saily vs Airalo vs Holafly — "
        "plus NordVPN vs Surfshark for safe hotel and airport WiFi.")
t = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", t, count=1)
t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', t, count=1)
t = re.sub(r'<meta property="og:title" content="[^"]*">',
           '<meta property="og:title" content="Best eSIM &amp; VPN for Travelers 2026: Real Prices Compared">', t, count=1)
t = re.sub(r'<meta property="og:description" content="[^"]*">',
           '<meta property="og:description" content="Real, dated eSIM prices by destination, plus the VPN that keeps hotel WiFi safe.">', t, count=1)
t = t.replace('"headline": "Best VPN for Travelers 2026: NordVPN vs Surfshark Compared"',
              '"headline": "Best eSIM & VPN for Travelers 2026: Real Prices Compared"')
t = re.sub(r'"dateModified": "[^"]+"', '"dateModified": "2026-10-10"', t, count=1)

if t != orig:
    open("index.html", "w", encoding="utf-8", newline="\r\n").write(t)
    print("updated index.html")
