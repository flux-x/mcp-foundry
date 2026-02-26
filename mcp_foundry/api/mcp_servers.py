"""REST API router for MCP server management."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_foundry.api.schemas.mcp_server import (
    McpServerCreate,
    McpServerSchema,
    McpServerUpdate,
)
from mcp_foundry.core.database import get_db
from mcp_foundry.models.datasource import Datasource
from mcp_foundry.models.mcp_server import McpServer

router = APIRouter(prefix="/mcp-servers", tags=["mcp-servers"])


@router.post("", response_model=McpServerSchema, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    body: McpServerCreate, db: AsyncSession = Depends(get_db)
) -> McpServerSchema:
    """Create an MCP server configuration (not yet deployed)."""
    ds = await db.get(Datasource, body.datasource_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Datasource not found")
    if ds.status != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Datasource is not ready (status: {ds.status}). Wait for scraping to complete.",
        )

    server = McpServer(
        name=body.name,
        datasource_id=body.datasource_id,
        tool_description=body.tool_description,
        status="stopped",
    )
    db.add(server)
    await db.commit()
    await db.refresh(server)
    return McpServerSchema.model_validate(server)


@router.get("", response_model=list[McpServerSchema])
async def list_mcp_servers(db: AsyncSession = Depends(get_db)) -> list[McpServerSchema]:
    """List all MCP servers."""
    rows = await db.execute(select(McpServer).order_by(McpServer.created_at.desc()))
    return [McpServerSchema.model_validate(s) for s in rows.scalars()]


@router.get("/{server_id}", response_model=McpServerSchema)
async def get_mcp_server(
    server_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> McpServerSchema:
    """Get an MCP server by ID."""
    server = await db.get(McpServer, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return McpServerSchema.model_validate(server)


@router.patch("/{server_id}", response_model=McpServerSchema)
async def update_mcp_server(
    server_id: uuid.UUID, body: McpServerUpdate, db: AsyncSession = Depends(get_db)
) -> McpServerSchema:
    """Update name or tool description of a stopped MCP server."""
    server = await db.get(McpServer, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    if server.status == "active":
        raise HTTPException(status_code=400, detail="Stop the server before editing it.")
    if body.name is not None:
        server.name = body.name
    if body.tool_description is not None:
        server.tool_description = body.tool_description
    await db.commit()
    await db.refresh(server)
    return McpServerSchema.model_validate(server)


@router.post("/{server_id}/deploy", response_model=McpServerSchema)
async def deploy_mcp_server(
    server_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> McpServerSchema:
    """Deploy (activate) an MCP server, mounting its SSE endpoint."""
    from mcp_foundry.mcp_runtime.registry import mount_server

    server = await db.get(McpServer, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    if server.status == "active":
        raise HTTPException(status_code=400, detail="Server is already active.")

    ds = await db.get(Datasource, server.datasource_id)
    if ds is None or ds.status != "ready":
        raise HTTPException(status_code=400, detail="Datasource is not ready.")

    await mount_server(server, ds)
    server.status = "active"
    await db.commit()
    await db.refresh(server)
    return McpServerSchema.model_validate(server)


@router.post("/{server_id}/stop", response_model=McpServerSchema)
async def stop_mcp_server(
    server_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> McpServerSchema:
    """Stop an active MCP server, unmounting its SSE endpoint."""
    from mcp_foundry.mcp_runtime.registry import unmount_server

    server = await db.get(McpServer, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")
    if server.status != "active":
        raise HTTPException(status_code=400, detail="Server is not active.")

    unmount_server(str(server_id))
    server.status = "stopped"
    await db.commit()
    await db.refresh(server)
    return McpServerSchema.model_validate(server)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_server(server_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    """Delete an MCP server config. Stop it first if active."""
    from mcp_foundry.mcp_runtime.registry import unmount_server

    server = await db.get(McpServer, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="MCP server not found")

    if server.status == "active":
        unmount_server(str(server_id))

    await db.delete(server)
    await db.commit()
