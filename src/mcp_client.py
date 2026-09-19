from contextlib import AsyncExitStack
from typing import Optional

class MCPClient:
    def __init__(self):
        self._stack = None
        self.session = None

    async def connect(self, url: str, token: Optional[str] = None):
        try:
            from mcp import ClientSession
        except ImportError as exc:
            raise RuntimeError("Install the official 'mcp' Python package to use MCP connections.") from exc
        headers = {"Authorization": f"Bearer {token}"} if token else None
        self._stack = AsyncExitStack()
        # MCP SDK v2 renamed this transport and moves headers to its HTTP client.
        # Retain the v1 path so a generic deployment works with either supported SDK.
        try:
            import httpx2
            from mcp.client.streamable_http import streamable_http_client
            http_client = httpx2.AsyncClient(headers=headers)
            await self._stack.enter_async_context(http_client)
            transport = streamable_http_client(url, http_client=http_client)
        except (ImportError, AttributeError):
            from mcp.client.streamable_http import streamablehttp_client
            transport = streamablehttp_client(url, headers=headers)
        streams = await self._stack.enter_async_context(transport)
        read, write = streams[0], streams[1]
        self.session = await self._stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    async def list_tools(self):
        if not self.session: raise RuntimeError("Not connected")
        return (await self.session.list_tools()).tools

    async def call_tool(self, name: str, arguments: dict | None = None):
        if not self.session: raise RuntimeError("Not connected")
        return await self.session.call_tool(name, arguments or {})

    async def close(self):
        if self._stack:
            await self._stack.aclose()
        self._stack = self.session = None
