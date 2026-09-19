import json
from pathlib import Path
from .models import SourceDocument

def documents_from_uploads(files) -> list[SourceDocument]:
    result = []
    for upload in files:
        name = upload.name
        raw = upload.getvalue()
        suffix = Path(name).suffix.lower()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if suffix == ".json":
            try:
                value = json.loads(text)
                rows = value if isinstance(value, list) else [value]
                for index, row in enumerate(rows):
                    if isinstance(row, dict):
                        title = str(row.get("title") or row.get("name") or f"{name} #{index + 1}")
                        content = json.dumps(row, indent=2)
                        result.append(SourceDocument(f"file-{name}-{index}", str(row.get("source_type", "document")), title, content, {"origin": "file", "source_name": name}))
                continue
            except json.JSONDecodeError:
                pass
        result.append(SourceDocument(f"file-{name}", "document", name, text, {"origin": "file", "source_name": name}))
    return result

def normalize_mcp_result(tool_name: str, value) -> list[SourceDocument]:
    if hasattr(value, "content"):
        value = [{"text": getattr(part, "text", str(part))} for part in value.content]
    rows = value if isinstance(value, list) else [value]
    docs = []
    for index, row in enumerate(rows):
        if isinstance(row, dict):
            title = str(row.get("title") or row.get("name") or f"{tool_name} #{index + 1}")
            content = json.dumps(row, indent=2)
        else:
            title, content = f"{tool_name} #{index + 1}", str(row)
        docs.append(SourceDocument(f"mcp-{tool_name}-{index}", "other", title, content, {"origin": "mcp", "source_name": tool_name}))
    return docs
