"""Draft-backed, key-free token simulation adapted from the linked classroom demo."""


def tokenizer_playground():
    pieces = ['AI', 'Engi', 'neer', 'ing', 'is', 'surp', 'risi', 'ngly', 'appr', 'oach', 'able', '!']
    chips = ''.join(f'<span class="tokenizer-chip" data-color="{i % 5}">{piece}</span>' for i, piece in enumerate(pieces))
    return f'''<section class="tokenizer-playground" id="tokenizer-playground" aria-labelledby="tokenizer-title">
      <header class="tokenizer-header"><h3 id="tokenizer-title"><span class="tokenizer-live">Live sim</span> Tokenizer playground</h3>
      <p>type → watch it split into tokens</p></header>
      <div class="tokenizer-body"><label for="tokenizer-input">Your text</label>
      <textarea id="tokenizer-input" rows="3" maxlength="5000" aria-describedby="tokenizer-note">AI Engineering is surprisingly approachable!</textarea>
      <div class="tokenizer-pieces" data-tokenizer-pieces aria-label="Illustrative token pieces">{chips}</div>
      <dl class="tokenizer-stats" aria-live="polite" aria-atomic="true">
      <div><dt>Tokens</dt><dd data-tokenizer-count>12</dd></div>
      <div><dt>Characters</dt><dd data-tokenizer-characters>44</dd></div>
      <div><dt>Cost @ $5/1M tok</dt><dd data-tokenizer-cost>$0.000060</dd></div></dl>
      <p id="tokenizer-note" class="tokenizer-note">Notice: in this simulation, common short words stay whole; long words get chopped into pieces.
      <strong>Rough rule for English: 1 token ≈ ¾ of a word ≈ 4 characters.</strong></p>
      <p class="tokenizer-disclaimer">Illustrative splitter, not a model’s tokenizer. Exact splits and counts depend on the model; the cost uses an example rate.</p>
      <noscript><p>Enable JavaScript to update the split as you type. The example above remains available.</p></noscript>
      </div></section>'''
