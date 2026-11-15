# Distribution

This repository is the single source of truth. The npm package contains the CLI, package metadata, README, and license; it reads `manifest/features.json` from GitHub (Contents API) and downloads only the files of the selected features into the target project. The manifest exposes six features: Log Analyzer, Logging Advisor, OCC Postman Generator, Worklog Generator / Commit Message Assistant, Code Review, and Security Checks.

## Publish

1. Set `repository.url` and `aiDevAssistant.repository` in `package.json` to the real GitHub repository.
2. Set `version` and `aiDevAssistant.ref` to the release (for example `1.0.4` and `v1.0.4`).
3. `npm test && npm run package:cli`
4. Ensure the release ref contains the updated manifest and all referenced skill/agent files, tag `v1.0.4`, create a GitHub Release, and upload `ai-dev-assistant-1.0.4.tgz`. If the release already exists, publish updates under a new version/tag rather than moving the existing tag.
5. Share the command:

```bash
npx --yes --package=https://github.com/AamenYousri/ai-dev-assistant/releases/download/v1.0.4/ai-dev-assistant-1.0.4.tgz ai-dev-assistant install log-analyzer code-review security-checks
```

Build output (`*.tgz`) is git-ignored; do not commit it.

## Update an installed feature

Run the command from the new release with `--overwrite`, then review the Git diff and keep project-specific edits. Files removed from a feature are not deleted.

Retired skills and their setup guides already copied into other projects must be removed manually after reviewing local customizations. Updating this repository does not remove files from those projects or change the feature manifest served by an existing release tag.

## Private repositories

Set `GITHUB_TOKEN` or `GH_TOKEN` (fine-grained, read-only **Contents**) in the shell. A private Release asset also needs authentication, so for a fully private toolkit publish the CLI through GitHub Packages or an internal npm registry. Never put tokens in URLs, scripts, or committed `.npmrc` files.

## Conflicts

- Existing files are skipped unless `--overwrite` is given.
- `.vscode/mcp.json` is never modified. Optional ticketing/calendar integrations must be configured and authorized separately.
