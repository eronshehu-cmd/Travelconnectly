"""Rebuild every generated page and re-apply the site-wide fixes, in the right order.

Usage (from the repo root):  python tools/build_all.py
Then check the output ends with "ISSUES: none", preview locally, commit and push.
After the deploy is live:      python tools/indexnow.py
"""
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(TOOLS)

STEPS = [
    "esim_country_pages.py",  # country + Europe guides (prices live in this file)
    "saily_vs_airalo.py",     # comparison pages, built from the same data
    "saily_vs_holafly.py",
    "link_countries2.py",     # guides cards, homepage links, eSIM guide, sitemap, llms.txt
    "home_esim.py",           # homepage hero picker and "cheapest unlimited week" board
    "link_svsa.py",
    "link_svsh.py",
    "fix_site.py",            # affiliate tagging, Saily coupon, analytics, sticky buttons (all pages)
    "bump_country_dates.py",
    "validate.py",            # prints ISSUES: none when everything checks out
]

for step in STEPS:
    print(f"--- {step}")
    subprocess.run([sys.executable, os.path.join(TOOLS, step), SITE], check=True, cwd=TOOLS)
