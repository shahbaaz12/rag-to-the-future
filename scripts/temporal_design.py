"""Static design components, shared by the site and lesson renderer.

Navigation instruments sit outside lesson teaching articles; graph visuals
sit beside their source snippets. Existing teaching prose and code are preserved.
"""
from pathlib import Path
import json
from hashlib import sha256
from bs4 import BeautifulSoup
from lesson_stories import opening, remove_legacy_story
from lesson_navigation import section_index, part_one_cards
from american_english import standardize_page
from lesson_graphs import add_graph_visuals

ROOT = Path(__file__).resolve().parents[1]
PARTS = {
    1: ("one", "1985", "Analog workshop", "analogue", 1, 8),
    2: ("two", "2015", "Future workshop", "future", 9, 16),
    3: ("three", "1885", "Frontier workshop", "frontier", 17, max(entry['number'] for entry in json.loads((ROOT / 'part-three-lessons.json').read_text(encoding='utf-8')))),
}


def fragment(markup):
    return BeautifulSoup(markup, "html.parser").find()


def route(part, lesson=None):
    links = []
    for number, (word, year, label, _, start, end) in PARTS.items():
        current = f' aria-current="{"step" if lesson else "page"}"' if number == part else ""
        links.append(f'''<a href="part-{word}.html"{current} data-route-part="{number}">
          <span class="era-route__heading"><span class="era-route__number">0{number}</span><b>{year}</b><small>{label}</small><span class="era-route__count" data-route-count data-start="{start}" data-end="{end}">0 / {end-start+1}</span></span></a>''')
    track = f'''<div class="route-progress" role="progressbar" aria-label="Current course position" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" data-route-progress data-current-lesson="{lesson or 0}" data-current-part="{part}">
      <span class="route-progress__fill"></span><img class="route-progress__vehicle" src="assets/progress-car.svg" width="160" height="72" alt=""/></div>'''
    return '<nav class="era-route" aria-label="Three-part journey" data-temporal-component>' + ''.join(links) + track + '</nav>'


def circuit(part, lesson=None):
    _, year, label, _, start, end = PARTS[part]
    position = f"LESSON {lesson - start + 1:02d} / {end - start + 1:02d}" if lesson else f"PART {part:02d} / 03"
    return f'''<section class="temporal-circuit" aria-label="Current workshop" data-temporal-component>
      <div class="temporal-circuit__readout"><span>DESTINATION / {label.upper()}</span><strong>{year}</strong></div>
      <div class="temporal-circuit__position"><span>{position}</span><b>{f'COURSE {lesson:02d}' if lesson else f'{PARTS[3][-1]} AVAILABLE · {24-PARTS[3][-1]} PLANNED'}</b></div>
      </section>'''


def stage(part):
    _, year, label, asset, start, end = PARTS[part]
    systems = {
        1: [("VOICE", "1,2,3"), ("MEMORY", "4,5,6"), ("TOOLS", "7,8")],
        2: [("STATE", "9,10,11"), ("ROUTES", "12,13,14"), ("APPROVAL", "15,16")],
        3: [("RETRIEVE", "17,18"), ("FOLLOW-UP", "19"), ("SEARCH", "20,21")],
    }
    readouts = ''.join(f'<div><dt>{name}</dt><dd data-subsystem="{lessons}">PENDING</dd></div>' for name, lessons in systems[part])
    return f'''<aside class="workshop-stage" aria-label="{label} setting" data-temporal-component>
      <div class="workshop-stage__plate"><span>WORKSHOP / 0{part}</span><b>{year}</b></div>
      <img src="assets/workshop-{asset}.svg" width="960" height="520" alt="The same clocktower square in the {label.lower()}, with a time machine and {'railway' if part == 3 else 'service bay'}" fetchpriority="high"/>
      <div class="workshop-stage__caption"><span>FIXED POINT / CLOCKTOWER SQUARE</span><strong>{label}</strong></div>
      <dl class="workshop-subsystems">{readouts}</dl>
      </aside>'''


