from .config import is_safe_read_tool

def describe_tools(tools):
    return [{"name": tool.name, "description": tool.description or "", "schema": getattr(tool, "inputSchema", {}) or {}, "safe": is_safe_read_tool(tool.name, tool.description or "")} for tool in tools]
