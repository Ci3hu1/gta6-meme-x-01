// Test for main.ts: run it with temp dirs and assert the output POST.json is
// byte-identical to the repository's POST.json.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = dirname(join(fileURLToPath(import.meta.url), '..'));
const work = mkdtempSync(join(tmpdir(), 'gta6-meme-x-01-test-'));
try {
  const outDir = join(work, 'out');
  execFileSync('node', ['main.ts'], {
    cwd: repo,
    env: { ...process.env, MAKEFUN_BOT_DIR: repo, MAKEFUN_OUTPUT_DIR: outDir },
    stdio: 'pipe',
  });
  const expected = readFileSync(join(repo, 'POST.json'));
  const actual = readFileSync(join(outDir, 'POST.json'));
  if (!expected.equals(actual)) {
    console.error('FAIL: out/POST.json differs from repo POST.json');
    process.exit(1);
  }
  console.log('PASS: out/POST.json is byte-identical to repo POST.json');
} finally {
  rmSync(work, { recursive: true, force: true });
}
