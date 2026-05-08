<div align="center">

# Habit Tracker Ai MCP

**MCP server for habit tracker ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-habit-tracker-ai-mcp)](https://pypi.org/project/meok-habit-tracker-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Habit Tracker Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `create_habit` | Create new habit |
| `log_completion` | Log habit completion |
| `get_habit_streak` | Get current streak |
| `get_habit_history` | Get habit history |
| `get_all_habits` | Get all habits |
| `delete_habit` | Delete habit |
| `get_weekly_stats` | Get weekly stats |

## Installation

```bash
pip install meok-habit-tracker-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "habit-tracker-ai": {
      "command": "python",
      "args": ["-m", "meok_habit_tracker_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 7 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
