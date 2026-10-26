"""Serve site/ at the existing URLs, with links to the lesson source notebooks.

Run from the repository root: python scripts/serve_site.py
"""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from site_paths import SITE, public_path


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def translate_path(self, path):
        return str(public_path(path) or SITE)

    def send_head(self):
        if public_path(self.path) is None:
            self.send_error(404, "Page not found")
            return None
        return super().send_head()

    def list_directory(self, path):
        self.send_error(404, "Page not found")
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), SiteHandler) as server:
        print(f"Serving {SITE} at http://127.0.0.1:{server.server_port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
