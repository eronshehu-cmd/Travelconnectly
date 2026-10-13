"""Link the Canada, Italy and Spain eSIM guides into the site, sitemap and llms.txt. Idempotent."""
import os
import re
import sys

os.chdir(sys.argv[1])
DATE = "2026-10-13"
GUIDE_COUNT = 31
ALL = [("japan", "Japan"), ("thailand", "Thailand"), ("usa", "USA"), ("turkey", "Turkey"),
       ("canada", "Canada"), ("italy", "Italy"), ("spain", "Spain"), ("uk", "UK"), ("france", "France"),
       ("greece", "Greece"), ("mexico", "Mexico"), ("china", "China"), ("south-korea", "South Korea"),
       ("bali", "Bali"), ("portugal", "Portugal"), ("dubai", "Dubai"), ("vietnam", "Vietnam"),
       ("australia", "Australia"), ("germany", "Germany"), ("philippines", "Philippines"),
       ("singapore", "Singapore"), ("malaysia", "Malaysia"), ("europe", "Europe")]
NEW = ALL[4:]
BLURBS = {
    "philippines": "Saily, Airalo and Holafly compared, plus coverage tips for island-hopping.",
    "singapore": "From a stopover to a longer stay: real, dated prices on Singtel and more.",
    "malaysia": "Saily, Airalo and Holafly Malaysia plans compared at real, dated prices.",
    "dubai": "UAE plans for Dubai and Abu Dhabi, plus what to know about calling apps.",
    "vietnam": "Saily, Airalo and Holafly Vietnam plans compared at real, dated prices.",
    "australia": "All three run on Optus — so here's who is cheapest, at real, dated prices.",
    "germany": "Saily, Airalo and Holafly Germany plans compared at real, dated prices.",
    "china": "Which eSIMs say Google and WhatsApp work, with real, dated prices.",
    "south-korea": "Saily, Airalo and Holafly Korea plans compared, plus the map apps that work.",
    "bali": "Indonesia plans that cover Bali, compared at real, dated prices.",
    "portugal": "Real, dated prices — and why the cheapest here isn't my affiliate partner.",
    "uk": "Saily, Airalo and Holafly UK plans compared, plus EU roaming after Brexit.",
    "france": "Saily, Airalo and Holafly France plans compared at real, dated prices.",
    "greece": "Real, dated prices, plus what to know about islands and ferries.",
    "mexico": "Real, dated prices — and why the cheapest here isn't my affiliate partner.",
    "europe": "Which countries each Europe plan really covers, with real, dated prices.",
    "canada": "Why unlimited often beats fixed data in Canada, with real, dated prices.",
    "italy": "Saily, Airalo and Holafly Italy plans compared at real, dated prices.",
    "spain": "Saily, Airalo and Holafly Spain plans compared at real, dated prices.",
}
LLMS = {
    "philippines": "Saily vs Airalo vs Holafly, networks (Smart, Globe), island coverage",
    "singapore": "Saily vs Airalo vs Holafly, network Singtel, stopover plans",
    "malaysia": "Saily vs Airalo vs Holafly, networks (Maxis, CelcomDigi), Borneo coverage",
    "dubai": "UAE plans: Saily vs Airalo vs Holafly, network du, WhatsApp/FaceTime calls restricted",
    "vietnam": "Saily vs Airalo vs Holafly, network VNPT/VinaPhone",
    "australia": "Saily vs Airalo vs Holafly, all on Optus; outback coverage",
    "germany": "Saily vs Airalo vs Holafly, networks (O2, Vodafone), EU roaming",
    "china": "Saily vs Airalo vs Holafly, which say Google/WhatsApp/Instagram work, VPN and setup",
    "south-korea": "Saily vs Airalo vs Holafly, networks (SK Telecom, LG U+), Naver Map/KakaoMap",
    "bali": "Indonesia plans covering Bali: Saily vs Airalo vs Holafly, Telkomsel/Indosat/XL",
    "portugal": "Saily vs Airalo vs Holafly, networks (MEO, NOS, Vodafone); Airalo cheapest for fixed data",
    "uk": "Saily vs Airalo vs Holafly, networks (EE and others), EU roaming after Brexit",
    "france": "Saily vs Airalo vs Holafly, networks (Orange, SFR, Bouygues, Free), EU roaming",
    "greece": "Saily vs Airalo vs Holafly, networks (Nova, Vodafone), islands and ferries",
    "mexico": "Saily vs Airalo vs Holafly, networks (Telcel, Movistar, AT&T); Airalo cheapest here",
    "europe": "regional plans compared: prices, which countries each covers (UK, Switzerland, Turkey, Balkans, Kosovo)",
    "canada": "Saily vs Airalo vs Holafly, networks (Bell, Telus), unlimited vs fixed data",
    "italy": "Saily vs Airalo vs Holafly, networks (WindTre, Vodafone), EU roaming",
    "spain": "Saily vs Airalo vs Holafly, networks (Orange, Movistar, Vodafone, Yoigo), EU roaming",
}


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, t, orig):
    if t != orig:
        open(p, "w", encoding="utf-8", newline="\r\n").write(t)
        print("updated", p)


