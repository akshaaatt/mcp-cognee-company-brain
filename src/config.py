MAX_TOOLS = 10
MAX_RECORDS_PER_TOOL = 100
MUTATING_WORDS = ("create", "update", "delete", "send", "publish", "modify", "pay", "write", "remove")

def is_safe_read_tool(name: str, description: str = "") -> bool:
    text = f"{name} {description}".lower()
    return not any(word in text for word in MUTATING_WORDS) and any(
        word in text for word in ("get", "list", "search", "read", "find", "fetch", "retrieve")
    )
