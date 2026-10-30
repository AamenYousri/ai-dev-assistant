---
name: documentation-confluence
description: Draft and maintain technical documentation from source code, architecture, APIs, and project decisions. Use for README, runbooks, architecture pages, and Confluence drafts.
---

# Documentation / Confluence

## Goal
Produce accurate, maintainable technical documentation grounded in the repository and user-provided decisions.

## Workflow
1. Identify the target audience and document type (README, architecture, API, runbook, operational guide, ADR, release note, or Confluence page).
2. Inspect source files, configuration, tests, existing docs, and relevant issue/ticket context. Cite paths and symbols so readers can verify statements.
3. Preserve existing project terminology. Separate verified facts, assumptions, and open questions.
4. Prefer concise structure: purpose, scope, prerequisites, architecture/flow, configuration, procedures, troubleshooting, security considerations, and ownership where relevant.
5. Do not expose secrets, internal personal data, or sensitive configuration values. Replace with placeholders.
6. When Confluence MCP is connected, search for existing pages before proposing a new one. Avoid duplicate pages and preserve existing conventions.
7. Default to a draft in the chat or a local Markdown file. Before creating, updating, or publishing any Confluence page, show the intended space/page/title and content summary and request explicit confirmation.

## Output
Provide the complete draft, source references, assumptions, and suggested destination. Never claim that a page was published unless the tool confirms success.
