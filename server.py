#!/usr/bin/env python3
"""MEOK AI Labs — habit-tracker-ai-mcp MCP Server. Track habits, streaks, and build accountability."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any
import uuid
import sys, os

sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
import mcp.types as types
from collections import defaultdict

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


_store = {"habits": {}, "completions": []}
server = Server("habit-tracker-ai")


def create_id():
    return str(uuid.uuid4())[:8]


@server.list_resources()
async def handle_list_resources():
    return [
        Resource(uri="habits://all", name="All Habits", mimeType="application/json")
    ]


@server.list_tools()
async def handle_list_tools():
    return [
        Tool(
            name="create_habit",
            description="Create new habit",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "frequency": {
                        "type": "string",
                        "enum": ["daily", "weekly", "custom"],
                    },
                    "reminder_time": {"type": "string"},
                },
            },
        ),
        Tool(
            name="log_completion",
            description="Log habit completion",
            inputSchema={
                "type": "object",
                "properties": {
                    "habit_id": {"type": "string"},
                    "date": {"type": "string"},
                    "notes": {"type": "string"},
                },
            },
        ),
        Tool(
            name="get_habit_streak",
            description="Get current streak",
            inputSchema={
                "type": "object",
                "properties": {"habit_id": {"type": "string"}},
            },
        ),
        Tool(
            name="get_habit_history",
            description="Get habit history",
            inputSchema={
                "type": "object",
                "properties": {
                    "habit_id": {"type": "string"},
                    "days": {"type": "number"},
                },
            },
        ),
        Tool(
            name="get_all_habits",
            description="Get all habits",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="delete_habit",
            description="Delete habit",
            inputSchema={
                "type": "object",
                "properties": {"habit_id": {"type": "string"}},
            },
        ),
        Tool(
            name="get_weekly_stats",
            description="Get weekly stats",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Any = None) -> list[types.TextContent]:
    args = arguments or {}
    api_key = args.get("api_key", "")
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
                ),
            )
        ]

    if name == "create_habit":
        habit = {
            "id": create_id(),
            "name": args["name"],
            "frequency": args.get("frequency", "daily"),
            "reminder": args.get("reminder_time"),
            "created_at": datetime.now().isoformat(),
            "current_streak": 0,
            "best_streak": 0,
        }
        _store["habits"][habit["id"]] = habit
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"created": True, "habit_id": habit["id"], "name": habit["name"]}
                ),
            )
        ]

    elif name == "log_completion":
        habit_id = args.get("habit_id")
        date = args.get("date", datetime.now().strftime("%Y-%m-%d"))

        if habit_id not in _store["habits"]:
            return [
                TextContent(type="text", text=json.dumps({"error": "Habit not found"}))
            ]

        completion = {
            "habit_id": habit_id,
            "date": date,
            "notes": args.get("notes", ""),
            "completed_at": datetime.now().isoformat(),
        }
        _store["completions"].append(completion)

        habit = _store["habits"][habit_id]
        habit["current_streak"] = habit.get("current_streak", 0) + 1
        if habit["current_streak"] > habit.get("best_streak", 0):
            habit["best_streak"] = habit["current_streak"]

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"logged": True, "current_streak": habit["current_streak"]}
                ),
            )
        ]

    elif name == "get_habit_streak":
        habit_id = args.get("habit_id")

        if habit_id not in _store["habits"]:
            return [
                TextContent(type="text", text=json.dumps({"error": "Habit not found"}))
            ]

        habit = _store["habits"][habit_id]
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "current_streak": habit.get("current_streak", 0),
                        "best_streak": habit.get("best_streak", 0),
                    }
                ),
            )
        ]

    elif name == "get_habit_history":
        habit_id = args.get("habit_id")
        days = args.get("days", 30)

        completions = [
            c for c in _store["completions"] if c.get("habit_id") == habit_id
        ][-days:]

        return [
            TextContent(
                type="text",
                text=json.dumps({"history": completions, "count": len(completions)}),
            )
        ]

    elif name == "get_all_habits":
        habits = list(_store["habits"].values())

        return [
            TextContent(
                type="text", text=json.dumps({"habits": habits, "count": len(habits)})
            )
        ]

    elif name == "delete_habit":
        habit_id = args.get("habit_id")

        if habit_id in _store["habits"]:
            del _store["habits"][habit_id]
            _store["completions"] = [
                c for c in _store["completions"] if c.get("habit_id") != habit_id
            ]
            return [TextContent(type="text", text=json.dumps({"deleted": True}))]

        return [TextContent(type="text", text=json.dumps({"error": "Habit not found"}))]

    elif name == "get_weekly_stats":
        cutoff = datetime.now() - timedelta(days=7)
        recent = [
            c
            for c in _store["completions"]
            if datetime.fromisoformat(c["completed_at"]) >= cutoff
        ]

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "week_completions": len(recent),
                        "total_habits": len(_store["habits"]),
                    }
                ),
            )
        ]

    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]


async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (
        read_stream,
        write_stream,
    ):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="habit-tracker-ai",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
