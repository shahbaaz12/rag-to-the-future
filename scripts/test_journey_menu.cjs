const assert = require('node:assert/strict');
const { test } = require('node:test');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const vm = require('node:vm');
const source = readFileSync(resolve(__dirname, '../site/temporal-ui.js'), 'utf8');

function load(lesson = 0, part = 0) {
  const labels = [[1, 8], [9, 16], [17, 21]].map(([start, end]) => ({ dataset: { start, end } }));
  const attributes = {};
  const styles = {};
  const image = { setAttribute: (name, value) => { image[name] = value; } };
  const track = {
    dataset: { currentLesson: String(lesson), currentPart: String(part) },
    style: { setProperty: (name, value) => { styles[name] = value; } },
    setAttribute: (name, value) => { attributes[name] = value; },
    querySelector: () => image,
  };
  const events = {};
  const document = {
    querySelectorAll: selector => selector === '[data-route-count]' ? labels : selector === '[data-route-progress]' ? [track] : [],
  };
  const window = {
    CourseProgress: { count: () => { throw new Error('The location tracker must not read completion counts'); } },
    addEventListener: (name, handler) => { events[name] = handler; },
  };
  vm.runInNewContext(source, { window, document });
  return { image, labels, attributes, styles, refresh: events['course-progress-change'] };
}

test('home shows the car at the course start and available lesson counts', () => {
  const state = load();
  assert.equal(state.image.src, 'assets/progress-car.svg');
  assert.equal(state.styles['--route-progress'], '0%');
  assert.deepEqual(state.labels.map(label => label.textContent), ['8 lessons', '8 lessons', '5 lessons']);
  assert.equal(state.attributes['aria-valuetext'], 'Course start');
});

test('vehicle follows the viewed lesson across workshop boundaries', () => {
  for (const [lesson, vehicle, percent] of [
    [8, 'car', 33.33333333333333],
    [9, 'flying-car', 37.5],
    [16, 'flying-car', 66.66666666666666],
    [17, 'train', 73.33333333333334],
  ]) {
    const state = load(lesson);
    assert.equal(state.image.src, `assets/progress-${vehicle}.svg`);
    assert.ok(Math.abs(parseFloat(state.styles['--route-progress']) - percent) < 0.00001);
  }
});

test('current lesson determines the local position and accessible description', () => {
  const state = load(17, 3);
  assert.ok(Math.abs(parseFloat(state.styles['--route-progress']) - 73.33333333333334) < 0.00001);
  assert.deepEqual(state.labels.map(label => label.textContent), ['8 lessons', '8 lessons', '1 / 5']);
  assert.equal(state.attributes['aria-valuetext'], 'Lesson 17, lesson 1 of 5 in Part 3');
});

test('viewing the final published lesson puts the train at the endpoint', () => {
  const state = load(21, 3);
  assert.equal(state.image.src, 'assets/progress-train.svg');
  assert.equal(state.styles['--route-progress'], '100%');
  assert.equal(state.attributes['aria-valuenow'], '100');
});

test('completion changes leave the tracker on the current lesson', () => {
  const state = load(12, 2);
  const percent = state.styles['--route-progress'];
  state.refresh();
  assert.equal(state.image.src, 'assets/progress-flying-car.svg');
  assert.equal(state.styles['--route-progress'], percent);
  assert.equal(state.labels[1].textContent, '4 / 8');
});

test('part maps place the vehicle at the start of their workshop', () => {
  for (const [part, vehicle, percent] of [[1, 'car', 0], [2, 'flying-car', 100 / 3], [3, 'train', 200 / 3]]) {
    const state = load(0, part);
    assert.equal(state.image.src, `assets/progress-${vehicle}.svg`);
    assert.ok(Math.abs(parseFloat(state.styles['--route-progress']) - percent) < 0.00001);
    assert.equal(state.attributes['aria-valuetext'], `Part ${part}`);
  }
});

test('each generated lesson supplies its current location and a visible glossary label', () => {
  for (let lesson = 1; lesson <= 21; lesson++) {
    const html = readFileSync(resolve(__dirname, `../site/lesson-${lesson}.html`), 'utf8');
    assert.ok(html.includes(`data-current-lesson="${lesson}"`), `Lesson ${lesson} location`);
    assert.ok(html.includes('class="glossary-label">Glossary</span>'), `Lesson ${lesson} glossary label`);
  }
});