def links(style=""):
    return " · ".join(f'<a href="best-esim-for-{s}.html"{style}>{n}</a>' for s, n in ALL)


def card(slug, name, blurb):
    return f"""        <a class="guide-card" href="best-esim-for-{slug}.html">
          <img src="og-esim-{slug}.jpg" alt="Best eSIM for {name} 2026: Saily vs Airalo vs Holafly" width="1200" height="630" loading="lazy">
          <div class="guide-card-body">
            <span class="tag">eSIM · {name}</span>
            <h3>Best eSIM for {name} (2026)</h3>
            <p>{blurb}</p>
          </div>
        </a>
"""


# guides.html: cards after Turkey (before the calculator card) and the "eSIM by country" line.
t = o = read("guides.html")
anchor = '        <a class="guide-card" href="esim-data-calculator.html">'
missing = [(s, n) for s, n in NEW if f'<a class="guide-card" href="best-esim-for-{s}.html">' not in t]
t = t.replace(anchor, "".join(card(s, n, BLURBS[s]) for s, n in missing) + anchor, 1)
t = re.sub(r'(<p id="esim-countries"[^>]*><strong>eSIM by country:</strong> ).*?(</p>)',
           lambda m: m.group(1) + links() + m.group(2), t, count=1)
write("guides.html", t, o)

# Homepage: guide count and country links.
t = o = read("index.html")
t = re.sub(r'<span class="n">\d+</span><span class="l">travel guides published</span>',
           f'<span class="n">{GUIDE_COUNT}</span><span class="l">travel guides published</span>', t)
style = ' style="color:var(--teal);text-decoration:underline;"'
t = re.sub(r'(<span class="link read-more" style="color:var\(--text-muted\);">Country guides: ).*?(</span>)',
           lambda m: m.group(1) + links(style) + m.group(2), t, count=1)
write("index.html", t, o)

# eSIM basics guide.
t = o = read("best-esim-for-travelers.html")
t = re.sub(r"(<p>Country guides with Saily, Airalo and Holafly plans compared at dated prices: ).*?(\.</p>)",
           lambda m: m.group(1) + links() + m.group(2), t, count=1)
write("best-esim-for-travelers.html", t, o)

# llms.txt
t = o = read("llms.txt")
for s, n in NEW:
    line = f"- [Best eSIM for {n}](https://www.travelconnectly.com/best-esim-for-{s}.html): {LLMS[s]}\n"
    if f"best-esim-for-{s}.html" not in t:
        t = t.replace("\n\n## eSIM basics and tools", "\n" + line.rstrip("\n") + "\n\n## eSIM basics and tools", 1)
write("llms.txt", t, o)

# Sitemap: new pages after Turkey; bump pages whose content changed today.
t = o = read("sitemap.xml")
entries = "".join(f"""  <url>
    <loc>https://www.travelconnectly.com/best-esim-for-{s}.html</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
""" for s, _ in NEW if f"best-esim-for-{s}.html" not in t)
loc = "<loc>https://www.travelconnectly.com/best-esim-for-turkey.html</loc>"
end = t.index("</url>", t.index(loc)) + len("</url>\n")
t = t[:end] + entries + t[end:]
for page in ["guides.html", "best-esim-for-travelers.html", ""] + [f"best-esim-for-{s}.html" for s, _ in ALL]:
    loc = f"<loc>https://www.travelconnectly.com/{page}</loc>"
    if loc not in t:
        print("not in sitemap:", page or "(home)")
        continue
    j = t.index("<lastmod>", t.index(loc))
    k = t.index("</lastmod>", j)
    t = t[:j] + f"<lastmod>{DATE}" + t[k:]
write("sitemap.xml", t, o)
print("sitemap urls:", t.count("<loc>"))
