"""
MCP Server entry point — run with: python -m backend.mcp_server.run
Supports stdio (default) and SSE transports.
Uses mcp SDK v2 API.
"""

import argparse
import sys

import anyio

from .server import create_server


def run_stdio():
    """Run MCP server over stdio transport."""
    from mcp.server.stdio import stdio_server

    server = create_server()

    async def _main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    anyio.run(_main)


def run_sse(host: str = "127.0.0.1", port: int = 8001):
    """Run MCP server over SSE transport via Starlette."""
    from mcp.server.sse import SseServerTransport

    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.responses import Response

    server = create_server()
    sse_transport = SseServerTransport("/mcp/message")

    async def handle_sse(request):
        # mcp SDK v2: connect_sse 需要 ASGI 的 scope/receive/send 三个参数
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
        # 连接结束后必须返回 Response，否则客户端断开时报 NoneType 错误
        return Response()

    async def handle_post_message(scope, receive, send):
        # handle_post_message 本身是 ASGI app，直接转发三参数
        await sse_transport.handle_post_message(scope, receive, send)

    app = Starlette(
        routes=[
            Route("/mcp/sse", endpoint=handle_sse),
            Mount("/mcp/message", app=handle_post_message),
        ],
        middleware=[
            Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
        ],
    )

    import uvicorn
    uvicorn.run(app, host=host, port=port)


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
        print(f"Starting MCP SSE server on {args.host}:{args.port}", file=sys.stderr)
        run_sse(host=args.host, port=args.port)
    else:
        print("Starting MCP stdio server...", file=sys.stderr)
        run_stdio()


if __name__ == "__main__":
    main()