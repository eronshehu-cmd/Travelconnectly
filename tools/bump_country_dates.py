"""Keep the first four country guides' sitemap lastmod in step with their dateModified.

(Originally a one-off bump for the 9 Oct 2026 redesign; since 15 Nov 2026 the sitemap date comes from each page's own
dateModified, which esim_country_pages.py sets when prices are re-checked.)
"""
import os
import re
import sys

os.chdir(sys.argv[1])
SLUGS = ["japan", "thailand", "usa", "turkey"]

sm = open("sitemap.xml", encoding="utf-8").read()
for s in SLUGS:
    f = f"best-esim-for-{s}.html"
    modified = re.search(r'"dateModified": "(\d{4}-\d{2}-\d{2})"', open(f, encoding="utf-8").read()).group(1)
    loc = f"<loc>https://www.travelconnectly.com/{f}</loc>"
    i = sm.index(loc)
    j = sm.index("<lastmod>", i)
    k = sm.index("</lastmod>", j)
    sm = sm[:j] + f"<lastmod>{modified}" + sm[k:]
open("sitemap.xml", "w", encoding="utf-8", newline="\r\n").write(sm)
print("sitemap updated")
