"""
MCP Server entry point — run with: python -m backend.mcp.run
Supports stdio (default) and SSE transports.
"""

import argparse
import sys

from mcp.server import mcp


def main():
    parser = argparse.ArgumentParser(description="MarsResume MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="SSE host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8001, help="SSE port (default: 8001)")

    args = parser.parse_args()

    if args.transport == "sse":
        print(f"Starting MCP SSE server on {args.host}:{args.port}")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        print("Starting MCP stdio server...", file=sys.stderr)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()