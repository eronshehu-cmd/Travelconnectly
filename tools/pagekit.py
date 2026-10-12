"""Shared builder for new TravelConnectly pages (template: best-esim-for-travelers.html)."""
import json
import os
import re

os.chdir(os.environ.get("SITE_DIR", "."))
TODAY = os.environ.get("PAGE_DATE", "2026-09-28")
BASE = "https://www.travelconnectly.com/"
NORD = "https://go.nordvpn.net/aff_c?offer_id=725&aff_id=141128"
SURF = "https://get.surfshark.net/aff_c?offer_id=926&aff_id=44567"
SAILY = "https://go.saily.site/aff_c?offer_id=101&aff_id=16029&coupon=travelconnectly"

tpl = open("best-esim-for-travelers.html", encoding="utf-8").read()
# Start from untagged links so fix_site.py re-tags them with the new page's slug.
tpl = re.sub(r"&aff_sub=[^\"&]+&aff_sub2=[^\"&]+", "", tpl)
tpl = re.sub(r"/pubref:[^\"]+", "", tpl)


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, indent=2, ensure_ascii=False) + "\n</script>"


def build(slug, title, desc, keywords, og_title, og_desc, og_image, headline, faq, main, nav_cta, sticky, extra_css="", extra_js=""):
    url = BASE + slug + ".html"
    head = f"""<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="TravelConnectly">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="{BASE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}{og_image}">
<meta property="og:locale" content="en_US">

""" + ld({
        "@context": "https://schema.org", "@type": "Article", "headline": headline,
        "author": {"@type": "Person", "name": "Eron", "url": BASE + "about.html"},
        "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": url,
        "publisher": {"@type": "Organization", "name": "TravelConnectly",
                      "logo": {"@type": "ImageObject", "url": BASE + "icon-192.png"}},
        "image": BASE + og_image,
    }) + "\n" + ld({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq],
    }) + "\n\n"
    t = re.sub(r"<title>.*?(?=<link rel=\"preconnect\")", lambda m: head, tpl, count=1, flags=re.S)
    t = t.replace("</style>", extra_css + "</style>", 1)
    t = re.sub(r'<div class="nav-cta">.*?</div>', lambda m: f'<div class="nav-cta">\n      {nav_cta}\n    </div>', t, count=1, flags=re.S)
    t = re.sub(r'<main id="top">.*?</main>', lambda m: '<main id="top">\n' + main + "\n</main>", t, count=1, flags=re.S)
    t = re.sub(r'<div class="sticky-cta">.*?</div>', lambda m: sticky, t, count=1, flags=re.S)
    if extra_js:
        t = t.replace("</body>", extra_js + "\n</body>", 1)
    open(slug + ".html", "w", encoding="utf-8", newline="\r\n").write(t)
    print("wrote", slug + ".html")


def credbar(updated):
    return f"""    <div class="credbar">
      <div class="who">
        <span class="av">E</span>
        <div class="nm">
          <b>Eron</b>
          <span>Solo traveler &amp; founder</span>
        </div>
      </div>
      <div class="vline"></div>
      <span class="chk"><i>&#10003;</i>Figures sourced and dated</span>
      <div class="meta">
        <span class="upd">Last updated: {updated}</span>
        <a class="how" href="methodology.html">How I compare providers &rarr;</a>
      </div>
    </div>"""
