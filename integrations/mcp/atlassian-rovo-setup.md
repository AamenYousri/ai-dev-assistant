# Atlassian Rovo MCP setup for VS Code

This guide is installed with the `documentation-confluence` feature. MCP setup is a separate, explicit step; authentication and Atlassian permissions remain under the user's control.

## Hosted endpoint

```text
https://mcp.atlassian.com/v2/mcp
```

## Add the server in VS Code

1. Open the Command Palette (`Ctrl+Shift+P`).
2. Run **MCP: Add Server**.
3. Choose **HTTP** as the server type.
4. Enter `https://mcp.atlassian.com/v2/mcp` as the URL.
5. Give it the name `atlassian-rovo` and save it to your user profile or workspace, following your organization's policy.
6. Start the server and complete the authentication flow.
7. Confirm the connected Atlassian account has only the permissions needed for the requested work.

Alternatively, merge this server entry into an existing `.vscode/mcp.json`; do not replace other configured servers:

```json
{
  "servers": {
    "atlassian-rovo": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v2/mcp"
    }
  }
}
```

## Security

Review content before publishing or changing Confluence pages. Do not publish automatically without explicit approval. Follow your organization's data-handling and Atlassian access policies.
