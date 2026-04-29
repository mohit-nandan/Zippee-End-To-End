#!/usr/bin/env python3
"""Read-only MySQL MCP server for Zippee prod database."""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from utils.config_loader import get_config
from utils.db_client import DatabaseClient

app = Server("mysql-prod")


def _get_db() -> DatabaseClient:
    cfg = get_config("prod")
    return DatabaseClient(
        host=cfg["db_host"],
        port=cfg["db_port"],
        user=cfg["db_user"],
        password=cfg["db_password"],
        database=cfg["db_name"],
    )


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="query",
            description="Run a read-only SQL query (SELECT/SHOW/DESCRIBE/EXPLAIN) against the Zippee prod database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL query to execute"},
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="list_tables",
            description="List all tables in the Zippee prod database.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="describe_table",
            description="Show the column structure of a table.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "Table name"},
                },
                "required": ["table"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        with _get_db() as db:
            if name == "query":
                rows = db.fetch_all(arguments["sql"])
                return [TextContent(type="text", text=json.dumps(rows, indent=2, default=str))]

            elif name == "list_tables":
                rows = db.fetch_all("SHOW TABLES")
                tables = [list(r.values())[0] for r in rows]
                return [TextContent(type="text", text="\n".join(tables))]

            elif name == "describe_table":
                table = arguments["table"]
                rows = db.fetch_all(f"DESCRIBE `{table}`")
                return [TextContent(type="text", text=json.dumps(rows, indent=2, default=str))]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {exc}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
