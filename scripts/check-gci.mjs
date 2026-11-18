import { readFile } from "node:fs/promises";
import assert from "node:assert/strict";
const p=new URL("../global-capital-intelligence/assets/data/assets.json",import.meta.url);
const d=JSON.parse(await readFile(p,"utf8"));
assert.equal(d.schemaVersion,1);
assert.ok(d.assets.length>100,"expected full research universe");
assert.equal(new Set(d.assets.map(a=>a.type+":"+a.symbol)).size,d.assets.length,"duplicate canonical IDs");
assert.equal(d.counts.stocks,d.assets.filter(a=>a.type==="stock").length);
assert.equal(d.counts.crypto,d.assets.filter(a=>a.type==="crypto").length);
assert.equal(d.counts.indicators,d.assets.filter(a=>a.type==="indicator").length);
for(const a of d.assets){assert.ok(a.symbol&&a.name&&a.type&&Array.isArray(a.groups)&&a.groups.length);}
assert.ok(d.assets.some(a=>a.symbol==="BINANCE:HBARUSDT"),"Hedera typo normalization missing");
console.log("GCI registry OK:",d.assets.length,"unique assets;",d.counts.stocks,"stocks;",d.counts.crypto,"crypto;",d.counts.indicators,"indicators");