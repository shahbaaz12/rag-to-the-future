const assert = require('node:assert/strict');
const { test } = require('node:test');
const { splitTokens, summarize } = require('../lesson-tokenizer.js');

test('reference sentence retains its twelve pieces and illustrative cost', () => {
  const state = summarize('AI Engineering is surprisingly approachable!');
  assert.equal(state.tokens, 12);
  assert.equal(state.characters, 44);
  assert.equal(state.cost, '$0.000060');
  assert.deepEqual(state.pieces.filter(piece => piece.trim()), ['AI', 'Engi', 'neer', 'ing', 'is', 'surp', 'risi', 'ngly', 'appr', 'oach', 'able', '!']);
});

test('empty input clears all counts and whitespace is preserved without billing it', () => {
  assert.deepEqual(summarize(''), { pieces: [], tokens: 0, characters: 0, cost: '$0.000000' });
  assert.deepEqual(summarize(' \n\t'), { pieces: [' \n\t'], tokens: 0, characters: 3, cost: '$0.000000' });
});

test('short words stay whole and punctuation is separate', () => {
  assert.deepEqual(splitTokens('The cat is here!'), ['The', ' ', 'cat', ' ', 'is', ' ', 'here', '!']);
  assert.equal(summarize('The cat is here!').tokens, 5);
});

test('pieces reconstruct arbitrary input including markup, line breaks and Unicode', () => {
  for (const text of ['Engineering\n12345678', '<img src=x onerror=alert(1)>', 'Hi 🙂 世界', 'a'.repeat(5000)]) {
    assert.equal(splitTokens(text).join(''), text);
  }
  assert.equal(summarize('🙂').characters, 1);
  assert.equal(summarize('🙂').tokens, 1);
});
