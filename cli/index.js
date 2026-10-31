#!/usr/bin/env node
'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');

const PACKAGE_ROOT = path.resolve(__dirname, '..');
const PACKAGE_JSON_PATH = path.join(PACKAGE_ROOT, 'package.json');
const API_VERSION = '2022-11-28';
const SKIP_NAMES = new Set(['.DS_Store', 'Thumbs.db']);

function printHelp() {
  console.log(`AI Dev Assistant installer

Usage:
  ai-dev-assistant list [--repo OWNER/REPO] [--ref BRANCH]
  ai-dev-assistant install <feature-id> [feature-id ...] [options]
  ai-dev-assistant install --all [options]

Options:
  --repo OWNER/REPO   GitHub repository containing the toolkit
  --ref REF           Branch, tag, or commit (default: package release ref)
  --target PATH       Destination project (default: current directory)
  --all               Install every feature in the manifest
  --overwrite         Replace files that already exist
  --dry-run           Preview the files without writing them
  --help              Show this help

Authentication for private repositories:
  Set GITHUB_TOKEN or GH_TOKEN to a GitHub token with Contents: read access.

Examples:
  ai-dev-assistant list
  ai-dev-assistant install drawio-diagram-generator
  ai-dev-assistant install log-analyzer code-review
  ai-dev-assistant install --all --dry-run
`);
}

function parseArgs(argv) {
  const args = [...argv];
  const command = args.shift();
  const options = {
    features: [],
    all: false,
    overwrite: false,
    dryRun: false,
    target: process.cwd(),
    repo: null,
    ref: null,
    help: false,
  };

  while (args.length) {
    const token = args.shift();
    if (token === '--help' || token === '-h') options.help = true;
    else if (token === '--all') options.all = true;
    else if (token === '--overwrite') options.overwrite = true;
    else if (token === '--dry-run') options.dryRun = true;
    else if (token === '--repo') options.repo = requireValue(args, token);
    else if (token === '--ref') options.ref = requireValue(args, token);
    else if (token === '--target') options.target = requireValue(args, token);
    else if (token.startsWith('--')) throw new Error(`Unknown option: ${token}`);
    else options.features.push(token);
  }

  return { command, options };
}

function requireValue(args, option) {
  const value = args.shift();
  if (!value || value.startsWith('--')) throw new Error(`Option ${option} requires a value.`);
  return value;
}

