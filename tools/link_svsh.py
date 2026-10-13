"""Link saily-vs-holafly.html into guides, homepage, eSIM basics guide, sitemap and llms.txt. Idempotent."""
import os
import re
import sys

os.chdir(sys.argv[1])
DATE = "2026-10-10"
HREF = 'href="saily-vs-holafly.html"'
GUIDE_COUNT = 31


def edit(path, fn):
    t = open(path, encoding="utf-8").read()
    t2 = fn(t)
    if t2 != t:
        open(path, "w", encoding="utf-8", newline="\r\n").write(t2)
        print("updated", path)


CARD = """        <a class="guide-card" href="saily-vs-holafly.html">
          <img src="og-saily-vs-holafly.jpg" alt="Saily vs Holafly 2026: unlimited eSIM prices in 23 destinations" width="1200" height="630" loading="lazy">
          <div class="guide-card-body">
            <span class="tag">eSIM · Comparison</span>
            <h3>Saily vs Holafly (2026)</h3>
            <p>Which unlimited eSIM is cheaper, destination by destination.</p>
          </div>
        </a>
"""
anchor = '        <a class="guide-card" href="esim-data-calculator.html">'
edit("guides.html", lambda t: t if HREF in t else t.replace(anchor, CARD + anchor, 1))

edit("index.html", lambda t: re.sub(r'<span class="n">\d+</span><span class="l">travel guides published</span>',
                                    f'<span class="n">{GUIDE_COUNT}</span><span class="l">travel guides published</span>', t))
edit("index.html", lambda t: t if HREF in t else t.replace(
    '<a href="saily-vs-airalo.html" class="link read-more">Saily vs Airalo →</a>',
    '<a href="saily-vs-airalo.html" class="link read-more">Saily vs Airalo →</a>\n'
    '            <a href="saily-vs-holafly.html" class="link read-more">Saily vs Holafly →</a>', 1))

edit("best-esim-for-travelers.html", lambda t: t if HREF in t else t.replace(
    '<a href="saily-vs-airalo.html">Saily vs Airalo</a>.',
    '<a href="saily-vs-airalo.html">Saily vs Airalo</a> and <a href="saily-vs-holafly.html">Saily vs Holafly</a>.', 1))

edit("llms.txt", lambda t: t if "saily-vs-holafly.html" in t else t.replace(
    "\n\n## eSIM basics and tools",
    "\n- [Saily vs Holafly](https://www.travelconnectly.com/saily-vs-holafly.html): unlimited-data prices in 23 destinations, speed limits, hotspot\n\n## eSIM basics and tools", 1))


def sitemap(t):
    if "saily-vs-holafly.html" not in t:
        t = t.replace("</urlset>", f"""  <url>
    <loc>https://www.travelconnectly.com/saily-vs-holafly.html</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>""", 1)
    return t


edit("sitemap.xml", sitemap)
