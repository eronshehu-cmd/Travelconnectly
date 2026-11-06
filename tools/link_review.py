"""Link saily-review.html into guides, homepage, eSIM basics guide, sitemap and llms.txt. Idempotent."""
import os
import sys

os.chdir(sys.argv[1])
DATE = "2026-11-06"
HREF = 'href="saily-review.html"'


def edit(path, fn):
    t = open(path, encoding="utf-8").read()
    t2 = fn(t)
    if t2 != t:
        open(path, "w", encoding="utf-8", newline="\r\n").write(t2)
        print("updated", path)


CARD = """        <a class="guide-card" href="saily-review.html">
          <img src="og-saily-review.jpg" alt="Saily eSIM review 2026: prices, pros and cons" width="1200" height="630" loading="lazy">
          <div class="guide-card-body">
            <span class="tag">eSIM · Review</span>
            <h3>Saily eSIM Review (2026)</h3>
            <p>How Saily's prices compare in 23 destinations, and who it suits.</p>
          </div>
        </a>
"""
anchor = '        <a class="guide-card" href="esim-data-calculator.html">'
edit("guides.html", lambda t: t if HREF in t else t.replace(anchor, CARD + anchor, 1))

edit("index.html", lambda t: t if HREF in t else t.replace(
    '<a href="saily-promo-code.html" class="link read-more">Saily promo code →</a>',
    '<a href="saily-promo-code.html" class="link read-more">Saily promo code →</a>\n'
    '            <a href="saily-review.html" class="link read-more">Saily review →</a>', 1))

edit("best-esim-for-travelers.html", lambda t: t if HREF in t else t.replace(
    'my <a href="saily-promo-code.html">Saily promo code</a>.',
    'my <a href="saily-promo-code.html">Saily promo code</a>. New to Saily? Read my <a href="saily-review.html">Saily review</a>.', 1))

edit("llms.txt", lambda t: t if "saily-review.html" in t else t.replace(
    "\n\n## eSIM basics and tools",
    "\n- [Saily review](https://www.travelconnectly.com/saily-review.html): Saily eSIM prices vs Airalo and Holafly in 23 destinations, limits, pros and cons\n\n## eSIM basics and tools", 1))


def sitemap(t):
    if "saily-review.html" not in t:
        t = t.replace("</urlset>", f"""  <url>
    <loc>https://www.travelconnectly.com/saily-review.html</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>""", 1)
    return t


edit("sitemap.xml", sitemap)
