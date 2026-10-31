# VS Code FAQ

**How do I run a feature?** Type `/` in Copilot Chat and choose the skill (for example `/logging-advisor`), then add context. Skills also load automatically when the request matches their description.

**Where are the agents?** `.github/agents/*.agent.md` appear in the Agent picker (Code Reviewer, Security Reviewer). They restrict tools; the workflow itself is in the matching skill.

**Why no prompt files?** A skill is already a slash command, and prompt files only run in Local harness sessions. A prompt that only says "use skill X" adds nothing.

**Does this review GitLab Merge Requests?** No. `/code-review` and the Code Reviewer agent review local changes before you open an MR and never post to GitLab.

**When do I need MCP?** Only for external systems: draw.io (diagram files) and Atlassian (Confluence/Jira). Setup guides are installed under `docs/ai-dev-assistant/`.
