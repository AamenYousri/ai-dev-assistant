# Feature catalogue

## 1. Log Analyzer

- **Approach:** custom agent + skill + prompt; optional parser/redaction helper.
- **Mode:** hybrid. A deterministic script redacts common secrets; AI groups symptoms, traces stack traces, and correlates logs with source code.
- **Use:** `/log-analyzer` or select **Log Analyzer** from the Agent picker.
- **Existing reference:** [Dynatrace platform and Davis AI](https://www.dynatrace.com/platform/).
- **Important:** redact before sharing. The helper is best-effort and is not a guarantee that all sensitive data is removed.

## 2. Logging Advisor

- **Approach:** skill + prompt.
- **Mode:** AI-driven.
- **Use:** `/logging-advisor`.
- **Existing reference:** [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) and Copilot in VS Code. This toolkit adds reusable team logging rules; it does not replace the coding assistant.

## 3. OCC Postman Generator

- **Approach:** skill + prompt + OpenAPI conversion helper.
- **Mode:** hybrid. AI can inspect custom SAP Commerce OCC controllers/DTOs; the script converts an OpenAPI JSON specification to a Postman Collection 2.1 file.
- **Use:** `/occ-postman-generator`.
- **Existing reference:** [Postman - Generate collections from API specifications](https://learning.postman.com/docs/design-apis/specifications/generate-collections).
- **Important:** when endpoints are discovered from source code, require evidence for HTTP method, path, parameters, body, authentication, and response. Never invent routes or business payloads.

## 4. draw.io Diagram Generator

- **Approach:** skill + prompt + optional official draw.io MCP.
- **Mode:** hybrid. AI interprets the requested architecture/process and the MCP server creates an editable diagram.
- **Use:** `/drawio-diagram-generator` after configuring draw.io MCP.
- **Existing reference:** [Official draw.io MCP documentation](https://www.drawio.com/docs/manual/generate/drawio-mcp-server/).

## 5. Documentation / Confluence

- **Approach:** custom agent + skill + prompt + optional Atlassian Rovo MCP.
- **Mode:** hybrid. AI drafts documentation; MCP can retrieve or publish Atlassian content when authorized.
- **Use:** `/documentation-confluence` or **Documentation Assistant**.
- **Existing reference:** [Atlassian Rovo MCP - Getting started](https://developer.atlassian.com/cloud/rovo-mcp/guides/getting-started/).
- **Important:** default behavior is draft-only. Ask for explicit confirmation before creating or updating a Confluence page.

## 6. Worklog Generator

- **Approach:** skill + prompt + Git evidence helper.
- **Mode:** hybrid. Script collects commits and changed files; AI turns verified activity and user notes into a concise description.
- **Use:** `/worklog-generator`.
- **Existing reference:** [Tempo Timesheets](https://www.tempo.io/products/timesheets) when the organization uses Tempo.
- **Important:** no duration is inferred from commits or file timestamps. The user supplies and confirms hours.

## 7. Code Review (GitLab)

- **Approach:** GitLab Duo Code Review + `.gitlab/duo/mr-review-instructions.yaml`; optional Copilot review skill/agent for local changes in VS Code.
- **Mode:** AI-driven, complemented by deterministic linters and tests.
- **Use:** GitLab Duo reviews Merge Requests when enabled and licensed. In VS Code, use `/code-review` or **Code Reviewer** for a local workspace review.
- **Existing reference:** [GitLab Duo Code Review](https://docs.gitlab.com/user/gitlab_duo/code_review/) and [custom review instructions](https://docs.gitlab.com/user/gitlab_duo/customize_duo/review_instructions/).
- **Important:** GitLab Duo's native MR review and Copilot's local workspace agent are separate workflows. GitLab Code Review Flow reads `.gitlab/duo/mr-review-instructions.yaml`; it does not read the Copilot `SKILL.md` or agent files. GitLab Duo custom instructions are guidance, not enforcement. The custom-instructions documentation currently lists Premium / Ultimate with the GitLab Duo Enterprise add-on; check your exact GitLab version, tier, add-on, and instance configuration.

## 8. Security Checks

- **Approach:** security agent + skill + prompt + existing scanners.
- **Mode:** hybrid. Scanners detect known patterns/dependencies; AI explains findings, prioritizes evidence, and reviews risky changes.
- **Use:** `/security-checks` or **Security Reviewer**.
- **Existing references:** [GitLab SAST](https://docs.gitlab.com/user/application_security/sast/), [Semgrep](https://semgrep.dev/docs/), [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/).
- **Important:** AI review is not a security control. Use approved scanners and CI policies, triage findings, and retain human review.
