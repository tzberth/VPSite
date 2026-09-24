# ::ILANG [TYPE:module][ROLE:verify-publishable-static-output]
# ::RULE{Check generated canonical URLs, JSON-LD, sitemap, and source evidence}
# ::BOUNDARY{never:accept missing provenance or invented price|scope:permanent}
import json
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

from config import load_config


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.jsonld = []
        self.capture = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.capture = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.capture = False

    def handle_data(self, data):
        if self.capture:
            self.jsonld.append(json.loads(data))


def main():
    root = Path(__file__).parent
    site, _ = load_config()
    domain = site['domain']
    offers = json.loads((root / 'data/offers.json').read_text(encoding='utf-8'))
    for offer in offers:
        assert offer['source_url'].startswith('https://') and offer['fetched_at']
        assert ('price' in offer) == ('currency' in offer)
    pages = list((root / 'site').rglob('*.html'))
    for page in pages:
        relative = page.relative_to(root / 'site')
        path = '/' if relative == Path('index.html') else '/' + relative.parent.as_posix() + '/'
        doc = Metadata()
        doc.feed(page.read_text(encoding='utf-8'))
        assert doc.canonicals == [f'https://{domain}{path}'], page
        assert len(doc.jsonld) == 1, page
    xml = ElementTree.parse(root / 'site/sitemap.xml').getroot()
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [element.text for element in xml.findall('s:url/s:loc', ns)]
    assert len(urls) == len(pages) and all(url.startswith(f'https://{domain}/') for url in urls)
    print(f'Verified {len(pages)} HTML pages, JSON-LD, canonicals, and sitemap URLs')


if __name__ == '__main__':
    main()
