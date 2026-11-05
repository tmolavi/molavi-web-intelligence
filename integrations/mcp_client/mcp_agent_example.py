"""
Example configuration and usage of MWIE MCP Server in Claude Desktop, Cursor, or Hermes.
"""

import json

# MCP Client configuration for Claude Desktop (claude_desktop_config.json)
# or Cursor settings.json:
CLAUDE_DESKTOP_CONFIG = {
    "mcpServers": {
        "molavi-web-intelligence": {
            "command": "python3",
            "args": ["-m", "mwie.mcp.server"],
            "env": {"MWIE_CACHE_ENABLED": "true", "MWIE_RESPECT_ROBOTS": "true"},
        }
    }
}

if __name__ == "__main__":
    print("Example Claude Desktop / Hermes MCP configuration:")
    print(json.dumps(CLAUDE_DESKTOP_CONFIG, indent=2))