def completion(lesson):
    return f'''<section class="lesson-completion" aria-label="Record your lesson progress" data-temporal-component>
      <span class="lesson-end" data-lesson-end="{lesson}" aria-hidden="true"></span>
      <div><span class="temporal-label">LESSON {lesson:02d}</span><p>Your lesson progress</p><small>Marked complete when you reach the end. You can undo it below.</small></div>
      <div><label><input type="checkbox" data-complete="{lesson}"/> Lesson complete</label><small data-save-note>Saved on this browser</small></div></section>'''


def versioned(source):
    version = sha256((ROOT / source).read_bytes()).hexdigest()[:10]
    return f"{source}?v={version}"


def assets(page):
    glossary_styles = page.select('link[href^="lesson-glossary.css"]')
    if glossary_styles:
        glossary_styles[0]['href'] = versioned('lesson-glossary.css')
        for duplicate in glossary_styles[1:]:
            duplicate.decompose()
    styles = [link for link in page.select("link[href]") if link["href"].split("?")[0] == "temporal-design.css"]
    for link in styles:
        link.decompose()
    page.head.append(page.new_tag("link", rel="stylesheet", href=versioned("temporal-design.css")))
    for link in page.select('link[href^="lesson-story.css"]'):
        link.decompose()
    if page.select_one("#lesson"):
        page.head.append(page.new_tag("link", rel="stylesheet", href=versioned("lesson-story.css")))
    for link in page.select('link[href^="lesson-topics.css"]'):
        link.decompose()
    if page.select_one('#lesson'):
        page.head.append(page.new_tag('link', rel='stylesheet', href=versioned('lesson-topics.css')))
    for node in page.select('link[href^="lesson-tokenizer.css"], script[src^="lesson-tokenizer.js"]'):
        node.decompose()
    if page.select_one('.tokenizer-playground'):
        page.head.append(page.new_tag('link', rel='stylesheet', href=versioned('lesson-tokenizer.css')))
        page.head.append(page.new_tag('script', src=versioned('lesson-tokenizer.js'), defer=True))
    for node in page.select('link[href^="lesson-embeddings.css"], script[src^="lesson-embeddings.js"]'):
        node.decompose()
    if page.select_one('.embedding-demo'):
        page.head.append(page.new_tag('link', rel='stylesheet', href=versioned('lesson-embeddings.css')))
        page.head.append(page.new_tag('script', src=versioned('lesson-embeddings.js'), defer=True))
    for node in page.select('link[href^="lesson-hybrid.css"]'):
        node.decompose()
    if page.select_one('.hybrid-search-visual'):
        page.head.append(page.new_tag('link', rel='stylesheet', href=versioned('lesson-hybrid.css')))
    for node in page.select('link[href^="lesson-catalog.css"]'):
        node.decompose()
    if page.select_one('.catalog-index-visual'):
        page.head.append(page.new_tag('link', rel='stylesheet', href=versioned('lesson-catalog.css')))
    for node in page.select('link[href^="lesson-reading.css"]'):
        node.decompose()
    if page.body.get('data-reading-layout') == 'clear':
        page.head.append(page.new_tag('link', rel='stylesheet', href=versioned('lesson-reading.css')))
    for source in ("course-progress.js", "temporal-ui.js", "lesson-reading.js"):
        scripts = [script for script in page.select("script[src]") if script["src"].split("?")[0] == source]
        for script in scripts:
            script.decompose()
        if source != "lesson-reading.js" or page.select_one("#lesson"):
            page.head.append(page.new_tag("script", src=versioned(source), defer=True))
    if page.select_one(".course-map") and not page.select_one('link[href^="part-two.css"]'):
        page.head.append(page.new_tag("link", rel="stylesheet", href=versioned("part-two.css")))
    for script in page.select("script[src]"):
        source = script["src"].split("?")[0]
        if source in ("part-one.js", "script.js"):
            script["src"] = versioned(source)


def decorate_cards(page):
    for link in list(page.select("a.course-card")):
        card = page.new_tag("article", attrs={"class": "course-card"})
        link.wrap(card)
        link["class"] = ["course-card__body"]
    for card in page.select(".course-card"):
        link = card.select_one(".course-card__body")
        number = int(link["href"].removeprefix("lesson-").removesuffix(".html"))
        card.append(fragment(f'<label class="course-card__completion" data-temporal-component><input type="checkbox" data-complete="{number}"/> Lesson complete</label>'))


