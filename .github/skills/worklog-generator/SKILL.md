---
name: worklog-generator
description: Turn verified Git activity, tickets, and user notes into accurate concise worklog descriptions. Use when preparing daily or weekly time entries.
---

# Worklog Generator

## Goal
Draft concise worklog descriptions from evidence supplied by Git, tickets, and the user. The user remains responsible for confirming the actual time spent.

## Workflow
1. Gather available evidence: commits, changed files, branch/issue identifiers, ticket summaries, review discussions, and the user's notes.
2. Use the included `./scripts/git_activity.py` helper when a Git repository is available. Treat its output as a list of evidence, not proof of time spent.
3. Group related work into meaningful activities (analysis, implementation, debugging, testing, review, deployment, documentation, coordination).
4. Ask for the hours or use only hours explicitly provided by the user or approved time-tracking data.
5. Draft clear, factual entries in past tense. Describe outcome and value without exaggeration.
6. Remove duplicate or overly technical detail when the target system needs short descriptions.
7. Present entries for user review.

## Output
A table with date, worklog description, evidence, and hours (blank or “to confirm” if not provided). Do not allocate hours from commit counts, file timestamps, or estimated coding speed.
