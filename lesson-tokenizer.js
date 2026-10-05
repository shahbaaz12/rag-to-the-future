/* Illustrative classroom splitter; not a provider tokenizer or billing calculator. */
(() => {
  function splitTokens(text) {
    const pieces = [];
    for (const chunk of text.match(/\s+|[^\s]+/gu) || []) {
      if (/^\s+$/u.test(chunk)) {
        pieces.push(chunk);
        continue;
      }
      for (const part of chunk.match(/[A-Za-z]+|[0-9]+|[^\sA-Za-z0-9]/gu) || []) {
        if (part.length <= 5) pieces.push(part);
        else for (let i = 0; i < part.length; i += 4) pieces.push(part.slice(i, i + 4));
      }
    }
    return pieces;
  }

  function summarize(text) {
    const pieces = splitTokens(text);
    const tokens = pieces.filter(piece => !/^\s+$/u.test(piece)).length;
    return { pieces, tokens, characters: Array.from(text).length, cost: `$${(tokens * 5 / 1e6).toFixed(6)}` };
  }

  if (typeof module !== 'undefined') module.exports = { splitTokens, summarize };
  if (typeof document === 'undefined') return;
  const playground = document.querySelector('.tokenizer-playground');
  if (!playground) return;
  const input = playground.querySelector('textarea');
  const output = playground.querySelector('[data-tokenizer-pieces]');

  function render() {
    const state = summarize(input.value);
    const fragment = document.createDocumentFragment();
    let color = 0;
    for (const piece of state.pieces) {
      if (/^\s+$/u.test(piece)) fragment.append(document.createTextNode(piece));
      else {
        const chip = document.createElement('span');
        chip.className = 'tokenizer-chip';
        chip.dataset.color = String(color++ % 5);
        chip.textContent = piece;
        fragment.append(chip);
      }
    }
    output.replaceChildren(fragment);
    playground.querySelector('[data-tokenizer-count]').textContent = state.tokens;
    playground.querySelector('[data-tokenizer-characters]').textContent = state.characters;
    playground.querySelector('[data-tokenizer-cost]').textContent = state.cost;
  }

  input.addEventListener('input', render);
  render();
})();
