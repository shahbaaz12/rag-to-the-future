const assert = require('node:assert/strict');
const { test } = require('node:test');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const vm = require('node:vm');
const source = readFileSync(resolve(__dirname, '../temporal-ui.js'), 'utf8');

function load(counts) {
  const labels = [[1, 8], [9, 16], [17, 20]].map(([start, end]) => ({ dataset: { start, end } }));
  const attributes = {};
  const styles = {};
  const image = { setAttribute: (name, value) => { image[name] = value; } };
  const track = {
    style: { setProperty: (name, value) => { styles[name] = value; } },
    setAttribute: (name, value) => { attributes[name] = value; },
    querySelector: () => image,
  };
  const events = {};
  const document = {
    querySelectorAll: selector => selector === '[data-route-count]' ? labels : selector === '[data-route-progress]' ? [track] : [],
  };
  const window = {
    CourseProgress: { count: start => counts[start === 1 ? 0 : start === 9 ? 1 : 2] },
    addEventListener: (name, handler) => { events[name] = handler; },
  };
  vm.runInNewContext(source, { window, document });
  return { image, labels, attributes, styles, refresh: events['course-progress-change'] };
}

test('empty progress shows one car at the start of the shared track', () => {
  const state = load([0, 0, 0]);
  assert.equal(state.image.src, 'assets/progress-car.svg');
  assert.equal(state.styles['--route-progress'], '0%');
  assert.deepEqual(state.labels.map(label => label.textContent), ['0 / 8', '0 / 8', '0 / 4']);
});

test('vehicle changes at both workshop boundaries', () => {
  for (const [counts, vehicle, percent] of [
    [[7, 0, 0], 'car', 29.166666666666668],
    [[8, 0, 0], 'flying-car', 33.33333333333333],
    [[8, 7, 0], 'flying-car', 62.5],
    [[8, 8, 0], 'train', 66.66666666666666],
  ]) {
    const state = load(counts);
    assert.equal(state.image.src, `assets/progress-${vehicle}.svg`);
    assert.ok(Math.abs(parseFloat(state.styles['--route-progress']) - percent) < 0.00001);
  }
});

test('frontier lessons advance by quarters of the final segment', () => {
  const state = load([8, 8, 1]);
  assert.equal(state.styles['--route-progress'], '75%');
  assert.equal(state.attributes['aria-valuetext'], '17 of 20 lessons complete');
});

test('all published lessons put the train at the endpoint', () => {
  const state = load([8, 8, 4]);
  assert.equal(state.image.src, 'assets/progress-train.svg');
  assert.equal(state.styles['--route-progress'], '100%');
  assert.equal(state.attributes['aria-valuenow'], '100');
});

test('undo refreshes position and changes the same marker back across a boundary', () => {
  const counts = [8, 8, 0];
  const state = load(counts);
  counts[1] = 7;
  state.refresh();
  assert.equal(state.image.src, 'assets/progress-flying-car.svg');
  assert.equal(state.styles['--route-progress'], '62.5%');
  assert.equal(state.labels[1].textContent, '7 / 8');
});
