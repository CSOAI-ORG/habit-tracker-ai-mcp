#!/usr/bin/env python3
"""MEOK AI Labs — habit-tracker-ai-mcp MCP Server. Track daily habits, streaks, and accountability metrics."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types

# In-memory store (replace with DB in production)
_store = {}

server = Server("habit-tracker-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="log_habit", description="Log a habit completion", inputSchema={"type":"object","properties":{"habit":{"type":"string"}},"required":["habit"]}),
        Tool(name="get_streaks", description="Get habit streaks", inputSchema={"type":"object","properties":{}}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "log_habit":
        _store.setdefault(args["habit"], []).append(datetime.now().strftime("%Y-%m-%d"))
        return [TextContent(type="text", text=json.dumps({"status": "logged"}, indent=2))]
    if name == "get_streaks":
        streaks = {k: len(set(v)) for k, v in _store.items()}
        return [TextContent(type="text", text=json.dumps(streaks, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="habit-tracker-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())
