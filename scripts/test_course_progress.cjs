const assert = require('node:assert/strict');
const { test } = require('node:test');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const vm = require('node:vm');
const source = readFileSync(resolve(__dirname, '../course-progress.js'), 'utf8');
const key = 'rag-to-the-future-course-progress';
const legacyKey = 'rag-to-the-future-part-one-progress';
const structureKey = 'rag-to-the-future-course-structure-version';

function load(initial = {}, blocked = false) {
  const stored = new Map(Object.entries(initial));
  const listeners = new Map();
  const window = {
    addEventListener: (type, listener) => {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(listener);
    },
    dispatchEvent: event => (listeners.get(event.type) || []).forEach(listener => listener(event)),
  };
  const localStorage = {
    getItem: name => { if (blocked) throw Error('Blocked'); return stored.get(name) ?? null; },
    setItem: (name, value) => { if (blocked) throw Error('Blocked'); stored.set(name, value); },
  };
  class CustomEvent { constructor(type) { this.type = type; } }
  vm.runInNewContext(source, { window, localStorage, CustomEvent });
  return { progress: window.CourseProgress, stored, window };
}

test('migrates valid Part I records and excludes invalid or planned lessons', () => {
  const { progress } = load({ [legacyKey]: '["1","6",6,0,21,"bad",true,null]' });
  assert.equal(progress.count(), 2);
  assert.equal(progress.has(6), true);
  assert.equal(progress.has(21), false);
});

test('uses the new record, including an empty record, ahead of legacy data', () => {
  const { progress } = load({ [key]: '[]', [legacyKey]: '["1"]' });
  assert.equal(progress.count(), 0);
});

test('recovers the legacy record when the new value is malformed', () => {
  const { progress } = load({ [key]: '{broken', [legacyKey]: '["3"]' });
  assert.equal(progress.has(3), true);
  assert.equal(progress.isPersistent(), true);
});

test('completion and undo persist, mirror Part I, and notify instruments', () => {
  const { progress, stored, window } = load();
  let notifications = 0;
  window.addEventListener('course-progress-change', () => notifications++);
  progress.set(4, true);
  progress.set(17, true);
  progress.set(24, true);
  assert.equal(progress.count(17, 20), 1);
  assert.deepEqual(JSON.parse(stored.get(legacyKey)), ['4']);
  progress.set(4, false);
  assert.deepEqual(JSON.parse(stored.get(key)), [17]);
  assert.equal(notifications, 3);
});

test('blocked storage retains progress for the current visit', () => {
  const { progress, window } = load({}, true);
  progress.set(10, true);
  window.dispatchEvent({ type: 'pageshow' });
  assert.equal(progress.has(10), true);
  assert.equal(progress.isPersistent(), false);
});

test('storage changes and history restoration refresh the record', () => {
  const { progress, stored, window } = load();
  stored.set(key, '[9,10]');
  window.dispatchEvent({ type: 'storage', key });
  assert.equal(progress.count(9, 16), 2);
  stored.set(key, '[17]');
  window.dispatchEvent({ type: 'pageshow' });
  assert.equal(progress.count(), 1);
  assert.equal(progress.has(17), true);
});

test('moves existing Part III completions once when the PDF lesson is inserted', () => {
  const first = load({ [key]: '[1,17,18,19,20,24]' });
  assert.deepEqual(JSON.parse(first.stored.get(key)), [1,17,19,20,21]);
  assert.equal(first.progress.has(18), false);
  assert.equal(first.stored.get(structureKey), '2');
  const second = load(Object.fromEntries(first.stored));
  assert.equal(second.progress.count(), 5);
  assert.equal(second.progress.has(19), true);
  assert.equal(second.progress.has(21), true);
  second.progress.set(18, true);
  assert.equal(second.progress.count(17,21), 5);
});
