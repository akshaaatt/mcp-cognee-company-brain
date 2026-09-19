import asyncio
import streamlit as st
from src.agent import answer_question
from src.demo_data import load_demo
from src.discovery import describe_tools
from src.ingestion import documents_from_uploads
from src.knowledge import KnowledgeBase
from src.mcp_client import MCPClient

async def discover_mcp(url, token):
    client = MCPClient()
    try:
        await client.connect(url, token)
        return describe_tools(await client.list_tools())
    finally:
        await client.close()

async def ingest_mcp(url, token):
    """Call only zero-argument, read-only candidates; schema-required tools are never guessed."""
    from src.ingestion import normalize_mcp_result
    client = MCPClient()
    docs = []
    try:
        await client.connect(url, token)
        for tool in describe_tools(await client.list_tools()):
            required = tool["schema"].get("required", []) if isinstance(tool["schema"], dict) else []
            if tool["safe"] and not required:
                try:
                    docs.extend(normalize_mcp_result(tool["name"], await client.call_tool(tool["name"])))
                except Exception:
                    # A generic client cannot safely invent arguments or retry a failed tool.
                    continue
        return docs
    finally:
        await client.close()

st.set_page_config(page_title="Mini Company Brain", page_icon="🧠", layout="wide")
if "knowledge" not in st.session_state:
    st.session_state.knowledge = KnowledgeBase()
if "tools" not in st.session_state:
    st.session_state.tools = []
if "result" not in st.session_state:
    st.session_state.result = None
kb = st.session_state.knowledge


def ask(question):
    """Store an answer so it survives Streamlit's button-triggered reruns."""
    st.session_state.question = question
    st.session_state.result = answer_question(kb, question)

st.title("🧠 Mini Company Brain")
st.caption("Connected, grounded company knowledge for humans and agents.")

with st.sidebar:
    st.header("Connect MCP")
    url = st.text_input("MCP Server URL", placeholder="https://example.com/mcp")
    auth = st.selectbox("Authentication", ["None", "Bearer Token"])
    token = st.text_input("Bearer Token", type="password", disabled=auth == "None")
    if st.button("Connect", use_container_width=True):
        if not url:
            st.warning("Enter an MCP server URL.")
        else:
            try:
                st.session_state.tools = asyncio.run(discover_mcp(url, token if auth == "Bearer Token" else None))
                st.success(f"Connected — {len(st.session_state.tools)} tools discovered")
            except Exception as exc:
                st.error(f"Connection failed: {exc}")
    if st.session_state.tools:
        st.subheader("Available MCP Tools")
        for tool in st.session_state.tools:
            icon = "✓" if tool["safe"] else "⚠"
            st.caption(f"{icon} **{tool['name']}** — {tool['description']}")
        if st.button("Ingest safe MCP data", use_container_width=True):
            if not url:
                st.warning("Enter the MCP URL again to ingest.")
            else:
                docs = asyncio.run(ingest_mcp(url, token if auth == "Bearer Token" else None))
                kb.ingest(docs); kb.build()
                st.success(f"Ingested {len(docs)} MCP sources from zero-argument read-only tools.")

left, right = st.columns(2)
with left:
    st.header("Knowledge")
    if st.button("Load Demo Company", type="primary"):
        kb.clear(); docs, links = load_demo(); kb.ingest(docs, links); kb.build()
        st.session_state.result = None
        st.success("Fictional demo company loaded.")
    st.caption(f"{len(kb.documents)} sources · {len({d.source_type for d in kb.documents})} types · {kb.knowledge_mode}")
with right:
    st.header("Upload Knowledge")
    files = st.file_uploader("Markdown, text, or JSON", type=["md", "txt", "json"], accept_multiple_files=True)
    if st.button("Ingest Files") and files:
        docs = documents_from_uploads(files); kb.ingest(docs); kb.build()
        st.success(f"Ingested {len(docs)} sources.")

st.header("Ask Your Company")
quick = "Which customer was affected by the decision made in the January product planning meeting?"
if "question" not in st.session_state:
    st.session_state.question = quick
question = st.text_input("What do you want to know?", key="question")
st.caption("Demo questions")
first, second, third = st.columns(3)
with first:
    if st.button("January decision", use_container_width=True):
        ask("What decision was made in the January product planning meeting?")
with second:
    if st.button("Related ticket", use_container_width=True):
        ask("Which ticket was created by the checkout migration decision?")
with third:
    if st.button("Affected customer", use_container_width=True):
        ask(quick)
if st.button("Ask"):
    ask(question)
result = st.session_state.result
if result:
    st.subheader("Answer")
    st.write(result.text)
    if result.chain:
        st.subheader("Relationship Chain")
        st.code("\n  ↓\n".join(result.chain), language=None)
    with st.expander("Sources / Evidence", expanded=True):
        if not result.evidence: st.caption("No supporting sources retrieved.")
        for doc in result.evidence:
            st.markdown(f"✓ **{doc.source_type.title()}: {doc.title}**")
            st.caption(doc.content)
