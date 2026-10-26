const assert = require('node:assert/strict');
const { test } = require('node:test');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const vm = require('node:vm');
const source = readFileSync(resolve(__dirname, '../site/lesson-reading.js'), 'utf8');

function load({ completed = false, visibility = 'visible', observation = true, endPresent = true } = {}) {
  const observers = [];
  const events = new Map();
  const changes = [];
  const end = { dataset: { lessonEnd: '17' }, top: 900, getBoundingClientRect() { return { top: this.top }; } };
  class IntersectionObserver {
    constructor(callback, options) { this.callback = callback; this.options = options; this.targets = []; observers.push(this); }
    observe(target) { this.targets.push(target); }
    disconnect() { this.disconnected = true; }
  }
  const document = {
    visibilityState: visibility,
    querySelector(selector) {
      if (selector === '[data-lesson-end]') return endPresent ? end : null;
      if (selector === '.era-route') return { getBoundingClientRect: () => ({ height: 100 }) };
      return null;
    },
    addEventListener: (name, listener) => events.set(name, listener),
    removeEventListener: name => events.delete(name),
  };
  const window = {
    CourseProgress: { has: () => completed, set: (lesson, checked) => { changes.push([lesson, checked]); completed = checked; } },
    addEventListener: (name, listener) => events.set(name, listener),
  };
  if (observation) window.IntersectionObserver = IntersectionObserver;
  vm.runInNewContext(source, { window, document, IntersectionObserver, innerHeight: 700, matchMedia: () => ({ matches: false, addEventListener() {} }) });
  return { observers, events, end, document, changes, progress: window.CourseProgress };
}

test('does not complete when only the earlier teaching sections are visible', () => {
  const { observers, changes } = load();
  const endObserver = observers.find(observer => observer.targets.length);
  endObserver.callback([{ isIntersecting: false }]);
  assert.deepEqual(changes, []);
});

test('records reaching the end once and allows subsequent manual undo', () => {
  const { observers, changes, progress } = load();
  const endObserver = observers.find(observer => observer.targets.length);
  assert.equal(endObserver.options.rootMargin, '0px 0px -16px 0px');
  endObserver.callback([{ isIntersecting: true }]);
  endObserver.callback([{ isIntersecting: true }]);
  assert.deepEqual(changes, [['17', true]]);
  assert.equal(endObserver.disconnected, true);
  progress.set('17', false);
  endObserver.callback([{ isIntersecting: true }]);
  assert.equal(progress.has('17'), false);
  assert.deepEqual(changes, [['17', true], ['17', false]]);
});

test('an unseen background page waits until it becomes visible', () => {
  const { observers, document, events, changes } = load({ visibility: 'hidden' });
  observers.find(observer => observer.targets.length).callback([{ isIntersecting: true }]);
  assert.deepEqual(changes, []);
  document.visibilityState = 'visible';
  events.get('visibilitychange')();
  assert.deepEqual(changes, [['17', true]]);
});

test('previously completed lessons and pages without a lesson end are not observed again', () => {
  for (const options of [{ completed: true }, { endPresent: false }]) {
    const { observers, changes } = load(options);
    assert.equal(observers.some(observer => observer.targets.length), false);
    assert.deepEqual(changes, []);
  }
});

test('fallback records only when the lesson end is inside the viewport', () => {
  const { events, end, changes } = load({ observation: false });
  end.top = 700;
  events.get('scroll')();
  assert.deepEqual(changes, []);
  end.top = 650;
  events.get('scroll')();
  assert.deepEqual(changes, [['17', true]]);
  events.get('scroll')();
  assert.equal(changes.length, 1);
});
