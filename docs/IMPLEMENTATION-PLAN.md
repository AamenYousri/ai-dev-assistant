# Implementation plan

Scope, recommended setup, reuse candidates, and estimates below follow [AI Dev Assistant v1.0.2](ai-dev-assistant-v1.0.2.docx). These are planning estimates, not guaranteed delivery dates or a measurement of remaining work. Actual effort depends on project conventions, access, existing tools, and team approvals.

| Initiative | Estimate | Recommended setup and tailoring |
|---|---:|---|
| Log Analyzer | 1 day | Skill with helpers for redaction, filtering, grouping, and context extraction. Start from the Log Analyzer Skill and tailor it to application log formats. |
| Logging Advisor | 1 day | Skill only. Use Logging Best Practices Skill as a starting point and apply team conventions. |
| OCC Postman Generator | 1 day | Custom OCC skill for controllers, facades, DTOs, and request/response behavior, plus a predictable conversion helper. Postman MCP is a reuse candidate, not confirmed for direct custom-controller conversion. |
| Worklog Generator / Commit Message Assistant | 1 day | Custom agent with Git, ticketing, and calendar evidence. No existing agent is identified as covering the full workflow. The developer reviews suggestions and confirms hours; never guess hours or invent activities. |
| Code Review | 1.5 days | Start with a reusable read-only Git review skill based on Awesome Code Review Skills. Tailor separate SAP Commerce/OCC and SAP CAP skills as needed; a shared agent can select the appropriate skill. A dedicated agent is optional for more advanced reviews. |
| Security Checks (Git / Bitbucket) | 1.5 days | Skill with helper scripts and existing scanners; separate agent optional. Use Sentry Security Review Skill as a starting point and tailor checks for SAP Commerce/OCC and SAP CAP, including authentication, authorization, data protection, APIs, dependencies, secrets, deployment, and business logic. |

**Total estimate: 7 days.** Reuse candidates are recommendations from the document, not claims that third-party skills or integrations are bundled.

## Current deliverable status

This repository is a starter implementation with six skills, a Worklog Assistant agent, optional code/security review agents, an npx feature installer, helper scripts for log analysis, OpenAPI conversion, Git evidence, and security scanning, plus tests.

Code review currently uses a shared skill with SAP Commerce/OCC and SAP CAP sections rather than separate stack-specific skills. OCC conversion uses the included OpenAPI helper, not a Postman MCP dependency. Ticketing and calendar integrations are not bundled or configured, and no company systems or production repositories are connected by default. Project-specific tailoring and validation remain necessary.
