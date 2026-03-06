from fastapi import FastAPI

from mcp_foundry.mcp_runtime.server_factory import build_mcp_app
from mcp_foundry.models.datasource import Datasource
from mcp_foundry.models.mcp_server import McpServer

_app_ref: FastAPI | None = None
_mounted: dict[str, object] = {}


def init_registry(app: FastAPI) -> None:
    global _app_ref
    _app_ref = app


async def mount_server(server: McpServer, datasource: Datasource | None) -> None:
    """Build and mount an MCP server at /mcp/{server_id}.

    Args:
        server: McpServer ORM instance.
        datasource: Associated Datasource ORM instance (optional).
    """
    assert _app_ref is not None, "Registry not initialized"
    mcp = build_mcp_app(server, datasource)
    path = f"/mcp/{server.id}"
    asgi_app = mcp.get_asgi_app()  # type: ignore
    _app_ref.mount(path, asgi_app)
    _mounted[str(server.id)] = asgi_app


def unmount_server(server_id: str) -> None:
    """Remove an MCP server mount from the registry.

    Args:
        server_id: UUID string of the server to unmount.

    Note:
        FastAPI does not support dynamic unmounting natively; the route
        is removed from the router table so new requests get 404, but
        existing connections drain naturally.
    """
    assert _app_ref is not None, "Registry not initialized"
    if server_id not in _mounted:
        return
    path = f"/mcp/{server_id}"
    _app_ref.routes[:] = [r for r in _app_ref.routes if getattr(r, "path", "") != path]
    del _mounted[server_id]


async def restore_active_servers(app: FastAPI) -> None:
    """Re-mount all active MCP servers from the database on startup.

    Args:
        app: The FastAPI application instance.
    """
    from sqlalchemy import select

    from mcp_foundry.core.database import async_session_factory
    from mcp_foundry.models.datasource import Datasource
    from mcp_foundry.models.mcp_server import McpServer

    init_registry(app)

    async with async_session_factory() as session:
        rows = await session.execute(select(McpServer).where(McpServer.status == "active"))
        servers = rows.scalars().all()
        for server in servers:
            ds = None
            if server.datasource_id:
                ds = await session.get(Datasource, server.datasource_id)
            if (ds and ds.status == "ready") or server.tools_config:
                await mount_server(server, ds)
