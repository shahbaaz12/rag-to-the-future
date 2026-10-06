"""Static lesson graph visuals with topology read from the displayed source."""
import html
import json
from pathlib import Path
from bs4 import BeautifulSoup
from graph_topology import read_graphs

ROOT = Path(__file__).resolve().parents[1]
CAPTIONS = json.loads((ROOT / "lesson-graphs.json").read_text(encoding="utf-8"))
escape = html.escape


def back_edges(nodes, edges):
    visiting, visited, backwards = set(), set(), set()
    def visit(node):
        visiting.add(node)
        for source, target, _ in edges:
            if source != node:
                continue
            if target in visiting:
                backwards.add((source, target))
            elif target not in visited:
                visit(target)
        visiting.remove(node)
        visited.add(node)
    for node in nodes:
        if node not in visited:
            visit(node)
    return backwards


def positions(model):
    nodes = ["START", *model["nodes"], "END"]
    edges = model["edges"]
    backwards = back_edges(nodes, edges)
    simple = not backwards and len(edges) == len(nodes) - 1 and all(sum(e[0] == n for e in edges) <= 1 for n in nodes)
    if simple and len(nodes) <= 4:
        return {node: (110 + i * 220, 90) for i, node in enumerate(nodes)}, 220 * len(nodes), 180, backwards, True
    ranks = {node: 0 for node in nodes}
    for _ in nodes:
        for source, target, _ in edges:
            if (source, target) not in backwards:
                ranks[target] = max(ranks[target], ranks[source] + 1)
    if model["kind"] == "agent":
        ranks["END"] = max(ranks.values()) + 1
    rows = [[node for node in nodes if ranks[node] == rank] for rank in range(max(ranks.values()) + 1)]
    width = max(660, max(map(len, rows)) * 270 + 160)
    points = {node: (width / 2 + (i - (len(row) - 1) / 2) * 270, 70 + rank * 140) for rank, row in enumerate(rows) for i, node in enumerate(row)}
    return points, width, len(rows) * 140, backwards, False


def edge_shape(source, target, points, width, backwards, horizontal, index):
    x, y = points[source]
    tx, ty = points[target]
    if horizontal:
        return f"M {x+86} {y} L {tx-86} {ty}", (x+tx)/2, y-45
    if (source, target) in backwards:
        side = -1 if x < tx else 1
        lane = 30 + (index % 2) * 18 if side == -1 else width - 30 - (index % 2) * 18
        start_y, end_y = (y-14, ty+14) if source == target else (y, ty)
        label_y = y-48 if source == target else (y+ty)/2-8
        return f"M {x+side*95} {start_y} C {lane} {start_y-45}, {lane} {end_y+45}, {tx+side*95} {end_y}", lane-side*10, label_y
    if ty-y > 145:
        lane = 35+index%3*18
        return f"M {x} {y+30} L {x} {y+65} L {lane} {y+65} L {lane} {ty-65} L {tx} {ty-65} L {tx} {ty-30}", (x+lane)/2, y+55
    mid = (y+ty)/2
    return f"M {x} {y+30} C {x} {mid}, {tx} {mid}, {tx} {ty-30}", (x+tx)/2, mid-7


def node_svg(node, point, horizontal):
    x, y = point
    terminal = node in ("START", "END")
    width = 172 if horizontal else 190
    label = escape(node)
    if len(node) > 18 and "_" in node:
        cut = node.rfind("_", 0, 17) + 1
        label = f'<tspan x="{x}" dy="-9">{escape(node[:cut])}</tspan><tspan x="{x}" dy="22">{escape(node[cut:])}</tspan>'
    return f'<g class="graph-node{ " graph-node--terminal" if terminal else ""}"><rect x="{x-width/2}" y="{y-30}" width="{width}" height="60" rx="{30 if terminal else 6}"/><text x="{x}" y="{y+6}" text-anchor="middle">{label}</text></g>'


def graph_svg(model, identity, title):
    points, width, height, backwards, horizontal = positions(model)
    routes = []
    for index, (source, target, label) in enumerate(model["edges"]):
        path, x, y = edge_shape(source, target, points, width, backwards, horizontal, index)
        label = "no tool calls" if label == "END" else label
        conditional = label not in ("next", "input", "wait for both", "wait for all", "initial state", "returned updates", "updated state", "tool result")
        label_half_width = len(label) * 4.8
        x = max(label_half_width + 12, min(x, width - label_half_width - 12))
        routes.append(f'<path class="graph-edge{ " graph-edge--choice" if conditional else ""}" d="{path}" marker-end="url(#{identity}-arrow)"/><text class="graph-edge-label" x="{x}" y="{y}" text-anchor="middle">{escape(label)}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{identity}-svg-title"><title id="{identity}-svg-title">{escape(title)}. See the caption and graph connections for the text equivalent.</title><defs><marker id="{identity}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>{"".join(routes)}{"".join(node_svg(node, point, horizontal) for node, point in points.items())}</svg>'


def connections(model):
    items = [f'<li><code>{escape(source)}</code> → <code>{escape(target)}</code> <span>({escape(label)})</span></li>' for source, target, label in model["edges"]]
    joins = [f'<p>The join at <code>{escape(target)}</code> waits for all of: {", ".join(f"<code>{escape(source)}</code>" for source in sources)}.</p>' for sources, target in model["joins"]]
    return f'<details class="lesson-graph__connections"><summary>Graph connections in text</summary><ul>{"".join(items)}</ul>{"".join(joins)}</details>'


def panel(model, identity, title, caption):
    kind = "CONCEPTUAL AGENT FLOW" if model["kind"] == "agent" else "GRAPH STRUCTURE"
    saved = '<span class="lesson-graph__storage">Checkpointer attached · storage outside the node path</span>' if model["checkpoint"] else ""
    return f'<figure class="lesson-graph" data-lesson-graph="{identity}" aria-labelledby="{identity}-title"><div class="lesson-graph__header"><span>{kind}</span><h4 id="{identity}-title">{escape(title)}</h4></div><p class="lesson-graph__hint">Scroll sideways to explore the diagram →</p><div class="lesson-graph__canvas" tabindex="0" role="region" aria-label="{escape(title)} diagram; scroll horizontally on narrow screens">{graph_svg(model, identity, title)}</div><figcaption><p>{escape(caption)}</p>{saved}</figcaption>{connections(model)}</figure>'


def add_graph_visuals(page, lesson):
    for old in page.select("[data-lesson-graph]"):
        old.decompose()
    article = page.select_one("#lesson")
    for figure, model in read_graphs(article):
        key = f'{lesson}:{model["name"]}'
        title, caption = CAPTIONS[key]
        identity = f'graph-{lesson}-{model["name"].replace("_", "-")}'
        anchor = article.find(attrs={"data-graph-preview": model["name"]})
        if anchor is None:
            anchor = figure
        if lesson == 9 and model["name"] == "builder":
            anchor = next(h for h in article.select("h2") if h.get_text() == "What we are building")
            for sibling in anchor.find_next_siblings():
                if sibling.name == "h2":
                    break
                anchor = sibling
        anchor.insert_after(BeautifulSoup(panel(model, identity, title, caption), "html.parser"))
