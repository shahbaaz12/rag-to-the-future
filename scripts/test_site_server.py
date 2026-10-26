"""Check real HTTP routes after moving the website into site/."""
import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer

from serve_site import SiteHandler
from site_paths import ROOT, SITE


class QuietHandler(SiteHandler):
    def log_message(self, *args):
        pass


class SiteServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, method="GET"):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, response.read(), dict(response.getheaders())
        finally:
            connection.close()

    def test_existing_page_urls_and_folder_urls_serve_the_same_pages(self):
        for path, filename in (("/", "index.html"), ("/lesson-21.html", "lesson-21.html"),
                               ("/part-three.html", "part-three.html")):
            expected = (SITE / filename).read_bytes()
            for prefix in ("", "/site"):
                with self.subTest(url=prefix + path):
                    status, body, _ = self.request(prefix + path)
                    self.assertEqual(status, 200)
                    self.assertEqual(body, expected)

    def test_styles_scripts_images_and_cache_queries(self):
        for path in ("theme-toggle.css?v=test", "course-progress.js", "assets/progress-car.svg"):
            with self.subTest(url=path):
                status, body, headers = self.request("/" + path)
                self.assertEqual(status, 200)
                self.assertEqual(body, (SITE / path.split("?")[0]).read_bytes())
                self.assertNotIn("text/html", headers["Content-type"])

    def test_source_notebook_links_remain_available(self):
        source = "code/Part I Understanding the Basics/6-Memory.ipynb"
        url = source.replace(" ", "%20")
        for prefix in ("/", "/site/"):
            status, body, _ = self.request(prefix + url)
            self.assertEqual(status, 200)
            self.assertEqual(body, (ROOT / source).read_bytes())

    def test_missing_private_and_traversal_paths_are_not_served(self):
        for path in ("/missing.html", "/.git/config", "/code/.env", "/code/.venv/",
                     "/%2e%2e/AGENTS.md", "/site/%2e%2e/code/.env", "/%00", "/code/"):
            with self.subTest(url=path):
                self.assertEqual(self.request(path)[0], 404)


if __name__ == "__main__":
    unittest.main()