def decorate_home(page):
    page.body["class"] = ["temporal-home"]
    page.body["data-era"] = "one"
    markup = f'''<section class="temporal-atlas" aria-labelledby="atlas-title" data-temporal-component>
      <div class="temporal-atlas__header"><div><p class="temporal-label">THE WORKSHOP ATLAS</p><h2 id="atlas-title">One square.<br/><em>Three timelines.</em></h2></div>
      <div class="atlas-selector" role="group" aria-label="Preview a workshop"><button type="button" data-part="one" aria-pressed="true">01 / 1985</button><button type="button" data-part="two" aria-pressed="false">02 / 2015</button><button type="button" data-part="three" aria-pressed="false">03 / 1885</button></div></div>
      <figure class="atlas-view"><img id="atlas-image" src="assets/workshop-analogue.svg" width="960" height="520" alt="The clocktower square in the analogue workshop setting" loading="lazy"/>
      <figcaption><span id="atlas-label">1985 / ANALOGUE WORKSHOP</span><a id="atlas-link" href="part-one.html">Explore this workshop ↗</a></figcaption></figure>
      </section>'''
    page.select_one(".control-deck").insert_after(fragment(markup))
    for card in page.select(".journey-card"):
        if card.name == "a":
            continue
        destination = card.select_one(".card-footer a")["href"]
        for link in card.select("a"):
            link.name = "span"
            link.attrs = {"class": "journey-card__link"}
        card.name = "a"
        card["href"] = destination


def apply_design(page, part=None, lesson=None):
    for old in page.select("[data-temporal-component]"):
        old.decompose()
    if part == 1 and not lesson:
        part_one_cards(page)
    if lesson == 21:
        page.body['data-reading-layout'] = 'clear'
        for table in page.select('#lesson table'):
            labels = [cell.get_text(' ', strip=True) for cell in table.select('thead th')]
            for row in table.select('tbody tr'):
                for cell, label in zip(row.select('td'), labels):
                    cell['data-label'] = label
    else:
        page.body.attrs.pop('data-reading-layout', None)
    assets(page)
    page.body.append(fragment(route(part or 0, lesson)))
    if part is None:
        decorate_home(page)
        standardize_page(page)
        return
    word = PARTS[part][0]
    page.body["data-era"] = word
    page.body["class"] = ["temporal-lesson" if lesson else "temporal-map"]
    hero = page.select_one(".hero")
    if lesson:
        hero.append(fragment(circuit(part, lesson)))
        article = page.select_one("#lesson")
        add_graph_visuals(page, lesson)
        for old in page.select('link[href^="lesson-graphs.css"]'):
            old.decompose()
        if article.select_one('[data-lesson-graph], .rag-flow'):
            page.head.append(page.new_tag("link", rel="stylesheet", href=versioned("lesson-graphs.css")))
        if lesson == 1:
            remove_legacy_story(article)
        story = opening(lesson)
        if story:
            article.insert_before(fragment(story))
            start = hero.select_one("a.button")
            start["href"] = "#story-opening"
            start.string = "Enter the story ↓"
        article.insert_after(fragment(completion(lesson)))
        page.body.append(fragment(section_index(article)))
        standardize_page(page)
        return
    hero["class"] = ["hero", "temporal-map-hero"]
    if not hero.select_one(".hero-copy"):
        copy = page.new_tag("div", attrs={"class": "hero-copy"})
        for child in list(hero.contents):
            copy.append(child.extract())
        hero.append(copy)
    hero.select_one(".status-panel") and hero.select_one(".status-panel").decompose()
    hero.append(fragment(stage(part)))
    decorate_cards(page)
    standardize_page(page)


if __name__ == "__main__":
    targets = [("index.html", None, None)]
    targets += [(f"part-{info[0]}.html", part, None) for part, info in PARTS.items()]
    targets += [(f"lesson-{number}.html", 1 if number <= 8 else 2 if number <= 16 else 3, number) for number in range(1, PARTS[3][-1]+1)]
    for filename, part, lesson in targets:
        path = ROOT / filename
        page = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        apply_design(page, part, lesson)
        path.write_text(str(page), encoding="utf-8")
    print(f"Updated design components on {len(targets)} pages; existing teaching prose and code preserved.")
