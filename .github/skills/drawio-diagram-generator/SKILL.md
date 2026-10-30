---
name: drawio-diagram-generator
description: Turn source code, architecture descriptions, or process requirements into clear editable draw.io diagrams. Use when a diagram is requested.
---

# draw.io Diagram Generator

## Goal
Create a diagram that communicates the requested system, process, sequence, deployment, or data model. Prefer an editable native `.drawio` result when the configured draw.io integration supports it.

## Workflow
1. Clarify the diagram's purpose and audience from the request. If the source is a repository, inspect only relevant files.
2. Identify components, actors, boundaries, interfaces, data stores, events, and relationships. Do not invent components or flows.
3. Choose an appropriate diagram type: C4/container, component, sequence, deployment, flowchart, ERD, or state diagram.
4. Keep labels concise; group related elements; use consistent direction and terminology; distinguish synchronous calls, asynchronous events, and data stores.
5. Include a legend when line styles or colors convey meaning. Use neutral, accessible colors and avoid visual clutter.
6. Create an editable draw.io diagram using the configured MCP tool. If MCP is unavailable, return Mermaid or structured diagram source and explain that no `.drawio` file was created.
7. Validate that every edge connects meaningful elements and that the diagram matches source evidence.

## Output
State the diagram type, source files used, assumptions, and output artifact. Keep a short list of unknowns when the source is incomplete.

## Safety
Do not send proprietary source code to a third-party MCP endpoint without authorization. Do not include secrets or personal data in diagram labels.
