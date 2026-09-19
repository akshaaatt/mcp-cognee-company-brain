# Mini Company Brain

A small, generic, open-source Company Brain that combines file uploads and dynamically configured MCP sources into connected, grounded knowledge.

## What it demonstrates

- Multiple company information types: meetings, decisions, tickets, projects, people, and customers
- A Cognee-ready semantic knowledge layer plus explicit relationship preservation
- Natural-language, evidence-first answers
- A genuine multi-hop path: meeting → decision → ticket → customer
- Runtime MCP tool discovery over Streamable HTTP, with mutating tools excluded
- No external AI API key, hardcoded MCP endpoint, or stored MCP credential

## Architecture

```text
MCP / Files → Normalization → Cognee + preserved graph → Retrieval → Grounded answer → Streamlit
```

Every ingestion is synchronized into Cognee (`add` then `cognify`) when its local runtime is available. The included fictional demo also works where Cognee's optional local model assets are unavailable: deterministic graph traversal remains fully grounded and displays its evidence chain, with no external provider key required.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To enable the optional local Cognee semantic pipeline where its compatible
dependencies are available, additionally run `pip install -r requirements-cognee.txt`.

Click **Load Demo Company**, then ask: “Which customer was affected by the decision made in the January product planning meeting?”

## MCP

Enter a Streamable HTTP MCP URL and optional Bearer token in the sidebar. Credentials are held only in the active Streamlit session and are never written to disk or included in knowledge ingestion. Tool discovery is dynamic; only retrieval-looking tools are identified as safe candidates. The import action executes only safe candidates with no required arguments—it never guesses arguments or invokes mutation-looking tools.

For development inspection:

```bash
python scripts/discover_mcp.py https://example.com/mcp --token optional-token
```

## Deploy to Render

Create a Render Blueprint from this repository. `render.yaml` installs the Python requirements and starts Streamlit without environment variables or secrets.

## Test

```bash
python -m pytest
```
