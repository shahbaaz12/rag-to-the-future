(() => {
  const wordVectors = {
    king: [2, 4], queen: [3, 5], man: [2, 2], woman: [3, 3],
    paris: [7, 5], france: [6, 3], delhi: [10, 5], india: [9, 3],
    tokyo: [10, 8], japan: [9, 6], berlin: [7, 8], germany: [6, 6],
    walking: [3, 8], walk: [2, 7], run: [4, 7], running: [5, 8],
    banana: [1, .5], grape: [1.6, .7], aeroplane: [10, .5],
  };
  const equations = {
    royalty: ['king', 'man', 'woman'], india: ['paris', 'france', 'india'],
    germany: ['tokyo', 'japan', 'germany'], tense: ['walking', 'walk', 'run'],
  };
  function analogy(key) {
    const words = equations[key];
    const vector = wordVectors[words[0]].map((value, i) => value - wordVectors[words[1]][i] + wordVectors[words[2]][i]);
    const candidates = Object.keys(wordVectors).filter(word => !words.includes(word));
    const answer = candidates.reduce((best, word) => {
      const distance = name => wordVectors[name].reduce((sum, value, i) => sum + (value - vector[i]) ** 2, 0);
      return distance(word) < distance(best) ? word : best;
    });
    return { words, vector, answer };
  }
  const wordGroups = {
    cat: ['cat', 'cats', 'kitten', 'kittens'], dog: ['dog', 'dogs', 'puppy'],
    sleep: ['sleep', 'sleeping', 'asleep', 'nap', 'napping'], sofa: ['couch', 'sofa'],
    coding: ['code', 'coding', 'program', 'programming', 'software'],
    enjoyment: ['love', 'enjoy', 'like'], flight: ['flight', 'plane', 'airplane'],
    mumbai: ['mumbai', 'bombay'], food: ['food', 'meal', 'eat', 'eating'],
    hunger: ['hungry', 'hunger'], money: ['money', 'stock', 'market'],
  };
  const groupForWord = new Map(Object.entries(wordGroups).flatMap(([group, words]) => words.map(word => [word, group])));
  const stopWords = new Set('a an the is are am was were be on in at to of and i my it this that'.split(' '));
  function demoVector(text) {
    const counts = new Map();
    for (const word of text.normalize('NFC').toLowerCase().match(/[\p{L}\p{N}\p{M}]+/gu) || []) {
      if (stopWords.has(word)) continue;
      const feature = groupForWord.get(word) || word;
      counts.set(feature, (counts.get(feature) || 0) + 1);
    }
    return counts;
  }
  function compareSentences(a, b) {
    const left = demoVector(a), right = demoVector(b);
    const features = [...new Set([...left.keys(), ...right.keys()])].sort();
    const dot = features.reduce((sum, feature) => sum + (left.get(feature) || 0) * (right.get(feature) || 0), 0);
    const length = counts => Math.sqrt([...counts.values()].reduce((sum, value) => sum + value * value, 0));
    const denominator = length(left) * length(right);
    return { left, right, features, score: denominator ? Math.min(1, dot / denominator) : null };
  }
  const sentencePresets = {
    synonyms: ['A cat is sleeping on the couch.', 'A kitten is napping on the sofa.'],
    paraphrase: ['I love programming.', 'I enjoy coding.'],
    city: ['Flight to Mumbai', 'Plane to Bombay'],
    related: ['I am hungry and want a meal.', 'I want food.'],
    opposite: ['The cat is asleep.', 'The cat is not asleep.'],
    unrelated: ['The stock market crashed.', 'A cat is sleeping.'],
  };
  const chunkSource = `# City guide

## Travel
The train station connects the city to nearby towns. Buy train tickets before a busy travel weekend. Local buses help travelers reach the station.

## Weather
The weather forecast helps you plan outdoor visits. Carry a jacket for cool mornings. Rain can change your plans, so check the forecast before leaving.

## Food
Local cafes serve fresh dosa and idli for breakfast. Food stalls offer quick meals near the market. Try a cup of coffee after your meal.`;
  function cutsWord(source, offset) {
    return offset > 0 && offset < source.length && /[\p{L}\p{N}]/u.test(source[offset - 1]) && /[\p{L}\p{N}]/u.test(source[offset]);
  }
  function fixedChunks(source, size, overlap = 0) {
    const limit = Math.max(1, Math.floor(size));
    const repeat = Math.min(limit - 1, Math.max(0, Math.floor(overlap)));
    const result = [];
    for (let start = 0; start < source.length;) {
      const end = Math.min(start + limit, source.length);
      result.push({ text: source.slice(start, end), start, end, repeated: start ? repeat : 0 });
      if (end === source.length) break;
      start = end - repeat;
    }
    return result;
  }
  function recursiveChunks(source, size) {
    const limit = Math.max(1, Math.floor(size));
    const boundaries = [/\n\n+/g, /[.!?]\s+/g, /\s+/g].map(pattern => [...source.matchAll(pattern)].map(match => match.index + match[0].length));
    const result = [];
    for (let start = 0; start < source.length;) {
      let end = Math.min(start + limit, source.length);
      if (end < source.length) {
        for (const level of boundaries) {
          const options = level.filter(offset => offset > start && offset <= end);
          if (options.length) { end = options[options.length - 1]; break; }
        }
      }
      result.push({ text: source.slice(start, end), start, end, repeated: 0 });
      start = end;
    }
    return result;
  }
  function semanticChunks(source) {
    const body = source.replace(/^#+[^\n]*$/gm, '').replace(/\s+/g, ' ').trim();
    const result = [];
    for (const text of body.match(/[^.!?]+(?:[.!?]+|$)/g) || []) {
      const sentence = text.trim();
      if (!sentence) continue;
      const topic = /train|ticket|bus|travel|station/i.test(sentence) ? 'Travel'
        : /weather|forecast|jacket|cool|rain/i.test(sentence) ? 'Weather'
        : /food|cafe|dosa|idli|meal|coffee|breakfast/i.test(sentence) ? 'Food' : 'Other';
      const previous = result[result.length - 1];
      if (previous && previous.topic === topic) previous.text += ` ${sentence}`;
      else result.push({ text: sentence, topic, repeated: 0 });
    }
    return result;
  }
  function structureChunks(source) {
    const headings = [...source.matchAll(/^##\s+.+$/gm)].map(match => match.index);
    const starts = [0, ...headings.slice(1)];
    return starts.map((start, i) => {
      const end = starts[i + 1] ?? source.length;
      return { text: source.slice(start, end), start, end, repeated: 0 };
    }).filter(chunk => chunk.text.length);
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { analogy, wordVectors, compareSentences, chunkSource, cutsWord, fixedChunks, recursiveChunks, semanticChunks, structureChunks };
  }
  if (typeof document === 'undefined') return;
  const make = (name, text, className) => {
    const node = document.createElement(name);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  function selectButton(demo, selector, chosen) {
    demo.querySelectorAll(selector).forEach(button => button.setAttribute('aria-pressed', String(button === chosen)));
  }
  const arithmetic = document.querySelector('.arithmetic-demo');
  if (arithmetic) {
    function show(key) {
      const { words, vector, answer } = analogy(key);
      const [a, b, c] = words;
      arithmetic.querySelector('[data-equation]').textContent = `${a} − ${b} + ${c} ≈ ${answer}`;
      const steps = arithmetic.querySelector('[data-equation-steps]');
      steps.replaceChildren();
      [[a, wordVectors[a]], [`subtract ${b}`, wordVectors[b]], [`add ${c}`, wordVectors[c]], ['result', vector]].forEach(([label, values]) => {
        const card = make('div');
        card.append(make('span', label), make('strong', `[${values.join(', ')}]`));
        steps.append(card);
      });
      arithmetic.querySelector('[data-equation-explanation]').textContent = `The result is [${vector.join(', ')}]. The closest point in this toy vocabulary is ${answer}, at [${wordVectors[answer].join(', ')}]. Try another relationship.`;
    }
    arithmetic.querySelectorAll('[data-equation-key]').forEach(button => button.addEventListener('click', () => {
      selectButton(arithmetic, '[data-equation-key]', button); show(button.dataset.equationKey);
    }));
    show('royalty');
  }
  const map = document.querySelector('.vector-map-demo');
  if (map) {
    const svgNode = (tag, attributes) => {
      const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
      Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
      return node;
    };
    const position = word => [55 + wordVectors[word][0] * 55, 290 - wordVectors[word][1] * 40];
    const points = map.querySelector('[data-map-points]');
    for (const word of ['king', 'queen', 'man', 'woman', 'paris', 'france', 'delhi', 'india', 'banana', 'grape', 'aeroplane']) {
      const [x, y] = position(word);
      const point = svgNode('circle', { cx: x, cy: y, r: 6, class: 'embedding-dot' });
      const label = svgNode('text', { x: x + 9, y: y + (word === 'banana' ? 20 : word === 'grape' ? -11 : 4), class: 'embedding-label' });
      label.textContent = word; points.append(point, label);
    }
    const descriptions = {
      royalty: 'king → queen and man → woman both move by [1, 1] in this teaching map. The parallel arrows show the same offset.',
      capital: 'france → paris and india → delhi both move by [1, 2]. Here, that shared offset represents country → capital.',
      food: 'Banana and grape are drawn near each other. Aeroplane is farther away. These positions illustrate related topics; they are not measured similarity scores.',
      clear: 'Choose a pair to see the relationship between its points.',
    };
    function draw(key) {
      const links = map.querySelector('[data-map-links]'); links.replaceChildren();
      const pairs = key === 'royalty' ? [['king', 'queen'], ['man', 'woman']]
        : key === 'capital' ? [['france', 'paris'], ['india', 'delhi']]
        : key === 'food' ? [['banana', 'grape'], ['banana', 'aeroplane']] : [];
      pairs.forEach(([a, b], i) => {
        const [x1, y1] = position(a), [x2, y2] = position(b);
        links.append(svgNode('line', { x1, y1, x2, y2, class: `vector-map-link vector-map-link--${i}`, 'marker-end': 'url(#word-map-arrow)' }));
      });
      map.querySelector('[data-map-explanation]').textContent = descriptions[key];
    }
    map.querySelectorAll('[data-map-pair]').forEach(button => button.addEventListener('click', () => {
      selectButton(map, '[data-map-pair]', button); draw(button.dataset.mapPair);
    }));
  }
  const similarity = document.querySelector('.similarity-demo');
  if (similarity) {
    const a = similarity.querySelector('#similarity-a'), b = similarity.querySelector('#similarity-b');
    function updateSimilarity() {
      const result = compareSentences(a.value, b.value);
      similarity.querySelector('[data-similarity-score]').textContent = result.score === null ? '—' : result.score.toFixed(3);
      similarity.querySelector('[data-similarity-fill]').style.width = `${(result.score || 0) * 100}%`;
      similarity.querySelector('[data-similarity-explanation]').textContent = result.score === null ? 'Type some words in both boxes so we can compare them.'
        : result.score > .999 ? 'These demo vectors point the same way. The sentences have the same balance of word groups.'
        : result.score === 0 ? 'The sentences share no word groups in this demo. A trained model may still find a connection.'
        : 'The sentences share some word groups. A higher score does not mean they agree or answer the same question.';
      const table = make('table');
      const head = make('tr'); ['Word group / literal word', 'A', 'B'].forEach(text => head.append(make('th', text))); table.append(head);
      result.features.forEach(feature => {
        const row = make('tr'); [feature, result.left.get(feature) || 0, result.right.get(feature) || 0].forEach(text => row.append(make('td', String(text)))); table.append(row);
      });
      similarity.querySelector('[data-similarity-vectors]').replaceChildren(table);
    }
    [a, b].forEach(input => input.addEventListener('input', () => {
      similarity.querySelectorAll('[data-similarity-preset]').forEach(button => button.setAttribute('aria-pressed', 'false')); updateSimilarity();
    }));
    similarity.querySelectorAll('[data-similarity-preset]').forEach(button => button.addEventListener('click', () => {
      [a.value, b.value] = sentencePresets[button.dataset.similarityPreset];
      selectButton(similarity, '[data-similarity-preset]', button); updateSimilarity();
    }));
    updateSimilarity();
  }
  const chunking = document.querySelector('.chunking-demo');
  if (chunking) {
    const size = chunking.querySelector('#chunk-size'), overlap = chunking.querySelector('#chunk-overlap');
    const notices = {
      fixed: 'Fixed size counts characters, even inside a word. Add overlap to repeat text around the boundary, then compare the total stored characters.',
      recursive: 'Try paragraph boundaries first, then sentence endings, then spaces. If a single word exceeds the limit, a hard cut is still necessary. This demo uses no overlap for this strategy.',
      semantic: 'This sample uses topic keywords to group adjacent sentences into Travel, Weather, and Food. Headings are removed. Real semantic chunkers use meaning comparisons and may choose different boundaries.',
      structure: 'Split at the guide’s ## headings and keep each heading with its content. The document title stays with the first section. A long section would still need smaller chunks.',
    };
    let strategy = 'fixed';
    chunking.querySelector('[data-chunk-source]').textContent = chunkSource;
    function updateChunks() {
      const budget = Number(size.value), repeat = Number(overlap.value);
      const chunks = strategy === 'fixed' ? fixedChunks(chunkSource, budget, repeat)
        : strategy === 'recursive' ? recursiveChunks(chunkSource, budget)
        : strategy === 'semantic' ? semanticChunks(chunkSource) : structureChunks(chunkSource);
      chunking.querySelector('[data-chunk-size-controls]').hidden = !['fixed', 'recursive'].includes(strategy);
      chunking.querySelector('[data-chunk-overlap-controls]').hidden = strategy !== 'fixed';
      chunking.querySelector('[data-chunk-size-label]').textContent = budget;
      chunking.querySelector('[data-chunk-overlap-label]').textContent = repeat;
      chunking.querySelector('[data-chunk-notice]').textContent = notices[strategy];
      const midWord = chunks.filter(chunk => chunk.start !== undefined && (cutsWord(chunkSource, chunk.start) || cutsWord(chunkSource, chunk.end))).length;
      const total = chunks.reduce((sum, chunk) => sum + chunk.text.length, 0);
      chunking.querySelector('[data-chunk-stats]').textContent = `${chunks.length} chunks · ${Math.round(total / chunks.length)} average characters · ${total} total characters${['fixed', 'recursive'].includes(strategy) ? ` · ${midWord} chunks with a mid-word boundary` : ''}`;
      const cards = chunking.querySelector('[data-chunk-cards]'); cards.replaceChildren();
      chunks.forEach((chunk, i) => {
        const card = make('div', undefined, 'chunking-demo__card');
        card.append(make('h4', `Chunk ${i + 1}${chunk.topic ? ` · ${chunk.topic}` : ''}`));
        const text = make('p');
        if (chunk.repeated) text.append(make('span', chunk.text.slice(0, chunk.repeated), 'chunking-demo__repeated'));
        text.append(document.createTextNode(chunk.text.slice(chunk.repeated)));
        card.append(text, make('span', `${chunk.text.length} characters${chunk.repeated ? ` · ${chunk.repeated} repeated` : ''}`, 'embedding-demo__note'));
        if (chunk.start !== undefined && (cutsWord(chunkSource, chunk.start) || cutsWord(chunkSource, chunk.end))) card.append(make('strong', 'Mid-word boundary', 'chunking-demo__warning'));
        cards.append(card);
      });
    }
    [size, overlap].forEach(input => input.addEventListener('input', updateChunks));
    chunking.querySelectorAll('[data-chunk-strategy]').forEach(button => button.addEventListener('click', () => {
      strategy = button.dataset.chunkStrategy; selectButton(chunking, '[data-chunk-strategy]', button); updateChunks();
    }));
    updateChunks();
  }
  const demo = document.querySelector('.cosine-demo');
  if (!demo) return;
  const input = demo.querySelector('#cosine-angle');
  const angleLabel = demo.querySelector('#cosine-angle-label');
  const score = demo.querySelector('#cosine-score');
  const arrow = demo.querySelector('[data-cosine-arrow]');
  const explanation = demo.querySelector('#cosine-explanation');
  function update() {
    const angle = Number(input.value);
    angleLabel.textContent = `${angle}°`;
    score.textContent = Math.cos(angle * Math.PI / 180).toFixed(3);
    arrow.setAttribute('transform', `rotate(${-angle} 150 145)`);
    explanation.textContent = angle === 0 ? 'Same direction: cosine similarity is 1.'
      : angle === 90 ? 'A right angle: cosine similarity is 0.'
      : angle === 180 ? 'Opposite directions: cosine similarity is −1.'
      : angle < 90 ? 'A smaller angle gives a higher similarity.'
      : 'Beyond 90°, the cosine is negative.';
    demo.querySelectorAll('[data-cosine-angle]').forEach(button => {
      button.setAttribute('aria-pressed', String(Number(button.dataset.cosineAngle) === angle));
    });
  }
  input.addEventListener('input', update);
  demo.querySelectorAll('[data-cosine-angle]').forEach(button => {
    button.addEventListener('click', () => { input.value = button.dataset.cosineAngle; update(); });
  });
  update();
})();
