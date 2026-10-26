"""Check local pages, anchors, styles, scripts, images, and notebook links.

Run: python scripts/validate_site.py [--base-url http://127.0.0.1:8765/]
"""
import argparse
import re
from html.parser import HTMLParser
from urllib.parse import quote, unquote, urljoin, urlsplit
from urllib.request import Request, urlopen

from site_paths import SITE, public_path


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.urls = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in (("id", "name") if tag == "a" else ("id",)):
            if attrs.get(key):
                self.ids.add(attrs[key])
        for key in ("href", "src", "poster", "xlink:href"):
            if attrs.get(key):
                self.urls.append(attrs[key])


def css_urls(text):
    for match in re.finditer(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^)]*))\s*\)", text):
        yield next(value for value in match.groups() if value is not None).strip()


def validate(base_url=None):
    documents = {}
    references = []
    for path in sorted(SITE.rglob("*")):
        if path.suffix not in (".html", ".svg"):
            continue
        text = path.read_text(encoding="utf-8")
        url = "/" + path.relative_to(SITE).as_posix()
        document = Links(text)
        documents[path] = document
        references.extend((url, link) for link in document.urls)
        references.extend((url, link) for link in css_urls(text))

    errors = []
    requests = {"/", "/site/"}
    stylesheets = set()
    checked = 0
    for source, link in references:
        original = urlsplit(link)
        if original.scheme or original.netloc:
            continue
        url = urlsplit(urljoin(source, link))
        target = public_path(url.path)
        if target is not None and target.is_dir():
            target = target / "index.html"
        if target is None or not target.is_file():
            errors.append(f"{source}: missing {link}")
            continue
        if target.suffix == ".css" and target not in stylesheets:
            stylesheets.add(target)
            references.extend((url.path, link) for link in css_urls(target.read_text(encoding="utf-8")))
        if url.fragment and target.suffix in (".html", ".svg"):
            document = documents.get(target)
            if document is None:
                document = Links(target.read_text(encoding="utf-8"))
            if unquote(url.fragment) not in document.ids:
                errors.append(f"{source}: missing anchor {link}")
        requests.add(quote(unquote(url.path), safe="/"))
        checked += 1

    if base_url:
        if urlsplit(base_url).hostname not in ("127.0.0.1", "localhost"):
            raise ValueError("HTTP validation is limited to the local preview server")
        for url in sorted(requests):
            try:
                with urlopen(Request(urljoin(base_url, url), method="HEAD"), timeout=10) as response:
                    if response.status != 200:
                        errors.append(f"HTTP {response.status}: {url}")
            except OSError as error:
                errors.append(f"HTTP {url}: {error}")
    if errors:
        raise AssertionError("\n".join(errors))
    print(f"Validated {len(documents)} HTML/SVG documents, {len(stylesheets)} linked stylesheets, and {checked} local references, including anchors.")
    if base_url:
        print(f"All {len(requests)} local URLs returned HTTP 200.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url")
    validate(parser.parse_args().base_url)
