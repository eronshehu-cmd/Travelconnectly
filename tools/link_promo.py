"""Link saily-promo-code.html into guides, homepage, eSIM basics guide, sitemap and llms.txt. Idempotent."""
import os
import sys

os.chdir(sys.argv[1])
DATE = "2026-11-04"
HREF = 'href="saily-promo-code.html"'


def edit(path, fn):
    t = open(path, encoding="utf-8").read()
    t2 = fn(t)
    if t2 != t:
        open(path, "w", encoding="utf-8", newline="\r\n").write(t2)
        print("updated", path)


CARD = """        <a class="guide-card" href="saily-promo-code.html">
          <img src="og-saily-promo-code.jpg" alt="Saily promo code: 10% off with TRAVELCONNECTLY" width="1200" height="630" loading="lazy">
          <div class="guide-card-body">
            <span class="tag">eSIM · Deal</span>
            <h3>Saily Promo Code: 10% Off</h3>
            <p>What TRAVELCONNECTLY takes off real plans, and what's confirmed.</p>
          </div>
        </a>
"""
anchor = '        <a class="guide-card" href="esim-data-calculator.html">'
edit("guides.html", lambda t: t if HREF in t else t.replace(anchor, CARD + anchor, 1))

edit("index.html", lambda t: t if HREF in t else t.replace(
    '<a href="saily-alternatives.html" class="link read-more">Saily alternatives →</a>',
    '<a href="saily-alternatives.html" class="link read-more">Saily alternatives →</a>\n'
    '            <a href="saily-promo-code.html" class="link read-more">Saily promo code →</a>', 1))

edit("best-esim-for-travelers.html", lambda t: t if HREF in t else t.replace(
    ', or see the <a href="saily-alternatives.html">best Saily alternatives</a>.',
    ', or see the <a href="saily-alternatives.html">best Saily alternatives</a> and my <a href="saily-promo-code.html">Saily promo code</a>.', 1))

edit("llms.txt", lambda t: t if "saily-promo-code.html" in t else t.replace(
    "\n\n## eSIM basics and tools",
    "\n- [Saily promo code](https://www.travelconnectly.com/saily-promo-code.html): TRAVELCONNECTLY, 10% off Saily plans, with real savings and what's confirmed\n\n## eSIM basics and tools", 1))


def sitemap(t):
    if "saily-promo-code.html" not in t:
        t = t.replace("</urlset>", f"""  <url>
    <loc>https://www.travelconnectly.com/saily-promo-code.html</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>""", 1)
    return t


edit("sitemap.xml", sitemap)
