#!/usr/bin/env python3
"""Appium MCP server — live inspection and interaction with Zippee Rider App."""

import asyncio
import base64
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, ImageContent, Tool

from appium import webdriver as appium_webdriver
from appium.options import AppiumOptions
from utils.config_loader import get_device_caps

APPIUM_URL = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")

app = Server("appium-android")
_driver = None


def _get_driver():
    global _driver
    if _driver is None:
        caps = get_device_caps("android")
        options = AppiumOptions()
        for k, v in caps.items():
            options.set_capability(k, v)
        _driver = appium_webdriver.Remote(APPIUM_URL, options=options)
    return _driver


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="screenshot",
            description="Take a screenshot of the current app screen.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="page_source",
            description="Get the full XML element tree of the current screen — use this to find real locators.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="tap",
            description="Tap an element by XPath.",
            inputSchema={
                "type": "object",
                "properties": {
                    "xpath": {"type": "string", "description": "XPath of the element to tap"},
                },
                "required": ["xpath"],
            },
        ),
        Tool(
            name="tap_by_id",
            description="Tap an element by resource-id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_id": {"type": "string", "description": "resource-id of the element"},
                },
                "required": ["resource_id"],
            },
        ),
        Tool(
            name="type_text",
            description="Clear and type text into an element by XPath.",
            inputSchema={
                "type": "object",
                "properties": {
                    "xpath": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["xpath", "text"],
            },
        ),
        Tool(
            name="swipe_up",
            description="Swipe up to scroll down the screen.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="swipe_down",
            description="Swipe down to scroll up the screen.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="current_activity",
            description="Get the current Android activity name.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="back",
            description="Press the Android back button.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="find_elements",
            description="Find all elements matching an XPath and return their text and resource-ids.",
            inputSchema={
                "type": "object",
                "properties": {
                    "xpath": {"type": "string"},
                },
                "required": ["xpath"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        drv = _get_driver()

        if name == "screenshot":
            data = drv.get_screenshot_as_base64()
            return [ImageContent(type="image", data=data, mimeType="image/png")]

        elif name == "page_source":
            return [TextContent(type="text", text=drv.page_source)]

        elif name == "tap":
            el = drv.find_element("xpath", arguments["xpath"])
            el.click()
            return [TextContent(type="text", text=f"Tapped: {arguments['xpath']}")]

        elif name == "tap_by_id":
            el = drv.find_element("id", arguments["resource_id"])
            el.click()
            return [TextContent(type="text", text=f"Tapped id: {arguments['resource_id']}")]

        elif name == "type_text":
            el = drv.find_element("xpath", arguments["xpath"])
            el.clear()
            el.send_keys(arguments["text"])
            return [TextContent(type="text", text=f"Typed into {arguments['xpath']}")]

        elif name == "swipe_up":
            size = drv.get_window_size()
            w, h = size["width"], size["height"]
            drv.swipe(w // 2, int(h * 0.75), w // 2, int(h * 0.25), 500)
            return [TextContent(type="text", text="Swiped up")]

        elif name == "swipe_down":
            size = drv.get_window_size()
            w, h = size["width"], size["height"]
            drv.swipe(w // 2, int(h * 0.25), w // 2, int(h * 0.75), 500)
            return [TextContent(type="text", text="Swiped down")]

        elif name == "current_activity":
            return [TextContent(type="text", text=drv.current_activity)]

        elif name == "back":
            drv.back()
            return [TextContent(type="text", text="Pressed back")]

        elif name == "find_elements":
            elements = drv.find_elements("xpath", arguments["xpath"])
            results = []
            for el in elements:
                results.append({
                    "text": el.text,
                    "resource_id": el.get_attribute("resource-id"),
                    "content_desc": el.get_attribute("content-desc"),
                    "class": el.get_attribute("class"),
                })
            return [TextContent(type="text", text=json.dumps(results, indent=2))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {exc}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
