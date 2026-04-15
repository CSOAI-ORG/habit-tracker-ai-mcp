#!/usr/bin/env python3
"""MEOK AI Labs — habit-tracker-ai-mcp MCP Server. Track habits, streaks, and build accountability."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.fastmcp import FastMCP
from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


_store = {"habits": {}, "completions": []}
mcp = FastMCP("habit-tracker-ai", instructions="Track habits, streaks, and build accountability.")


def create_id():
    return str(uuid.uuid4())[:8]


@mcp.tool()
def create_habit(name: str, frequency: str = "daily", reminder_time: str = "", api_key: str = "") -> str:
    """Create new habit"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    habit = {
        "id": create_id(),
        "name": name,
        "frequency": frequency,
        "reminder": reminder_time or None,
        "created_at": datetime.now().isoformat(),
        "current_streak": 0,
        "best_streak": 0,
    }
    _store["habits"][habit["id"]] = habit
    return json.dumps({"created": True, "habit_id": habit["id"], "name": habit["name"]})


@mcp.tool()
def log_completion(habit_id: str, date: str = "", notes: str = "", api_key: str = "") -> str:
    """Log habit completion"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    if habit_id not in _store["habits"]:
        return json.dumps({"error": "Habit not found"})

    completion = {
        "habit_id": habit_id,
        "date": date,
        "notes": notes,
        "completed_at": datetime.now().isoformat(),
    }
    _store["completions"].append(completion)

    habit = _store["habits"][habit_id]
    habit["current_streak"] = habit.get("current_streak", 0) + 1
    if habit["current_streak"] > habit.get("best_streak", 0):
        habit["best_streak"] = habit["current_streak"]

    return json.dumps({"logged": True, "current_streak": habit["current_streak"]})


@mcp.tool()
def get_habit_streak(habit_id: str, api_key: str = "") -> str:
    """Get current streak"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if habit_id not in _store["habits"]:
        return json.dumps({"error": "Habit not found"})

    habit = _store["habits"][habit_id]
    return json.dumps({
        "current_streak": habit.get("current_streak", 0),
        "best_streak": habit.get("best_streak", 0),
    })


@mcp.tool()
def get_habit_history(habit_id: str, days: int = 30, api_key: str = "") -> str:
    """Get habit history"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    completions = [
        c for c in _store["completions"] if c.get("habit_id") == habit_id
    ][-days:]

    return json.dumps({"history": completions, "count": len(completions)})


@mcp.tool()
def get_all_habits(api_key: str = "") -> str:
    """Get all habits"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    habits = list(_store["habits"].values())
    return json.dumps({"habits": habits, "count": len(habits)})


@mcp.tool()
def delete_habit(habit_id: str, api_key: str = "") -> str:
    """Delete habit"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    if habit_id in _store["habits"]:
        del _store["habits"][habit_id]
        _store["completions"] = [
            c for c in _store["completions"] if c.get("habit_id") != habit_id
        ]
        return json.dumps({"deleted": True})

    return json.dumps({"error": "Habit not found"})


@mcp.tool()
def get_weekly_stats(api_key: str = "") -> str:
    """Get weekly stats"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    cutoff = datetime.now() - timedelta(days=7)
    recent = [
        c
        for c in _store["completions"]
        if datetime.fromisoformat(c["completed_at"]) >= cutoff
    ]

    return json.dumps({
        "week_completions": len(recent),
        "total_habits": len(_store["habits"]),
    })


if __name__ == "__main__":
    mcp.run()
