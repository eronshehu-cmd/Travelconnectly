"""Site-wide sanity checks for TravelConnectly."""
import glob
import json
import os
import re
import sys

os.chdir(sys.argv[1])

u = open("best-esim-for-usa.html", encoding="utf-8").read()
print("usa takeaways:", "Key takeaways" in u, "| hawaii tip:", "Hawaii and Alaska:" in u,
      "| faq hawaii:", "Does a US eSIM work in Hawaii and Alaska?" in u)
print("usa dateModified:", re.findall(r'"dateModified": "([^"]+)"', u), "| upd:", re.findall(r"Last updated: ([^<]+)", u))
print("cross-links:", all("More country guides:" in open(f"best-esim-for-{s}.html", encoding="utf-8").read()
                          for s in ["japan", "thailand", "usa", "turkey"]))

bad = []
for f in sorted(glob.glob("*.html")):
    if f.startswith("google"):
        continue
    t = open(f, encoding="utf-8").read()
    if "guides.html#esim-countries" not in t:
        bad.append(f + ": no country nav")
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(s)
        except Exception:
            bad.append(f + ": bad JSON-LD")
    for h in set(re.findall(r'(?:href|src)="([^"#:]+\.(?:html|jpg|png|ico|txt))', t)):
        if not os.path.exists(h):
            bad.append(f + ": missing " + h)
    if re.search(r'aff_id=\d+"', t):
        bad.append(f + ": untagged affiliate link")
    b = open(f, "rb").read()
    if b.count(b"\n") != b.count(b"\r\n"):
        bad.append(f + ": mixed line endings")
    if t.count(".wrap.breadcrumb, .wrap.article-head") > 1:
        bad.append(f + ": duplicate gutter css")
print("ISSUES:", bad or "none")
