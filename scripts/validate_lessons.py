"""Check lesson source, copyable snippets, comments, glossary, and navigation.

From code/: uv run python ../scripts/validate_lessons.py
These checks do not call a model API or read API keys.
"""

import ast
import io
import json
import tokenize
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from site_paths import SITE, public_path

ROOT = Path(__file__).resolve().parents[1]
introduced = {}
total = 0

for path in (ROOT / "code").glob("Part*/*.ipynb"):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for entry in notebook["cells"]:
        if entry["cell_type"] == "code":
            ast.parse("".join(entry["source"]), filename=f'{path.name}:{entry["id"]}')

for path in [*(ROOT / "code").glob("*.py"), *(ROOT / "scripts").glob("*.py")]:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

last_lesson = max(entry["number"] for filename in ("part-two-lessons.json", "part-three-lessons.json") for entry in json.loads((SITE / filename).read_text(encoding="utf-8")))
for lesson in range(1, last_lesson + 1):
    page = BeautifulSoup((SITE / f"lesson-{lesson}.html").read_text(encoding="utf-8"), "html.parser")
    for card in page.select(".snippet-card"):
        code = card.select_one(".code-explorer__source").get_text()
        visible = "\n".join(line.get_text().rstrip("\n") for line in card.select(".code-explorer__line"))
        assert visible == code, f"Lesson {lesson}: visible code differs from copied code"
        source, location = card["data-source"].split("#", 1)
        path = ROOT / source
        if path.suffix == ".ipynb":
            cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
            actual = "".join(next(entry for entry in cells if entry["id"] == location)["source"])
        else:
            actual = path.read_text(encoding="utf-8")
        assert code in actual, f"Lesson {lesson}: source mismatch in {source}"
        if card.select_one(".code-explorer__language").get_text().lower() == "python":
            ast.parse(code)
            comments = [token.string for token in tokenize.generate_tokens(io.StringIO(code).readline) if token.type == tokenize.COMMENT]
            assert comments == [comment.get_text() for comment in card.select(".snippet-comment")], f"Lesson {lesson}: comment mismatch"
        assert card.select_one(".snippet-prose") and card.select_one(".snippet-result")
        assert not card.select("pre mark, .snippet-comment mark"), "Glossary markup must not change source code or comments"
        total += 1

    for mark in page.select(".lesson-term"):
        key = mark["data-term"]
        assert key not in introduced, f"Repeated highlight for {key}"
        introduced[key] = {"lesson": lesson, "anchor": mark["id"]}
    registry = json.loads(page.select_one("#lesson-terms").string)
    assert {entry["term"] for entry in registry} == set(introduced), f"Lesson {lesson}: glossary does not carry earlier terms forward"
    for entry in registry:
        assert entry["definition"] and introduced[entry["term"]] == {"lesson": entry["lesson"], "anchor": entry["anchor"]}
    navigation = page.select("#lesson > .lesson-pagination a")
    assert [link["href"] for link in navigation] == [f"lesson-{lesson-1}.html" if lesson > 1 else "part-one.html", f"lesson-{lesson+1}.html" if lesson < last_lesson else "part-three.html"]
    for element in page.select("a[href], link[href], script[src], img[src]"):
        url = urlsplit(element.get("href", element.get("src")))
        if not url.scheme and url.path:
            target = public_path(url.path)
            assert target and target.exists(), f"Lesson {lesson}: broken local link {url.path}"
    ids = [element["id"] for element in page.select("[id]")]
    assert len(ids) == len(set(ids)), f"Lesson {lesson}: duplicate element IDs"
    print(f"Lesson {lesson}: source, comments, glossary and navigation OK")

assert introduced["init_chat_model"]["lesson"] == 3
print(f"Validated {total} snippets and {len(introduced)} terms across {last_lesson} lessons.")
