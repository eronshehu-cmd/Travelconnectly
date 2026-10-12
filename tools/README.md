# TravelConnectly build tools

Scripts that generate the eSIM guides and keep links consistent across the site.
`.vercelignore` keeps this folder off the live site.

## Everyday use

```
python tools/build_all.py        # rebuild generated pages + site-wide fixes; must end with "ISSUES: none"
python tools/indexnow.py         # after the deploy is live: notify Bing/Yandex of every sitemap URL
python tools/indexnow.py URL ... # or only specific URLs
```

## Where things live

| What | File |
|---|---|
| Country and Europe guide data (prices, networks, FAQ, picks) | `esim_country_pages.py` — one dict per destination, `ALL_PAGES` at the bottom |
| Page template, affiliate base links (Saily link carries `coupon=travelconnectly`) | `pagekit.py` |
| Saily vs Airalo / Saily vs Holafly (built from the same data; counts asserted) | `saily_vs_airalo.py`, `saily_vs_holafly.py` |
| Homepage destination picker and board | `home_esim.py` (`DEST`) |
| Links into guides, homepage, sitemap, llms.txt | `link_countries2.py`, `link_svsa.py`, `link_svsh.py` |
| Affiliate tagging (`aff_sub` = page, `aff_sub2` = position), Saily coupon on every Saily link | `fix_site.py` |
| Sanity checks | `validate.py` |
| Social share images | `python tools/og_image.py out.jpg photo.jpg "EYEBROW" "line 1" "line 2" "sub"` |

## Refreshing prices

1. Check prices in USD on each provider's own page: saily.com (currency USD, **clear any coupon cookie**
   so you see list prices), airalo.com/...-esim?currency=USD (Unlimited and Fixed data tabs),
   esim.holafly.com (USD price table; spot-check a length live).
2. Update the destination's dict in `esim_country_pages.py` (prices, `checked`, `checked_long`, `date`)
   and any text that quotes a price.
3. Run `build_all.py`. If a comparison assert fails, the winner counts changed: update the numbers and
   the sentences that mention them in `saily_vs_airalo.py` / `saily_vs_holafly.py`.
4. Preview locally (`python -m http.server 8765`), commit, push, check the live pages, run `indexnow.py`.

Vercel can take ~5 minutes to start a deploy after a push.
