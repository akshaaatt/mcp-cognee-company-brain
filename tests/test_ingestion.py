from src.ingestion import normalize_mcp_result
from src.config import is_safe_read_tool

def test_normalizes_mcp_dict():
    doc = normalize_mcp_result("search_records", {"title": "A", "status": "open"})[0]
    assert doc.title == "A" and doc.metadata["origin"] == "mcp"

def test_rejects_mutating_tool():
    assert not is_safe_read_tool("delete_ticket", "Delete a ticket")
