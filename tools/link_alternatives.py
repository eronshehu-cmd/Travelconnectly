"""Link saily-alternatives.html into guides, homepage, eSIM basics guide, sitemap and llms.txt. Idempotent."""
import os
import sys

os.chdir(sys.argv[1])
DATE = "2026-10-12"
HREF = 'href="saily-alternatives.html"'


def edit(path, fn):
    t = open(path, encoding="utf-8").read()
    t2 = fn(t)
    if t2 != t:
        open(path, "w", encoding="utf-8", newline="\r\n").write(t2)
        print("updated", path)


CARD = """        <a class="guide-card" href="saily-alternatives.html">
          <img src="og-saily-alternatives.jpg" alt="Saily alternatives 2026: Airalo and Holafly compared in 20 destinations" width="1200" height="630" loading="lazy">
          <div class="guide-card-body">
            <span class="tag">eSIM · Comparison</span>
            <h3>Saily Alternatives (2026)</h3>
            <p>When Airalo or Holafly beats Saily, destination by destination.</p>
          </div>
        </a>
"""
anchor = '        <a class="guide-card" href="esim-data-calculator.html">'
edit("guides.html", lambda t: t if HREF in t else t.replace(anchor, CARD + anchor, 1))

edit("index.html", lambda t: t if HREF in t else t.replace(
    '<a href="saily-vs-holafly.html" class="link read-more">Saily vs Holafly →</a>',
    '<a href="saily-vs-holafly.html" class="link read-more">Saily vs Holafly →</a>\n'
    '            <a href="saily-alternatives.html" class="link read-more">Saily alternatives →</a>', 1))

edit("best-esim-for-travelers.html", lambda t: t if HREF in t else t.replace(
    '<a href="saily-vs-holafly.html">Saily vs Holafly</a>.',
    '<a href="saily-vs-holafly.html">Saily vs Holafly</a>, or see the <a href="saily-alternatives.html">best Saily alternatives</a>.', 1))

edit("llms.txt", lambda t: t if "saily-alternatives.html" in t else t.replace(
    "\n\n## eSIM basics and tools",
    "\n- [Saily alternatives](https://www.travelconnectly.com/saily-alternatives.html): when Airalo or Holafly beats Saily, 20 destinations\n\n## eSIM basics and tools", 1))


def sitemap(t):
    if "saily-alternatives.html" not in t:
        t = t.replace("</urlset>", f"""  <url>
    <loc>https://www.travelconnectly.com/saily-alternatives.html</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>""", 1)
    return t


edit("sitemap.xml", sitemap)
