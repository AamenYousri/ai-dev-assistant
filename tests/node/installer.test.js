'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const {
  normalizeRepository,
  repositoryFromPackage,
  createGitHubClient,
  safeRepoPath,
  resolveInside,
  parseArgs,
  installFeature,
} = require('../../cli/index.js');

async function tempDir() {
  return fs.mkdtemp(path.join(os.tmpdir(), 'ai-dev-assistant-test-'));
}

test('normalizes GitHub repository forms', () => {
  assert.equal(normalizeRepository('acme/ai-dev-assistant').slug, 'acme/ai-dev-assistant');
  assert.equal(normalizeRepository('https://github.com/acme/ai-dev-assistant.git').slug, 'acme/ai-dev-assistant');
  assert.equal(normalizeRepository('git@github.com:acme/ai-dev-assistant.git').slug, 'acme/ai-dev-assistant');
});

test('reads repository from package metadata', () => {
  assert.equal(repositoryFromPackage({
    repository: { url: 'https://github.com/acme/ai-dev-assistant.git' },
    aiDevAssistant: { repository: 'YOUR_GITHUB_ORG/ai-dev-assistant' },
  }), 'acme/ai-dev-assistant');
  assert.equal(repositoryFromPackage({
    repository: { url: 'https://github.com/YOUR_GITHUB_ORG/ai-dev-assistant.git' },
    aiDevAssistant: { repository: 'YOUR_GITHUB_ORG/ai-dev-assistant' },
  }), null);
});

test('rejects unsafe manifest paths', () => {
  assert.throws(() => safeRepoPath('../outside.txt', 'source'), /Unsafe source path/);
  assert.throws(() => safeRepoPath('/absolute/path', 'destination'), /Unsafe destination path/);
  assert.throws(() => resolveInside('/tmp/project', '../outside.txt'), /Path escapes/);
  assert.equal(resolveInside(path.parse(process.cwd()).root, 'tmp/inside.txt'), path.join(path.parse(process.cwd()).root, 'tmp', 'inside.txt'));
});

test('parses install options', () => {
  const parsed = parseArgs(['install', 'log-analyzer', 'code-review', '--overwrite', '--ref', 'v1']);
  assert.equal(parsed.command, 'install');
  assert.deepEqual(parsed.options.features, ['log-analyzer', 'code-review']);
  assert.equal(parsed.options.overwrite, true);
  assert.equal(parsed.options.ref, 'v1');
});

test('copies directory contents and skips existing files by default', async () => {
  const target = await tempDir();
  const client = {
    async listDirectory(repoPath) {
      if (repoPath === '.github/skills/sample') {
        return [
          { type: 'file', name: 'SKILL.md', path: '.github/skills/sample/SKILL.md' },
          { type: 'dir', name: 'references', path: '.github/skills/sample/references' },
        ];
      }
      if (repoPath === '.github/skills/sample/references') {
        return [{ type: 'file', name: 'guide.md', path: '.github/skills/sample/references/guide.md' }];
      }
      throw new Error(`Unexpected directory ${repoPath}`);
    },
    async getFile(repoPath) {
      return Buffer.from(repoPath.endsWith('SKILL.md') ? '# sample skill\n' : 'reference text\n');
    },
  };

  const result = await installFeature({
    client,
    featureId: 'sample',
    feature: { description: 'sample feature', files: [{
      source: '.github/skills/sample',
      destination: '.github/skills/sample',
      kind: 'directory',
    }] },
    target,
    overwrite: false,
    dryRun: false,
  });

  assert.deepEqual(result, { copied: 2, skipped: 0 });
  assert.equal(await fs.readFile(path.join(target, '.github/skills/sample/SKILL.md'), 'utf8'), '# sample skill\n');
  assert.equal(await fs.readFile(path.join(target, '.github/skills/sample/references/guide.md'), 'utf8'), 'reference text\n');

  const second = await installFeature({
    client,
    featureId: 'sample',
    feature: { description: 'sample feature', files: [{
      source: '.github/skills/sample', destination: '.github/skills/sample', kind: 'directory',
    }] },
    target,
    overwrite: false,
    dryRun: false,
  });
  assert.deepEqual(second, { copied: 0, skipped: 2 });
});

test('dry run does not create files', async () => {
  const target = await tempDir();
  const client = {
    async listDirectory() {
      return [{ type: 'file', name: 'SKILL.md', path: '.github/skills/sample/SKILL.md' }];
    },
    async getFile() {
      throw new Error('getFile should not be called during dry run');
    },
  };
  const result = await installFeature({
    client,
    featureId: 'sample',
    feature: { description: '', files: [{ source: '.github/skills/sample', destination: '.github/skills/sample', kind: 'directory' }] },
    target,
    overwrite: false,
    dryRun: true,
  });
  assert.deepEqual(result, { copied: 1, skipped: 0 });
  await assert.rejects(fs.access(path.join(target, '.github/skills/sample/SKILL.md')));
});


test('GitHub client fetches a manifest, directory listing, and raw file', async (t) => {
  const requests = [];
  const server = http.createServer((request, response) => {
    requests.push({ url: request.url, accept: request.headers.accept });
    if (request.url === '/repos/acme/ai-dev-assistant/contents/manifest/features.json?ref=v1.0.3') {
      response.writeHead(200, { 'content-type': 'application/json' });
      response.end(JSON.stringify({ features: { sample: { description: 'Sample', files: [] } } }));
      return;
    }
    if (request.url === '/repos/acme/ai-dev-assistant/contents/.github/skills/sample?ref=v1.0.3') {
      response.writeHead(200, { 'content-type': 'application/json' });
      response.end(JSON.stringify([{ type: 'file', name: 'SKILL.md', path: '.github/skills/sample/SKILL.md' }]));
      return;
    }
    if (request.url === '/repos/acme/ai-dev-assistant/contents/.github/skills/sample/SKILL.md?ref=v1.0.3') {
      response.writeHead(200, { 'content-type': 'text/plain' });
      response.end('# skill from GitHub');
      return;
    }
    response.writeHead(404, { 'content-type': 'application/json' });
    response.end(JSON.stringify({ message: 'Not found' }));
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const address = server.address();
  const client = createGitHubClient({
    owner: 'acme',
    repo: 'ai-dev-assistant',
    ref: 'v1.0.3',
    apiBaseUrl: `http://127.0.0.1:${address.port}`,
  });

  const manifest = await client.getManifest();
  assert.equal(manifest.features.sample.description, 'Sample');
  const listing = await client.listDirectory('.github/skills/sample');
  assert.equal(listing[0].name, 'SKILL.md');
  const file = await client.getFile('.github/skills/sample/SKILL.md');
  assert.equal(file.toString('utf8'), '# skill from GitHub');
  assert.equal(requests.length, 3);
  assert.equal(requests[0].accept, 'application/vnd.github.raw+json');
  assert.equal(requests[1].accept, 'application/vnd.github+json');
});