function repositoryFromPackage(packageJson) {
  const configured = packageJson.aiDevAssistant?.repository;
  if (configured && !configured.includes('YOUR_GITHUB_ORG')) return configured;

  const repository = packageJson.repository;
  const url = typeof repository === 'string' ? repository : repository?.url;
  if (!url || url.includes('YOUR_GITHUB_ORG')) return null;

  const normalized = url
    .replace(/^git\+/, '')
    .replace(/\.git$/, '')
    .replace(/^git@github\.com:/, 'https://github.com/')
    .replace(/^ssh:\/\/git@github\.com\//, 'https://github.com/');
  const match = normalized.match(/(?:https?:\/\/github\.com\/)?([^/]+\/[^/]+)$/i);
  return match ? match[1] : null;
}

function normalizeRepository(value) {
  if (!value || typeof value !== 'string') {
    throw new Error('GitHub repository is not configured. Set it in package.json or pass --repo OWNER/REPO.');
  }
  const cleaned = value
    .trim()
    .replace(/^git\+/, '')
    .replace(/\.git$/, '')
    .replace(/^git@github\.com:/, '')
    .replace(/^ssh:\/\/git@github\.com\//, '')
    .replace(/^https?:\/\/github\.com\//, '');
  const match = cleaned.match(/^([A-Za-z0-9-]+)\/([A-Za-z0-9_.-]+)$/);
  if (!match) throw new Error(`Invalid GitHub repository '${value}'. Expected OWNER/REPO.`);
  return { owner: match[1], repo: match[2], slug: `${match[1]}/${match[2]}` };
}

function safeRepoPath(repoPath, label) {
  if (typeof repoPath !== 'string' || !repoPath.trim()) {
    throw new Error(`Invalid ${label} path in feature manifest.`);
  }
  const normalized = repoPath.replace(/\\/g, '/');
  if (normalized.startsWith('/') || /^[A-Za-z]:/.test(normalized)) {
    throw new Error(`Unsafe ${label} path in feature manifest: ${repoPath}`);
  }
  const segments = normalized.split('/');
  if (segments.some((segment) => !segment || segment === '.' || segment === '..')) {
    throw new Error(`Unsafe ${label} path in feature manifest: ${repoPath}`);
  }
  return segments.join('/');
}

function resolveInside(root, relativePath) {
  const resolvedRoot = path.resolve(root);
  const resolvedPath = path.resolve(resolvedRoot, ...relativePath.split('/'));
  const rootPrefix = resolvedRoot.endsWith(path.sep) ? resolvedRoot : resolvedRoot + path.sep;
  if (resolvedPath === resolvedRoot || !resolvedPath.startsWith(rootPrefix)) {
    throw new Error(`Path escapes the target project: ${relativePath}`);
  }
  return resolvedPath;
}

function createGitHubClient({ owner, repo, ref, token, apiBaseUrl }) {
  const base = (apiBaseUrl || 'https://api.github.com').replace(/\/$/, '');
  const repositoryApi = `${base}/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`;

  async function request(url, accept) {
    const headers = {
      Accept: accept,
      'X-GitHub-Api-Version': API_VERSION,
      'User-Agent': 'ai-dev-assistant-installer',
    };
    if (token) headers.Authorization = `Bearer ${token}`;

    let response;
    try {
      response = await fetch(url, { headers });
    } catch (error) {
      throw new Error(`Could not connect to GitHub: ${error.message}`);
    }
    if (!response.ok) {
      const detail = await response.text().catch(() => '');
      if (response.status === 401 || response.status === 403) {
        throw new Error(`GitHub denied access (${response.status}). Check repository permissions and GITHUB_TOKEN/GH_TOKEN. ${detail}`.trim());
      }
      if (response.status === 404) {
        throw new Error(`GitHub resource not found: ${url}. Check the repository, ref, and file path.`);
      }
      throw new Error(`GitHub request failed (${response.status}): ${detail || response.statusText}`);
    }
    return response;
  }

  function contentUrl(repoPath) {
    const encodedPath = repoPath.split('/').map(encodeURIComponent).join('/');
    return `${repositoryApi}/contents/${encodedPath}?ref=${encodeURIComponent(ref)}`;
  }

  return {
    async getManifest() {
      const response = await request(contentUrl('manifest/features.json'), 'application/vnd.github.raw+json');
      const content = await response.text();
      try {
        return JSON.parse(content);
      } catch {
        throw new Error('The feature manifest in GitHub is not valid JSON.');
      }
    },
    async listDirectory(repoPath) {
      const response = await request(contentUrl(repoPath), 'application/vnd.github+json');
      const items = await response.json();
      if (!Array.isArray(items)) throw new Error(`Expected a directory listing for ${repoPath}.`);
      return items;
    },
    async getFile(repoPath) {
      const response = await request(contentUrl(repoPath), 'application/vnd.github.raw+json');
      return Buffer.from(await response.arrayBuffer());
    },
  };
}

async function listFeatures(client) {
  const manifest = await client.getManifest();
  if (!manifest.features || typeof manifest.features !== 'object') {
    throw new Error('The feature manifest is missing its features map.');
  }
  for (const [id, feature] of Object.entries(manifest.features)) {
    console.log(`${id.padEnd(29)} ${feature.description || ''}`);
  }
}

async function installFeature({ client, featureId, feature, target, overwrite, dryRun }) {
  if (!Array.isArray(feature.files)) throw new Error(`Feature '${featureId}' has no valid files list.`);
  let copied = 0;
  let skipped = 0;

  console.log(`\n[${featureId}] ${feature.description || ''}`);

  async function installFile(sourcePath, destinationPath) {
    const safeSource = safeRepoPath(sourcePath, 'source');
    const safeDestination = safeRepoPath(destinationPath, 'destination');
    const absoluteDestination = resolveInside(target, safeDestination);

    if (!overwrite) {
      try {
        await fs.access(absoluteDestination);
        console.log(`  SKIP existing: ${safeDestination}`);
        skipped += 1;
        return;
      } catch (error) {
        if (error.code !== 'ENOENT') throw error;
      }
    }

    console.log(`  ${dryRun ? 'WOULD COPY' : 'COPY'}: ${safeSource} -> ${safeDestination}`);
    if (!dryRun) {
      const bytes = await client.getFile(safeSource);
      await fs.mkdir(path.dirname(absoluteDestination), { recursive: true });
      await fs.writeFile(absoluteDestination, bytes);
    }
    copied += 1;
  }

  async function installDirectory(sourceDir, destinationDir) {
    const safeSourceDir = safeRepoPath(sourceDir, 'source');
    const safeDestinationDir = safeRepoPath(destinationDir, 'destination');
    const entries = await client.listDirectory(safeSourceDir);

    for (const entry of entries) {
      if (entry.type === 'dir') {
        await installDirectory(entry.path, `${safeDestinationDir}/${entry.name}`);
      } else if (entry.type === 'file') {
        if (SKIP_NAMES.has(entry.name) || entry.name.endsWith('.pyc') || entry.name.endsWith('.pyo')) continue;
        if (entry.name === '.gitkeep') continue;
        await installFile(entry.path, `${safeDestinationDir}/${entry.name}`);
      } else if (entry.type === 'symlink' || entry.type === 'submodule') {
        console.log(`  SKIP unsupported ${entry.type}: ${entry.path}`);
      }
    }
  }

  for (const entry of feature.files) {
    const source = safeRepoPath(entry.source, 'source');
    const destination = safeRepoPath(entry.destination, 'destination');
    if (entry.kind === 'file') {
      await installFile(source, destination);
    } else if (entry.kind === 'directory') {
      await installDirectory(source, destination);
    } else {
      throw new Error(`Unknown manifest entry kind '${entry.kind}' for ${source}.`);
    }
  }

  return { copied, skipped };
}

async function main(argv = process.argv.slice(2)) {
  const { command, options } = parseArgs(argv);
  if (options.help || command === 'help' || command === '--help' || command === '-h' || !command) {
    printHelp();
    return 0;
  }
  if (!['list', 'install'].includes(command)) {
    throw new Error(`Unknown command '${command}'. Run 'ai-dev-assistant --help'.`);
  }

  const packageJson = JSON.parse(await fs.readFile(PACKAGE_JSON_PATH, 'utf8'));
  const repository = normalizeRepository(options.repo || process.env.AI_DEV_ASSISTANT_REPOSITORY || repositoryFromPackage(packageJson));
  const ref = options.ref || process.env.AI_DEV_ASSISTANT_REF || packageJson.aiDevAssistant?.ref || 'main';
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || null;
  const client = createGitHubClient({
    ...repository,
    ref,
    token,
  });

  if (command === 'list') {
    await listFeatures(client);
    return 0;
  }

  if (options.all && options.features.length) throw new Error('Use --all or feature IDs, not both.');
  if (!options.all && !options.features.length) throw new Error('Choose --all or provide one or more feature IDs.');

  const target = path.resolve(options.target);
  const stat = await fs.stat(target).catch(() => null);
  if (!stat?.isDirectory()) throw new Error(`Target directory must already exist: ${target}`);
  const manifest = await client.getManifest();
  const featureMap = manifest.features;
  if (!featureMap || typeof featureMap !== 'object') throw new Error('The feature manifest is missing its features map.');
  const selected = options.all ? Object.keys(featureMap) : [...new Set(options.features)];

  for (const featureId of selected) {
    if (!Object.prototype.hasOwnProperty.call(featureMap, featureId)) {
      throw new Error(`Unknown feature '${featureId}'. Run 'ai-dev-assistant list' to see valid feature IDs.`);
    }
  }

  let totalCopied = 0;
  let totalSkipped = 0;
  for (const featureId of selected) {
    const result = await installFeature({
      client,
      featureId,
      feature: featureMap[featureId],
      target,
      overwrite: options.overwrite,
      dryRun: options.dryRun,
    });
    totalCopied += result.copied;
    totalSkipped += result.skipped;
  }

  console.log(`\nCompleted. ${options.dryRun ? 'Would copy' : 'Copied'}: ${totalCopied}; skipped: ${totalSkipped}.`);
  if (!options.dryRun) console.log('Review the changed files and commit them through your normal code-review process.');
  return 0;
}

if (require.main === module) {
  main().then((code) => {
    process.exitCode = code;
  }).catch((error) => {
    console.error(`\nError: ${error.message}`);
    process.exitCode = 1;
  });
}

module.exports = {
  main,
  normalizeRepository,
  repositoryFromPackage,
  safeRepoPath,
  resolveInside,
  createGitHubClient,
  installFeature,
  parseArgs,
};
