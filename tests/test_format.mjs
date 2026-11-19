import assert from 'node:assert/strict';

import { formatBlocks, formatSegments } from '../app/static/format.mjs';

assert.deepEqual(formatSegments('A **bold** choice'), [
  { type: 'text', value: 'A ' },
  { type: 'strong', value: 'bold' },
  { type: 'text', value: ' choice' },
]);
assert.deepEqual(formatSegments('An **unfinished marker'), [
  { type: 'text', value: 'An **unfinished marker' },
]);
assert.deepEqual(formatBlocks('A short introduction\n\n- **Villa One** — SAR 1M\n- Villa Two — SAR 2M'), [
  { type: 'paragraph', value: 'A short introduction' },
  { type: 'list', items: ['**Villa One** — SAR 1M', 'Villa Two — SAR 2M'] },
]);
console.log('formatSegments tests passed');
