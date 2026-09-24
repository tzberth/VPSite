# ::ILANG [TYPE:module][ROLE:verify-public-offer-sources]
# ::RULE{Read providers from .ilang/site.ilang; respect robots.txt}
# ::BOUNDARY{never:guess prices or dates bypass access controls|scope:permanent}
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from config import load_config

ROOT = Path(__file__).parent
AGENT = 'VPSDealsRadar/1.0 (+public-source-check; contact via repository)'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.description = ''
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'meta' and attrs.get('name', '').lower() == 'description':
            self.description = attrs.get('content', '')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def allowed(url):
    parsed = urllib.parse.urlparse(url)
    robots = urllib.robotparser.RobotFileParser()
    robots.set_url(f'{parsed.scheme}://{parsed.netloc}/robots.txt')
    try:
        robots.read()
        return robots.can_fetch(AGENT, url)
    except (OSError, urllib.error.URLError):
        return False


def fetch(provider):
    url = provider['source']
    if not allowed(url):
        print(f'Skipped (robots unavailable or disallowed): {url}')
        return None
    request = urllib.request.Request(url, headers={'User-Agent': AGENT, 'Accept-Language': 'en-US,en;q=0.9'})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get('Content-Type', '')
            if 'html' not in content_type:
                return None
            html = response.read(2_000_000).decode('utf-8', errors='replace')
    except (OSError, urllib.error.URLError) as exc:
        print(f'Skipped (fetch failed): {url}: {exc}')
        return None
    page = Page()
    page.feed(html)
    title = re.sub(r'\s+', ' ', page.title).strip()
    if not title:
        return None
    return {
        'id': re.sub(r'[^a-z0-9]+', '-', provider['name'].lower()).strip('-'),
        'provider': provider['name'],
        'title': title[:160],
        'description': re.sub(r'\s+', ' ', page.description).strip()[:300],
        'kind': provider['kind'],
        'offer_url': provider['affiliate'] or url,
        'source_url': url,
        'fetched_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def main():
    _, providers = load_config()
    existing_path = ROOT / 'data' / 'offers.json'
    existing = json.loads(existing_path.read_text(encoding='utf-8')) if existing_path.exists() else []
    previous = {item['provider']: item for item in existing if item.get('provider')}
    results = []
    for provider in providers:
        item = fetch(provider)
        if item:
            results.append(item)
        elif provider['name'] in previous:
            # Keep the last verified source while clearly exposing its last successful fetch time.
            results.append(previous[provider['name']])
    existing_path.parent.mkdir(exist_ok=True)
    existing_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(results)} verified source entries saved')


if __name__ == '__main__':
    main()
