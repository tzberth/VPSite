# ::ILANG [TYPE:module][ROLE:render-static-pages]
# ::RULE{Read brand domain and providers from .ilang/site.ilang}
# ::BOUNDARY{never:render unverified price or fabricated expiry|scope:permanent}
import html
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from config import load_config

ROOT = Path(__file__).parent
OUT = ROOT / 'site'
TEMPLATES = ROOT / 'templates'


def esc(value):
    return html.escape(str(value or ''), quote=True)


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def render(template, **values):
    content = (TEMPLATES / template).read_text(encoding='utf-8')
    for key, value in values.items():
        content = content.replace('{{' + key + '}}', str(value))
    return content


def write(relative, content):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def jsonld(value):
    return '<script type="application/ld+json">' + json.dumps(value, ensure_ascii=False).replace('<', '\\u003c') + '</script>'


def layout(site, path, title, description, body, schema):
    url = f"https://{site['domain']}{path}"
    return render('base.html', lang=esc(site.get('locale', 'en-US')), brand=esc(site['brand']),
                  title=esc(title), description=esc(description), canonical=esc(url),
                  og_image=esc(f"https://{site['domain']}/og.svg"), body=body, schema=jsonld(schema), year=datetime.now().year)


def card(item):
    page = f"/deals/{slug(item['provider'])}/"
    return render('card.html', provider=esc(item['provider']), title=esc(item['title']), kind=esc(item['kind'].upper() + ' SOURCE'),
                  description=esc(item.get('description') or 'Explore the current terms at the official source.'),
                  page=page, checked=esc(item['fetched_at'][:10]))


def main():
    site, providers = load_config()
    provider_map = {p['name']: p for p in providers}
    data_path = ROOT / 'data' / 'offers.json'
    records = json.loads(data_path.read_text(encoding='utf-8')) if data_path.exists() else []
    records = [r for r in records if r.get('provider') in provider_map and r.get('source_url') == provider_map[r['provider']]['source']]
    records = [r for r in records if not r.get('valid_until') or r['valid_until'] >= datetime.now().date().isoformat()]
    OUT.mkdir(exist_ok=True)
    cards = ''.join(card(r) for r in records) or '<p class="empty">No verified sources are available yet. Check back after the next update.</p>'
    list_items = [{'@type': 'ListItem', 'position': i, 'url': f"https://{site['domain']}/deals/{slug(r['provider'])}/"} for i, r in enumerate(records, 1)]
    pages = []

    def add(path, title, description, body, schema, lastmod=None):
        write(path.lstrip('/') + 'index.html' if path != '/' else 'index.html', layout(site, path, title, description, body, schema))
        pages.append((path, lastmod))

    add('/', f"VPS offers and official plans | {site['brand']}",
        'Verified official VPS offer and plan pages, with source links and last checked dates.',
        render('index.html', cards=cards, count=len(records)),
        {'@context': 'https://schema.org', '@type': 'ItemList', 'itemListElement': list_items},
        max((r['fetched_at'][:10] for r in records), default=None))
    add('/compare/', f"Compare VPS sources | {site['brand']}",
        'Compare official VPS offer and pricing sources. Check live terms with each provider.',
        render('compare.html', rows=''.join(render('row.html', provider=esc(r['provider']), title=esc(r['title']),
                                           page=f"/deals/{slug(r['provider'])}/", source=esc(r['source_url']),
                                           checked=esc(r['fetched_at'][:10])) for r in records)),
        {'@context': 'https://schema.org', '@type': 'ItemList', 'itemListElement': list_items})
    for r in records:
        provider = provider_map[r['provider']]
        provider_path = f"/providers/{slug(r['provider'])}/"
        detail_path = f"/deals/{slug(r['provider'])}/"
        breadcrumb = {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f"https://{site['domain']}/"},
            {'@type': 'ListItem', 'position': 2, 'name': r['provider'], 'item': f"https://{site['domain']}{provider_path}"}]}
        add(provider_path, f"{r['provider']} VPS source | {site['brand']}",
            f"Official {r['provider']} VPS source, last checked {r['fetched_at'][:10]}.",
            render('provider.html', provider=esc(r['provider']), title=esc(r['title']), detail=detail_path, kind=esc(r['kind'].upper() + ' SOURCE'),
                   website=esc(provider['website']), checked=esc(r['fetched_at'][:10])),
            {'@context': 'https://schema.org', '@graph': [
                {'@type': 'Service', 'name': f"{r['provider']} VPS hosting", 'provider': {'@type': 'Organization', 'name': r['provider']},
                 'url': f"https://{site['domain']}{provider_path}"}, breadcrumb]}, r['fetched_at'][:10])
        service = {'@type': 'Service', 'name': r['title'], 'provider': {'@type': 'Organization', 'name': r['provider']}, 'url': r['source_url']}
        if 'price' in r and 'currency' in r:
            offer = {'@type': 'Offer', 'url': r['offer_url'], 'price': r['price'], 'priceCurrency': r['currency']}
            if r.get('valid_until'):
                offer['priceValidUntil'] = r['valid_until']
            service['offers'] = offer
        add(detail_path, f"{r['provider']}: {r['title']} | {site['brand']}",
            f"Official {r['provider']} source. Verify current terms and availability before buying.",
            render('deal.html', provider=esc(r['provider']), title=esc(r['title']), kind=esc(r['kind'].upper() + ' SOURCE'),
                   description=esc(r.get('description') or 'See the provider page for current terms.'),
                   source=esc(r['source_url']), outbound=esc(r['offer_url']),
                   checked=esc(r['fetched_at'][:10]), provider_page=provider_path,
                   price=(f"{esc(r['price'])} {esc(r['currency'])}" if 'price' in r and 'currency' in r else 'See official page')),
            {'@context': 'https://schema.org', '@graph': [
                service, breadcrumb]}, r['fetched_at'][:10])
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, lastmod in pages:
        sitemap.append(f'<url><loc>https://{esc(site["domain"])}{esc(path)}</loc>' + (f'<lastmod>{lastmod}</lastmod>' if lastmod else '') + '</url>')
    sitemap.append('</urlset>')
    write('sitemap.xml', '\n'.join(sitemap))
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: https://{site["domain"]}/sitemap.xml\n')
    print(f'Built {len(pages)} pages from {len(records)} verified sources')


if __name__ == '__main__':
    main()
