"""Country guides got the answer-first redesign today: bump dateModified and sitemap lastmod."""
import os
import sys

os.chdir(sys.argv[1])
TODAY = "2026-10-09"
SLUGS = ["japan", "thailand", "usa", "turkey"]

for s in SLUGS:
    f = f"best-esim-for-{s}.html"
    t = open(f, encoding="utf-8").read()
    t2 = t.replace('"dateModified": "2026-09-29"', f'"dateModified": "{TODAY}"')
    if t2 != t:
        open(f, "w", encoding="utf-8", newline="\r\n").write(t2)
        print("dateModified", f)

sm = open("sitemap.xml", encoding="utf-8").read()
for s in SLUGS:
    loc = f"<loc>https://www.travelconnectly.com/best-esim-for-{s}.html</loc>"
    i = sm.index(loc)
    j = sm.index("<lastmod>", i)
    k = sm.index("</lastmod>", j)
    sm = sm[:j] + f"<lastmod>{TODAY}" + sm[k:]
open("sitemap.xml", "w", encoding="utf-8", newline="\r\n").write(sm)
print("sitemap updated")
