// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry itself is the X post: the meme was made by the agent, posted on X
// from a public account with make.fun and the entrant's play code in its text,
// and POST.json at this repository's root names that post. This program's only
// job is to hand POST.json to the grader: it copies it from the repository
// (the bot directory) into the output directory, creating the directory first.
//
// Local check:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
// and then out/POST.json must be byte-identical to ./POST.json.

import { copyFileSync, existsSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const source = join(botDir, 'POST.json');
const target = join(outDir, 'POST.json');

function fail(message: string): never {
  console.error(`gta6-meme-x-01: ${message}`);
  process.exit(1);
}

if (!existsSync(source)) {
  fail(`POST.json not found in bot directory ${botDir}`);
}

let payload: string;
try {
  payload = readFileSync(source, 'utf8');
  JSON.parse(payload);
} catch (err) {
  fail(`POST.json in ${botDir} is not valid JSON: ${(err as Error).message}`);
}

try {
  mkdirSync(outDir, { recursive: true });
  copyFileSync(source, target);
} catch (err) {
  fail(`could not write POST.json to ${outDir}: ${(err as Error).message}`);
}

console.log(`gta6-meme-x-01: copied POST.json (${payload.length} bytes) to ${target}`);
