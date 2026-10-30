# VS Code FAQ

## Why does my custom agent appear in the Agent picker, but a prompt does not?

They are different customization types:

- `*.agent.md` files under `.github/agents/` appear in the Agent picker.
- `SKILL.md` files under `.github/skills/<skill-name>/` appear as skills and can be invoked with `/skill-name` in Copilot-compatible chat sessions.
- `*.prompt.md` files under `.github/prompts/` are manually invoked prompt templates. Current VS Code documentation says prompt files run only in Local harness sessions. If you use the Copilot harness, use the corresponding skill or agent.

## How do I use a feature in chat?

Open the project where the feature was installed, open Copilot Chat, type `/`, and select a skill such as `/logging-advisor`. You can also add context after the slash command.

## How do I open an interactive reviewer?

Open the Agent picker and choose **Code Reviewer**. This agent reviews the current local workspace changes. It does not automatically fetch a GitLab Merge Request or post comments to GitLab.

## How do I review a GitLab Merge Request?

Use GitLab Duo Code Review if it is enabled and available in your GitLab subscription. The installed `.gitlab/duo/mr-review-instructions.yaml` customizes native GitLab Duo reviews. The Copilot Code Reviewer is a separate local review workflow.

## When do I need MCP?

Only when a capability needs to interact with an external service, such as creating diagrams through draw.io or searching/publishing Atlassian content. Normal source-code review, logging advice, and local helper scripts do not need MCP.
