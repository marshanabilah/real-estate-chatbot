import assert from 'node:assert/strict';

import { formatSegments } from '../app/static/format.mjs';

assert.deepEqual(formatSegments('A **bold** choice'), [
  { type: 'text', value: 'A ' },
  { type: 'strong', value: 'bold' },
  { type: 'text', value: ' choice' },
]);
assert.deepEqual(formatSegments('An **unfinished marker'), [
  { type: 'text', value: 'An **unfinished marker' },
]);
console.log('formatSegments tests passed');
