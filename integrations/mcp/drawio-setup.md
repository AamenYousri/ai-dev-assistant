# draw.io MCP setup for VS Code

This guide is installed with the `drawio-diagram-generator` feature. MCP setup is a separate, explicit step; the installer does not overwrite an existing MCP configuration.

## Hosted endpoint

```text
https://mcp.draw.io/mcp
```

## Add the server in VS Code

1. Open the Command Palette (`Ctrl+Shift+P`).
2. Run **MCP: Add Server**.
3. Choose **HTTP** as the server type.
4. Enter `https://mcp.draw.io/mcp` as the URL.
5. Give it the name `drawio` and save it to your user profile or workspace, following your organization's policy.
6. Start the server and approve any trust or connection prompt.
7. In Copilot Chat, use Agent mode and make sure the draw.io tools are enabled.

Alternatively, merge this server entry into an existing `.vscode/mcp.json`; do not replace other configured servers:

```json
{
  "servers": {
    "drawio": {
      "type": "http",
      "url": "https://mcp.draw.io/mcp"
    }
  }
}
```

If an `mcp.json` already exists, merge the `drawio` object into its existing `servers` object. Do not overwrite existing MCP configuration blindly.

## Test it

In Copilot Chat (Agent mode), ask:

> Create an editable draw.io architecture diagram of this application. Inspect relevant project files first, and do not invent components or connections.

If the MCP server is not available, the skill instructs the assistant to provide Mermaid or structured diagram source instead and state that no draw.io diagram was created.

## Security

The hosted MCP server is an external service. Follow your organization's rules before sending source code or architecture details to it. Do not include secrets or personal data in diagram prompts.
