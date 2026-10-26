"""Static section index and the shared Part I lesson-card presentation."""
from html import escape
from bs4 import BeautifulSoup
from site_paths import SITE

def section_index(article):
    links = []
    for position, heading in enumerate(article.select("h2"), 1):
        if not heading.get("id"):
            heading["id"] = f"lesson-section-{position:02d}"
            heading["data-index-heading"] = ""
        label = escape(heading.get_text(" ", strip=True))
        links.append(f'<li><a href="#{heading["id"]}">{label}</a></li>')
    return f'''<aside class="lesson-index" data-temporal-component>
      <details open><summary>On this page</summary>
      <nav aria-label="Lesson sections"><ol>{''.join(links)}</ol></nav></details></aside>'''


def part_one_cards(page):
    """Migrate the accordion once, retaining its original lesson fragment links."""
    old = page.select_one("section.repairs")
    if old is None:
        return
    cards = []
    for number in range(1, 9):
        lesson = BeautifulSoup((SITE / f"lesson-{number}.html").read_text(encoding="utf-8"), "html.parser")
        title = escape(lesson.select_one(".hero h1").get_text())
        description = escape(lesson.select_one(".hero .lede").get_text())
        cards.append(f'''<article class="course-card" id="lesson-{number}">
          <a class="course-card__body" href="lesson-{number}.html">
          <span class="course-card__number">PART I · {number:02d} / COURSE {number:02d}</span>
          <h3>{title}</h3><p>{description}</p>
          <span class="course-card__link">Read the lesson →</span></a></article>''')
    markup = f'''<article class="document course-map" id="repairs"><section>
      <h2 class="snippet-section">Part I lessons</h2>
      <p>Start with the first signal, then make a call, carry a conversation and connect tools. Each lesson builds on the last; you can return to any lesson at any time.</p>
      <div class="course-grid">{''.join(cards)}</div></section></article>'''
    old.replace_with(BeautifulSoup(markup, "html.parser").find())
    page.select_one(".repair-header").decompose()
    for script in page.select('script[src^="part-one.js"]'):
        script.decompose()
