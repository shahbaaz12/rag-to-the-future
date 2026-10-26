"""Optional narrative openings, rendered outside the teaching article."""
import json
from html import escape

from site_paths import SITE

STORIES = json.loads((SITE / "lesson-stories.json").read_text(encoding="utf-8"))


def remove_legacy_story(article):
    """Migrate Lesson 1's old scene; retain its technical explanation verbatim."""
    heading = next((node for node in article.select("h2")
                    if node.get_text().startswith("Optional story —")), None)
    if heading is None:
        return
    for sibling in list(heading.next_siblings):
        if getattr(sibling, "name", None) == "h2":
            break
        if getattr(sibling, "name", None) in ("p", "blockquote"):
            if sibling.get_text().startswith("The machine can generate language."):
                continue
            sibling.decompose()
    heading.decompose()


def opening(lesson):
    story = STORIES.get(str(lesson))
    if story is None:
        return None
    paragraphs = ''.join(f'<p>{escape(text)}</p>' for text in story["paragraphs"])
    title = escape(story["title"])
    return f'''<section class="lesson-story" id="story-opening" aria-labelledby="story-title" data-temporal-component>
      <figure class="lesson-story__setting"><img src="assets/workshop-{story['asset']}.svg" width="960" height="520" alt=""/>
      <figcaption>{escape(story['image_caption'])}</figcaption><p>Original course adventure inspired by the films.</p></figure>
      <div class="lesson-story__copy"><p class="temporal-label">{story['year']} / {escape(story['location'])}</p>
      <h2 id="story-title">{title}</h2>
      <details class="lesson-story__scene" open><summary>Professor’s field note · Optional story</summary>
      <p class="lesson-story__recap"><strong>Previously:</strong> {escape(story['recap'])}</p>{paragraphs}
      <p class="lesson-story__obstacle"><strong>Current obstacle:</strong> {escape(story['obstacle'])}</p></details>
      </div></section>'''
