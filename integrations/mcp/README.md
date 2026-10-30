# Optional MCP integrations

MCP provides access to external tools. It is optional and should be enabled only when a workflow needs the corresponding integration.

## draw.io

Official hosted endpoint:

```text
https://mcp.draw.io/mcp
```

The hosted MCP App Server can show interactive draw.io diagrams in supported clients. In VS Code, add it as a remote HTTP MCP server. See [draw.io setup](https://www.drawio.com/docs/manual/generate/drawio-mcp-server/).

## Atlassian Rovo MCP

Official hosted endpoint:

```text
https://mcp.atlassian.com/v2/mcp
```

It can connect compatible AI clients to Jira, Confluence, and other Atlassian Cloud services. Authentication and existing Atlassian permissions apply. See [Atlassian getting started](https://developer.atlassian.com/cloud/rovo-mcp/guides/getting-started/).

## VS Code configuration example

`vscode.mcp.json.example` uses the VS Code `servers` format. Review it, then use **MCP: Add Server** in VS Code to add the desired server to a workspace or personal configuration. VS Code's configuration destinations and format can evolve; do not blindly copy configuration formats between MCP clients.

The example is deliberately not named `mcp.json` and is not installed automatically. Do not commit credentials or tokens.
