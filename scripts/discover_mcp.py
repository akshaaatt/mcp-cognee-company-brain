import argparse, asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.discovery import describe_tools
from src.mcp_client import MCPClient

async def main(url, token):
    client = MCPClient()
    try:
        await client.connect(url, token)
        print("MCP Connection\n==============\n\nStatus: Connected\n\nAvailable tools:")
        for index, tool in enumerate(describe_tools(await client.list_tools()), 1):
            print(f"{index}. {tool['name']} {'[read-only candidate]' if tool['safe'] else '[not auto-called]'}")
    finally: await client.close()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('url'); parser.add_argument('--token')
    args = parser.parse_args(); asyncio.run(main(args.url, args.token))
