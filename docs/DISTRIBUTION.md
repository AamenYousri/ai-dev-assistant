# Distribution

This repository is the single source of truth. The npm package is a small CLI (`cli/**` only); it reads `manifest/features.json` from GitHub (Contents API) and downloads only the files of the selected features into the target project.

## Publish

1. Set `repository.url` and `aiDevAssistant.repository` in `package.json` to the real GitHub repository.
2. Set `version` and `aiDevAssistant.ref` to the release (for example `1.0.3` and `v1.0.3`).
3. `npm test && npm run package:cli`
4. Tag `v1.0.3`, create a GitHub Release, and upload `ai-dev-assistant-1.0.3.tgz`.
5. Share the command:

```bash
npx --yes --package=https://github.com/<org>/ai-dev-assistant/releases/download/v1.0.3/ai-dev-assistant-1.0.3.tgz ai-dev-assistant install <feature-id>
```

Build output (`*.tgz`) is git-ignored; do not commit it.

## Update an installed feature

Run the command from the new release with `--overwrite`, then review the Git diff and keep project-specific edits. Files removed from a feature are not deleted.

## Private repositories

Set `GITHUB_TOKEN` or `GH_TOKEN` (fine-grained, read-only **Contents**) in the shell. A private Release asset also needs authentication, so for a fully private toolkit publish the CLI through GitHub Packages or an internal npm registry. Never put tokens in URLs, scripts, or committed `.npmrc` files.

## Conflicts

- Existing files are skipped unless `--overwrite` is given.
- `.vscode/mcp.json` is never modified; follow the guides in `docs/ai-dev-assistant/` after installing `drawio-diagram-generator` or `documentation-confluence`.
