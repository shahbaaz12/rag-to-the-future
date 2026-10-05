"""Static design components, shared by the site and lesson renderer.

All instruments sit outside lesson teaching articles. Run this file to apply
the design layer without regenerating or editing teaching content.
"""
from pathlib import Path
from hashlib import sha256
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PARTS = {
    1: ("one", "1985", "Analogue workshop", "analogue", 1, 8),
    2: ("two", "2045", "Future workshop", "future", 9, 16),
    3: ("three", "????", "Frontier workshop", "frontier", 17, 20),
}


def fragment(markup):
    return BeautifulSoup(markup, "html.parser").find()


def meter(start, end):
    total = end - start + 1
    return f'''<div class="charge-meter" data-course-meter data-start="{start}" data-end="{end}">
      <div class="charge-meter__label"><span>REPAIRS RECORDED</span><b><span data-meter-count>0</span> / {total}</b></div>
      <div class="charge-meter__track" role="progressbar" aria-label="Recorded lesson completion" aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="0"><i></i></div>
      <p data-save-note>Saved on this browser · self-reported</p></div>'''


def route(part, lesson=None):
    links = []
    for number, (word, year, label, _, _, _) in PARTS.items():
        current = f' aria-current="{"step" if lesson else "page"}"' if number == part else ""
        links.append(f'<a href="part-{word}.html"{current}><span class="era-route__number">0{number}</span><span><b>{year}</b><small>{label}</small></span><span aria-hidden="true">↗</span></a>')
    return '<nav class="era-route" aria-label="Three-part journey" data-temporal-component>' + ''.join(links) + '</nav>'


def circuit(part, lesson=None):
    _, year, label, _, start, end = PARTS[part]
    position = f"LESSON {lesson - start + 1:02d} / {end - start + 1:02d}" if lesson else f"PART {part:02d} / 03"
    return f'''<section class="temporal-circuit" aria-label="Current workshop and progress" data-temporal-component>
      <div class="temporal-circuit__readout"><span>DESTINATION / {label.upper()}</span><strong>{year}</strong></div>
      <div class="temporal-circuit__position"><span>{position}</span><b>{f'COURSE {lesson:02d}' if lesson else '20 AVAILABLE · 4 PLANNED'}</b></div>
      {meter(start, end)}</section>'''


def stage(part):
    _, year, label, asset, start, end = PARTS[part]
    systems = {
        1: [("VOICE", "1,2,3"), ("MEMORY", "4,5,6"), ("TOOLS", "7,8")],
        2: [("STATE", "9,10,11"), ("ROUTES", "12,13,14"), ("APPROVAL", "15,16")],
        3: [("RETRIEVE", "17"), ("FOLLOW-UP", "18"), ("SEARCH", "19,20")],
    }
    readouts = ''.join(f'<div><dt>{name}</dt><dd data-subsystem="{lessons}">PENDING</dd></div>' for name, lessons in systems[part])
    return f'''<aside class="workshop-stage" aria-label="{label} setting" data-temporal-component>
      <div class="workshop-stage__plate"><span>WORKSHOP / 0{part}</span><b>{year}</b></div>
      <img src="assets/workshop-{asset}.svg" width="960" height="520" alt="The same clocktower square in the {label.lower()}, with a time machine and {'railway' if part == 3 else 'service bay'}" fetchpriority="high"/>
      <div class="workshop-stage__caption"><span>FIXED POINT / CLOCKTOWER SQUARE</span><strong>{label}</strong></div>
      <dl class="workshop-subsystems">{readouts}</dl>
      <div class="workshop-stage__instrument"><img src="assets/flux-capacitor.svg" width="360" height="320" alt=""/>{meter(start, end)}</div></aside>'''


def completion(lesson):
    return f'''<section class="lesson-completion" aria-label="Record your lesson progress" data-temporal-component>
      <div><span class="temporal-label">WORKSHOP LOG / {lesson:02d}</span><p>Record this repair</p></div>
      <div><label><input type="checkbox" data-complete="{lesson}"/> Lesson complete</label><small data-save-note>Saved on this browser · self-reported</small></div></section>'''


def versioned(source):
    version = sha256((ROOT / source).read_bytes()).hexdigest()[:10]
    return f"{source}?v={version}"


def assets(page):
    styles = [link for link in page.select("link[href]") if link["href"].split("?")[0] == "temporal-design.css"]
    for link in styles:
        link.decompose()
    page.head.append(page.new_tag("link", rel="stylesheet", href=versioned("temporal-design.css")))
    for source in ("course-progress.js", "temporal-ui.js"):
        scripts = [script for script in page.select("script[src]") if script["src"].split("?")[0] == source]
        for script in scripts:
            script.decompose()
        page.head.append(page.new_tag("script", src=versioned(source), defer=True))
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
        card.append(fragment(f'<label class="course-card__completion" data-temporal-component><input type="checkbox" data-complete="{number}"/> Repair recorded</label>'))


def decorate_home(page):
    page.body["class"] = ["temporal-home"]
    page.body["data-era"] = "one"
    markup = f'''<section class="temporal-atlas" aria-labelledby="atlas-title" data-temporal-component>
      <div class="temporal-atlas__header"><div><p class="temporal-label">THE WORKSHOP ATLAS</p><h2 id="atlas-title">One square.<br/><em>Three timelines.</em></h2></div>
      <div class="atlas-selector" role="group" aria-label="Preview a workshop"><button type="button" data-part="one" aria-pressed="true">01 / 1985</button><button type="button" data-part="two" aria-pressed="false">02 / 2045</button><button type="button" data-part="three" aria-pressed="false">03 / FRONTIER</button></div></div>
      <figure class="atlas-view"><img id="atlas-image" src="assets/workshop-analogue.svg" width="960" height="520" alt="The clocktower square in the analogue workshop setting" loading="lazy"/>
      <figcaption><span id="atlas-label">1985 / ANALOGUE WORKSHOP</span><a id="atlas-link" href="part-one.html">Explore this workshop ↗</a></figcaption></figure>
      {route(0)}{meter(1, 20)}</section>'''
    page.select_one(".control-deck").insert_after(fragment(markup))


def apply_design(page, part=None, lesson=None):
    for old in page.select("[data-temporal-component]"):
        old.decompose()
    assets(page)
    if part is None:
        decorate_home(page)
        return
    word = PARTS[part][0]
    page.body["data-era"] = word
    page.body["class"] = ["temporal-lesson" if lesson else "temporal-map"]
    hero = page.select_one(".hero")
    hero.insert_before(fragment(route(part, lesson)))
    if lesson:
        hero.append(fragment(circuit(part, lesson)))
        page.select_one("#lesson").insert_after(fragment(completion(lesson)))
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


if __name__ == "__main__":
    targets = [("index.html", None, None)]
    targets += [(f"part-{info[0]}.html", part, None) for part, info in PARTS.items()]
    targets += [(f"lesson-{number}.html", 1 if number <= 8 else 2 if number <= 16 else 3, number) for number in range(1, 21)]
    for filename, part, lesson in targets:
        path = ROOT / filename
        page = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        apply_design(page, part, lesson)
        path.write_text(str(page), encoding="utf-8")
    print(f"Updated design components on {len(targets)} pages; teaching articles preserved.")
