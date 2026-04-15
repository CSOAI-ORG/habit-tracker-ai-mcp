# Habit Tracker Ai

> By [MEOK AI Labs](https://meok.ai) — Track habits, streaks, and build accountability.

MEOK AI Labs — habit-tracker-ai-mcp MCP Server. Track habits, streaks, and build accountability.

## Installation

```bash
pip install habit-tracker-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install habit-tracker-ai-mcp
```

## Tools

### `create_habit`
Create new habit

**Parameters:**
- `name` (str)
- `frequency` (str)
- `reminder_time` (str)

### `log_completion`
Log habit completion

**Parameters:**
- `habit_id` (str)
- `date` (str)
- `notes` (str)

### `get_habit_streak`
Get current streak

**Parameters:**
- `habit_id` (str)

### `get_habit_history`
Get habit history

**Parameters:**
- `habit_id` (str)
- `days` (int)

### `get_all_habits`
Get all habits

### `delete_habit`
Delete habit

**Parameters:**
- `habit_id` (str)

### `get_weekly_stats`
Get weekly stats


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/habit-tracker-ai-mcp](https://github.com/CSOAI-ORG/habit-tracker-ai-mcp)
- **PyPI**: [pypi.org/project/habit-tracker-ai-mcp](https://pypi.org/project/habit-tracker-ai-mcp/)

## License

MIT — MEOK AI Labs
