# vps-deals

An English-language VPS source radar. It tracks public, official provider pages and sends readers to the original source to verify live pricing and terms. The site does not invent discounts or prices.

## Defaults used

- Niche: VPS hosting
- Brand: `vps-deals`
- Locale: `en-US`
- Seeds: Hostinger VPS, Akamai Linode credit page, DigitalOcean Droplet pricing
- Intended Cloudflare Pages project: `vps-deals-promo-radar`

The intended URL, `https://vps-deals-promo-radar.pages.dev`, is **not verified or deployed**. Change `domain` in `.ilang/site.ilang` to the actual Pages hostname before publishing, then run `python build.py` again.

## Build locally

Python 3.12 or newer, standard library only:

```sh
python scraper.py
python build.py
```

The scraper checks robots.txt and reads only public HTML. If a source cannot be accessed, it preserves the last successfully checked entry with its original timestamp. If no source has ever been checked, the site shows an honest empty state. Data is in `data/offers.json`; generated pages are in `site/`.

To test that I-Lang configuration is active, change a provider or source in `.ilang/site.ilang` and rerun both scripts. The resulting listing changes or disappears if the new source cannot be verified.

## GitHub and Cloudflare Pages

Create a public repository named `vps-deals-promo-radar` and push these files. The GitHub Actions workflow runs every six hours and on manual dispatch. It commits verified data and generated HTML only when content changes. Scheduled workflows may be delayed or disabled after long repository inactivity; check the Actions tab periodically.

Connect the repository in Cloudflare Pages. Set the build command to `python build.py` and the output directory to `site`. Update the domain in `.ilang/site.ilang` to the assigned Pages hostname and push again. Once online, check the home page, a detail page, `/sitemap.xml`, `/robots.txt`, and canonical links.

## Revenue rules

The fourth field in each provider line of `.ilang/site.ilang` accepts an approved affiliate link. Leave it empty until the provider approves the account. Disclose affiliate relationships on the site when such links are added, and follow the applicable program terms. No commission rates are claimed here. An eventual sale of the site requires a real income history and buyer due diligence; no valuation is promised.

Site rules use the I-Lang protocol: see `.ilang/site.ilang`; protocol information: ilang.ai.
