// Node-side half of the trace-v1 cross-check (test_trace_contract.py calls
// this as a subprocess). Decodes the fixture with the JS reference decoder
// (lab-ui/contract/decoder.js + replay.js) and prints a JSON summary to
// stdout: first/last 8 values of every neural.trace block, plus the replay
// header and the observed being's first/last replay frame. Python compares
// this against the same fixture decoded with reference_decoder.py.
//
// Usage: node decode_fixture.mjs <fixture_dir> <contract_dir>

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [fixtureDir, contractDir] = process.argv.slice(2);
if (!fixtureDir || !contractDir) {
  console.error("usage: node decode_fixture.mjs <fixture_dir> <contract_dir>");
  process.exit(2);
}

const { loadManifest, readBlock } = await import(pathToFileURL(path.join(contractDir, "decoder.js")));
const { readReplay } = await import(pathToFileURL(path.join(contractDir, "replay.js")));

const manifestText = fs.readFileSync(path.join(fixtureDir, "manifest.json"), "utf8");
const schemaText = fs.readFileSync(path.join(contractDir, "trace-v1.schema.json"), "utf8");
const manifest = loadManifest(manifestText, schemaText);

const traceBuf = fs.readFileSync(path.join(fixtureDir, "neural.trace"));
const blocks = {};
for (const b of manifest.blocks) {
  const arr = readBlock(traceBuf, manifest, b.name);
  blocks[b.name] = {
    dtype: b.dtype,
    length: arr.length,
    first8: Array.from(arr.slice(0, 8)),
    last8: Array.from(arr.slice(-8)),
  };
}

const replayBuf = fs.readFileSync(path.join(fixtureDir, "physical.replay"));
const { header, frames } = readReplay(replayBuf, manifest.being);
const first = frames[0];
const last = frames[frames.length - 1];

console.log(JSON.stringify({
  manifest_run: manifest.run,
  manifest_count: manifest.count,
  blocks,
  replay_header: header,
  replay_n_frames: frames.length,
  replay_first_frame: { tick: first.tick, pos: first.pos, finalBrk: first.finalBrk, gear: first.gear },
  replay_last_frame: { tick: last.tick, pos: last.pos, finalBrk: last.finalBrk, gear: last.gear },
}));
