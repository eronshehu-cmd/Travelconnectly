"""Link saily-vs-airalo.html into guides, homepage, eSIM basics guide, sitemap and llms.txt. Idempotent."""
import os
import re
import sys

os.chdir(sys.argv[1])
DATE = "2026-10-10"
HREF = 'href="saily-vs-airalo.html"'


def edit(path, fn):
    t = open(path, encoding="utf-8").read()
    t2 = fn(t)
    if t2 != t:
        open(path, "w", encoding="utf-8", newline="\r\n").write(t2)
        print("updated", path)


CARD = """        <a class="guide-card" href="saily-vs-airalo.html">
          <img src="og-saily-vs-airalo.jpg" alt="Saily vs Airalo 2026: prices compared in 20 destinations" width="1200" height="630" loading="lazy">
          <div class="guide-card-body">
            <span class="tag">eSIM · Comparison</span>
            <h3>Saily vs Airalo (2026)</h3>
            <p>Who is cheaper for unlimited and for fixed data, destination by destination.</p>
          </div>
        </a>
"""
anchor = '        <a class="guide-card" href="esim-data-calculator.html">'
edit("guides.html", lambda t: t if HREF in t else t.replace(anchor, CARD + anchor, 1))

# Guide count and the eSIM spotlight links on the homepage.
edit("index.html", lambda t: re.sub(r'<span class="n">\d+</span><span class="l">travel guides published</span>',
                                    '<span class="n">31</span><span class="l">travel guides published</span>', t))
edit("index.html", lambda t: t if HREF in t else t.replace(
    '<a href="esim-data-calculator.html" class="link read-more">How much data do I need? →</a>\n            <span',
    '<a href="esim-data-calculator.html" class="link read-more">How much data do I need? →</a>\n'
    '            <a href="saily-vs-airalo.html" class="link read-more">Saily vs Airalo →</a>\n            <span', 1))

edit("best-esim-for-travelers.html", lambda t: t if HREF in t else re.sub(
    r"(<p>Country guides with Saily, Airalo and Holafly plans compared at dated prices: .*?\.)(</p>)",
    lambda m: m.group(1) + ' Or compare providers head to head: <a href="saily-vs-airalo.html">Saily vs Airalo</a>.' + m.group(2),
    t, count=1))

edit("llms.txt", lambda t: t if "saily-vs-airalo.html" in t else t.replace(
    "\n\n## eSIM basics and tools",
    "\n- [Saily vs Airalo](https://www.travelconnectly.com/saily-vs-airalo.html): head-to-head prices in 20 destinations, unlimited vs fixed data\n\n## eSIM basics and tools", 1))


def sitemap(t):
    if "saily-vs-airalo.html" in t:
        return t
    entry = f"""  <url>
    <loc>https://www.travelconnectly.com/saily-vs-airalo.html</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
"""
    t = t.replace("</urlset>", entry + "</urlset>", 1)
    for page in ["", "guides.html", "best-esim-for-travelers.html"]:
        loc = f"<loc>https://www.travelconnectly.com/{page}</loc>"
        j = t.index("<lastmod>", t.index(loc))
        t = t[:j] + f"<lastmod>{DATE}" + t[t.index("</lastmod>", j):]
    return t


edit("sitemap.xml", sitemap)
