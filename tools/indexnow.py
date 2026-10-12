"""Notify IndexNow (Bing, Yandex, ...) about TravelConnectly URLs.

Usage: python indexnow.py            -> submits every URL in the live sitemap
       python indexnow.py url1 url2  -> submits only those URLs
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request

HOST = "www.travelconnectly.com"
KEY = "7f5ffa04c5154c5d060def6c36ec5ebb"
KEY_URL = f"https://{HOST}/{KEY}.txt"
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")


for _ in range(12):
    try:
        if fetch(KEY_URL).strip() == KEY:
            break
    except urllib.error.URLError:
        pass
    time.sleep(15)
else:
    raise SystemExit("key file not live yet: " + KEY_URL)

urls = sys.argv[1:] or re.findall(r"<loc>([^<]+)</loc>", fetch(f"https://{HOST}/sitemap.xml"))
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": KEY_URL, "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, f"({len(urls)} URLs submitted)")
except urllib.error.HTTPError as e:
    print("IndexNow error:", e.code, e.read().decode("utf-8", "replace")[:300])
