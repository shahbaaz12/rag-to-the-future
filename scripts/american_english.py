"""American English for authored prose; source code and technical names stay exact."""
import json
import re
from bs4 import Comment

SPELLINGS = {}
for british, american in {
    'authorise': 'authorize', 'categorise': 'categorize', 'emphasise': 'emphasize',
    'generalise': 'generalize', 'initialise': 'initialize', 'maximise': 'maximize',
    'minimise': 'minimize', 'normalise': 'normalize', 'optimise': 'optimize',
    'organise': 'organize', 'personalise': 'personalize', 'recognise': 'recognize',
    'serialise': 'serialize', 'specialise': 'specialize', 'stabilise': 'stabilize',
    'standardise': 'standardize', 'summarise': 'summarize', 'utilise': 'utilize',
    'visualise': 'visualize',
}.items():
    for old, new in [(british, american), (british + 's', american + 's'),
                     (british + 'd', american + 'd'), (british[:-1] + 'ing', american[:-1] + 'ing'),
                     (british[:-1] + 'ation', american[:-1] + 'ation')]:
        SPELLINGS[old] = new
        if old.endswith('ation'):
            SPELLINGS[old + 's'] = new + 's'
            SPELLINGS[old + 'al'] = new + 'al'
SPELLINGS.update({
    'analogue': 'analog', 'behaviour': 'behavior', 'behaviours': 'behaviors', 'behavioural': 'behavioral',
    'colour': 'color', 'colours': 'colors', 'coloured': 'colored', 'colouring': 'coloring',
    'favour': 'favor', 'favours': 'favors', 'favourite': 'favorite', 'favourites': 'favorites',
    'centre': 'center', 'centres': 'centers', 'centred': 'centered', 'centring': 'centering',
    'analyse': 'analyze', 'analysed': 'analyzed', 'analysing': 'analyzing',
    'grey': 'gray', 'labelled': 'labeled', 'labelling': 'labeling', 'modelling': 'modeling',
    'modelled': 'modeled', 'travelling': 'traveling', 'travelled': 'traveled',
    'cancelled': 'canceled', 'cancelling': 'canceling', 'learnt': 'learned',
    'recognisable': 'recognizable', 'recognisably': 'recognizably',
    'practise': 'practice', 'practises': 'practices', 'practised': 'practiced', 'practising': 'practicing',
    'artefact': 'artifact', 'artefacts': 'artifacts', 'licence': 'license', 'licences': 'licenses',
})
WORDS = re.compile(r'\b(?:' + '|'.join(sorted(SPELLINGS, key=len, reverse=True)) + r')\b', re.I)
PROTECTED = re.compile(r'```.*?```|`+[^`]*`+|<!--.*?-->|https?://[^\s)<>]+|\]\([^\n]*?\)', re.S)


def americanize(text):
    def replace(match):
        word = match[0]
        replacement = SPELLINGS[word.lower()]
        return replacement.upper() if word.isupper() else replacement.capitalize() if word[0].isupper() else replacement
    return WORDS.sub(replace, text)


def markdown_prose(text):
    pieces = []
    cursor = 0
    for match in PROTECTED.finditer(text):
        pieces.extend([americanize(text[cursor:match.start()]), match[0]])
        cursor = match.end()
    return ''.join(pieces) + americanize(text[cursor:])


def standardize_page(page):
    """Keep copied/displayed code, IDs and asset paths untouched."""
    page.html['lang'] = 'en-US'
    for node in list(page.find_all(string=True)):
        if isinstance(node, Comment) or node.find_parent(['pre', 'code', 'script', 'style']):
            continue
        if node.find_parent(class_=['snippet-source-comments', 'snippet-source', 'lesson-term']):
            continue
        updated = americanize(str(node))
        if updated != str(node):
            node.replace_with(updated)
    for node in page.find_all(True):
        for attribute in ('alt', 'title', 'aria-label', 'placeholder'):
            if attribute in node.attrs:
                node[attribute] = americanize(node[attribute])
        if node.name == 'meta' and node.get('name') == 'description':
            node['content'] = americanize(node['content'])
    registry = page.select_one('#lesson-terms')
    if registry:
        entries = json.loads(registry.string)
        for entry in entries:
            entry['definition'] = americanize(entry['definition'])
        registry.string = json.dumps(entries, ensure_ascii=False).replace('<', '\\u003c')
