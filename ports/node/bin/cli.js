#!/usr/bin/env node
'use strict';
const fs = require('fs'), path = require('path');
const { standard, conformance } = require('../lib/standard.js');
const vpath = process.argv[2] || path.join(__dirname, '..', '..', 'conformance', 'vectors.json');
const vdir = path.dirname(path.resolve(vpath));
const v = JSON.parse(fs.readFileSync(vpath, 'utf8'));
const results = v.cases.map(c => {
  if ((c.op || 'standard') === 'standard') { const s = standard(); return { name: c.name, id: s.id, hash: s.hash, rules: s.rules }; }
  const root = path.isAbsolute(c.root) ? c.root : path.join(vdir, c.root);
  return Object.assign({ name: c.name }, conformance(root));
});
process.stdout.write(JSON.stringify({ results }, null, 2) + '\n');
