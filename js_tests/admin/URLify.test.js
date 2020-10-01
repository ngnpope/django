/* global QUnit, URLify */
'use strict';

QUnit.module('admin.URLify');

QUnit.test('empty string', (assert) => {
    assert.strictEqual(URLify('', 8, true), '');
});

QUnit.test('preserve nonessential words', (assert) => {
    assert.strictEqual(URLify('the D is silent', 15, true), 'the-d-is-silent');
});

QUnit.test('strip non-URL characters', (assert) => {
    assert.strictEqual(URLify('D#silent@', 7, true), 'dsilent');
});

QUnit.test('merge adjacent whitespace', (assert) => {
    assert.strictEqual(URLify('D   silent', 8, true), 'd-silent');
});

QUnit.test('trim trailing hyphens', (assert) => {
    assert.strictEqual(URLify('D silent always', 9, true), 'd-silent');
});

QUnit.test('non-ASCII string', (assert) => {
    assert.strictEqual(URLify('Kaupa-miða', 255, true), 'kaupa-miða');
});
