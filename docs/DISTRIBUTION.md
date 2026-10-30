# Distribution to personal and team projects

## Recommended model

Use this repository as the canonical source and install selected features into each application repository. The application repository contains the copy that Copilot or GitLab Duo discovers; the central toolkit remains the maintained source.

## Install selected features

```bash
python scripts/install.py --list
python scripts/install.py --target ../my-java-project --features logging-advisor code-review
python scripts/install.py --target ../my-cap-project --features logging-advisor log-analyzer code-review security-checks
```

Windows example:

```powershell
py scripts/install.py --target "C:\src\my-cap-project" --features logging-advisor code-review security-checks
```

The installer:

- Copies only files mapped to the selected feature IDs.
- Creates missing destination folders.
- Skips existing files unless `--overwrite` is used.
- Supports `--dry-run` and `--list`.
- Does not modify `.gitlab-ci.yml`, `.vscode/mcp.json`, or project build files automatically.

## Updating an installed feature

1. Pull the latest toolkit repository.
2. Create a branch in the target application repository.
3. Rerun the installer with the same feature IDs and `--overwrite`.
4. Review the resulting diff. Preserve local project-specific instructions.
5. Run the project's tests and commit the reviewed update.

Example:

```bash
python scripts/install.py --target ../my-cap-project --features logging-advisor code-review --overwrite
```

## Team rollout

For a team, publish this repository to the company's GitLab, Bitbucket, or GitHub and document the approved toolkit version. Each project owner selects the features that fit the application. A small onboarding script or CI job can run the installer, but changes should still be reviewed like normal source changes.

Do not use a Git submodule as the default distribution mechanism for `.github` customizations. Copilot discovery is based on supported directories in the opened workspace. A submodule nested under another folder will not automatically become the project's `.github/skills`, `.github/prompts`, or `.github/agents` directory.

## Avoiding conflicts

- The installer intentionally skips existing target files by default.
- If `.gitlab/duo/mr-review-instructions.yaml` already exists, merge the toolkit's review groups manually or use `--overwrite` only after backing up and reviewing the existing file.
- Keep project-specific instructions and secrets out of the central toolkit.
- Store credentials in the approved secret store or MCP authentication flow, never in committed configuration.
