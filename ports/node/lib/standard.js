'use strict';
/*
 * SmartStandard — native Node port.
 * Reproduces smartstandard.core.standard()/conformance(): the deterministic
 * SHA-256 standard hash and the 4-rule conformance score/drift. Zero deps.
 */
const crypto = require('crypto'), fs = require('fs'), path = require('path');
const IDS = ['STD-README', 'STD-SMARTJSON', 'STD-LICENSE', 'STD-TESTS'];

function standard() {
  const h = crypto.createHash('sha256').update(IDS.join(',')).digest('hex').slice(0, 12);
  return { id: 'iaiso-baseline', rules: IDS, hash: 'sha256:' + h };
}
const exists = p => { try { fs.accessSync(p); return true; } catch { return false; } };
const isdir = p => { try { return fs.statSync(p).isDirectory(); } catch { return false; } };
function conformance(root) {
  const checks = {
    'STD-README': exists(path.join(root, 'README.md')),
    'STD-SMARTJSON': exists(path.join(root, '.smart.json')),
    'STD-LICENSE': exists(path.join(root, 'LICENSE')),
    'STD-TESTS': isdir(path.join(root, 'tests')),
  };
  const drift = IDS.filter(k => !checks[k]);
  const present = IDS.filter(k => checks[k]).length;
  return { score: Math.round(100 * present / IDS.length), drift };
}
module.exports = { standard, conformance, IDS };
