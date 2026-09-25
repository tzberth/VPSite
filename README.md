# vps-deals

An English-language VPS source radar. It tracks public, official provider pages and sends readers to the original source to verify live pricing and terms. The site does not invent discounts or prices.

## Defaults used

- Niche: VPS hosting
- Brand: `vps-deals`
- Locale: `en-US`
- Seeds: IONOS and VPS.NET promotion pages; OVHcloud US VPS pricing
- Cloudflare Pages project: `vps-deals-promo-radar`

Production hostname: `https://vpsdealscout.com`. The hostname is configured in `.ilang/site.ilang` so canonical links, Open Graph images, and the sitemap use the same address.

## Build locally

Python 3.12 or newer, standard library only:

```sh
python scraper.py
python build.py
python verify.py
```

The scraper checks robots.txt and reads only public HTML. If a source cannot be accessed, it preserves the last successfully checked entry with its original timestamp. If no source has ever been checked, the site shows an honest empty state. Data is in `data/offers.json`; generated pages are in `site/`.

To test that I-Lang configuration is active, change a provider or source in `.ilang/site.ilang` and rerun both scripts. The resulting listing changes or disappears if the new source cannot be verified.

## GitHub and Cloudflare Pages

The public repository is `https://github.com/tzberth/VPSite`. The GitHub Actions workflow runs every six hours and on manual dispatch. It commits verified data and generated HTML only when content changes. Scheduled workflows may be delayed or disabled after long repository inactivity; check the Actions tab periodically.

Cloudflare Pages is connected to this repository with build command `python build.py` and output directory `site`. If the Pages hostname changes, update `domain` in `.ilang/site.ilang` and push again. Check the home page, a detail page, `/sitemap.xml`, `/robots.txt`, and canonical links after each domain change.

## Revenue rules

The fourth field in each provider line of `.ilang/site.ilang` accepts an approved affiliate link. Leave it empty until the provider approves the account. Disclose affiliate relationships on the site when such links are added, and follow the applicable program terms. No commission rates are claimed here. An eventual sale of the site requires a real income history and buyer due diligence; no valuation is promised.

Site rules use the I-Lang protocol: see `.ilang/site.ilang`; protocol information: ilang.ai.
