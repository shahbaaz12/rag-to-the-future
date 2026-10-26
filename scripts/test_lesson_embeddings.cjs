const assert = require('node:assert/strict');
const { test } = require('node:test');
const demo = require('../site/lesson-embeddings.js');

test('equations compute coordinates and find the matching toy word', () => {
  for (const [key, expected] of Object.entries({ royalty: 'queen', india: 'delhi', germany: 'berlin', tense: 'running' })) {
    const result = demo.analogy(key);
    assert.equal(result.answer, expected);
    assert.deepEqual(result.vector, demo.wordVectors[expected]);
  }
});

test('sentence comparison is cosine, symmetric and unchanged by vector length', () => {
  assert.ok(Math.abs(demo.compareSentences('cat sleep', 'kitten napping').score - 1) < 1e-12);
  assert.ok(Math.abs(demo.compareSentences('cat sleep', 'cat cat sleep sleep').score - 1) < 1e-12);
  const forward = demo.compareSentences('cat sleep sofa', 'cat');
  const reverse = demo.compareSentences('cat', 'cat sleep sofa');
  assert.ok(Math.abs(forward.score - 1 / Math.sqrt(3)) < 1e-12);
  assert.equal(forward.score, reverse.score);
  assert.equal(demo.compareSentences('cat sleep', 'stock market').score, 0);
});

test('empty vectors have no cosine, and negation stays visible as a separate feature', () => {
  assert.equal(demo.compareSentences('', 'cat').score, null);
  assert.equal(demo.compareSentences('the is a', 'cat').score, null);
  const result = demo.compareSentences('cat asleep', 'cat not asleep');
  assert.ok(result.score > .8 && result.score < 1);
  assert.equal(result.right.get('not'), 1);
  assert.ok(Math.abs(demo.compareSentences('नमस्ते', 'नमस्ते').score - 1) < 1e-12);
});

test('fixed chunks preserve the source and duplicate only the configured overlap', () => {
  const source = demo.chunkSource;
  for (const size of [40, 80, 120, 240]) {
    for (const overlap of [0, 10, 30]) {
      const chunks = demo.fixedChunks(source, size, overlap);
      assert.equal(chunks.map(chunk => chunk.text.slice(chunk.repeated)).join(''), source);
      assert.ok(chunks.every(chunk => chunk.text.length <= size));
      for (let i = 1; i < chunks.length; i++) {
        assert.equal(chunks[i].start, chunks[i - 1].end - overlap);
        assert.equal(chunks[i].text.slice(0, overlap), chunks[i - 1].text.slice(-overlap || chunks[i - 1].text.length));
      }
    }
  }
});

test('boundary cuts keep all text within budget and avoid breaking normal words', () => {
  for (const size of [40, 80, 120, 240]) {
    const chunks = demo.recursiveChunks(demo.chunkSource, size);
    assert.equal(chunks.map(chunk => chunk.text).join(''), demo.chunkSource);
    assert.ok(chunks.every(chunk => chunk.text.length <= size));
    assert.ok(chunks.every(chunk => !demo.cutsWord(demo.chunkSource, chunk.end)));
  }
  const longWord = 'x'.repeat(100);
  const chunks = demo.recursiveChunks(longWord, 40);
  assert.equal(chunks.map(chunk => chunk.text).join(''), longWord);
  assert.ok(chunks.some(chunk => demo.cutsWord(longWord, chunk.end)));
  assert.deepEqual(demo.fixedChunks('', 40), []);
  assert.deepEqual(demo.recursiveChunks('', 40), []);
});

test('topic and structure demos show three groups without losing source sentences', () => {
  const semantic = demo.semanticChunks(demo.chunkSource);
  assert.deepEqual(semantic.map(chunk => chunk.topic), ['Travel', 'Weather', 'Food']);
  const body = demo.chunkSource.replace(/^#+[^\n]*$/gm, '').replace(/\s+/g, ' ').trim();
  assert.equal(semantic.map(chunk => chunk.text).join(' '), body);
  const structure = demo.structureChunks(demo.chunkSource);
  assert.equal(structure.length, 3);
  assert.equal(structure.map(chunk => chunk.text).join(''), demo.chunkSource);
  for (const [i, title] of ['Travel', 'Weather', 'Food'].entries()) assert.ok(structure[i].text.includes(`## ${title}`));
});
