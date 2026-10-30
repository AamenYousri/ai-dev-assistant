# GitLab integrations

## GitLab Duo Code Review

For native Merge Request reviews, GitLab Duo Code Review is the relevant product feature. It is separate from GitHub Copilot custom agents running locally in VS Code.

1. Check your GitLab version, subscription, Duo add-on entitlement, and administrator settings.
2. Enable automatic reviews or request a review according to your organization's GitLab configuration.
3. The toolkit repository includes `.gitlab/duo/mr-review-instructions.yaml` at the native GitLab discovery path. The installer also copies this file into target projects when you select `code-review`.
4. Customize the instructions to match that repository's architecture and standards.

The included YAML is a starting point. GitLab documents the file location and format. Instructions guide the AI reviewer; they are not enforced policies.

Official docs: https://docs.gitlab.com/user/gitlab_duo/customize_duo/review_instructions/

## GitLab SAST

GitLab's SAST template can be enabled in a project's `.gitlab-ci.yml` with:

```yaml
include:
  - template: Jobs/SAST.gitlab-ci.yml
```

Do not add this automatically to projects. First inspect the existing pipeline, stages, runner executor, language support, and company security policy. Official docs: https://docs.gitlab.com/user/application_security/sast/.
