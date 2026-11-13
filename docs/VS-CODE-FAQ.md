# VS Code FAQ

**How do I run a feature?** Type `/` in Copilot Chat and choose the skill (for example `/logging-advisor`), then add context. Skills also load automatically when the request matches their description.

**Where are the agents?** `.github/agents/*.agent.md` appear in the Agent picker (Worklog Assistant, Code Reviewer, Security Reviewer) when their features are installed. They scope tool use; the workflow itself is in the matching skill. Code/security review can also start directly from a skill without selecting an agent.

**Why no prompt files?** A skill is already a slash command, and prompt files only run in Local harness sessions. A prompt that only says "use skill X" adds nothing.

**Does this review Pull/Merge Requests?** No. `/code-review` and the Code Reviewer agent review local changes before you open a PR/MR and never post to GitHub, GitLab, or any other Git host.

**Can I generate commit messages?** Use `/worklog-generator` or the Worklog Assistant agent with a staged diff. Suggestions require developer review; the agent does not create commits or submit worklogs. Never infer hours from Git activity or meetings.

**When do I need integrations?** The six features can start from local files and user-supplied evidence. Worklog ticketing/calendar access is optional and requires separately configured, explicitly authorized integrations. The installer does not configure MCP or external services.
