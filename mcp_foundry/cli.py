import json
import uuid
from typing import Annotated

import httpx
import typer

app = typer.Typer(help="MCP Foundry CLI - Manage MCP servers and datasources")
API_BASE = "http://localhost:8000"


def _handle_response(response: httpx.Response, success_msg: str):
    try:
        response.raise_for_status()
        data = response.json()
        typer.secho(f"✅ {success_msg}", fg=typer.colors.GREEN)
        typer.echo(json.dumps(data, indent=2))
        return data
    except httpx.HTTPError as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        if hasattr(response, "text") and response.text:
            try:
                err_data = response.json()
                typer.echo(json.dumps(err_data, indent=2))
            except Exception as e:
                typer.echo(response.text)
                raise typer.Exit(1) from e


@app.command("list")
def list_servers():
    """List all MCP servers."""
    with httpx.Client() as client:
        response = client.get(f"{API_BASE}/mcp-servers")
        _handle_response(response, "Servers retrieved successfully:")


@app.command("create-generic")
def create_generic_server(
    name: Annotated[str, typer.Argument(help="Name of the MCP server")],
    tools_config: Annotated[str, typer.Argument(help="Path to JSON file containing tools config")],
    description: Annotated[
        str, typer.Option(help="Description of the server tools")
    ] = "Generic tools server",
):
    """Create an MCP server with generic tool configuration from a JSON file."""
    try:
        with open(tools_config) as f:
            config_data = json.load(f)
    except Exception as e:
        typer.secho(f"❌ Failed to read tools config file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1) from e

    payload = {
        "name": name,
        "tools_config": config_data,
        "tool_description": description,
    }

    with httpx.Client() as client:
        response = client.post(f"{API_BASE}/mcp-servers", json=payload)
        _handle_response(response, "Server created successfully:")


@app.command("deploy")
def deploy_server(
    server_id: Annotated[uuid.UUID, typer.Argument(help="ID of the server to deploy")],
):
    """Deploy an MCP server and make it active."""
    with httpx.Client() as client:
        response = client.post(f"{API_BASE}/mcp-servers/{server_id}/deploy")
        _handle_response(response, "Server deployed successfully:")


@app.command("stop")
def stop_server(server_id: Annotated[uuid.UUID, typer.Argument(help="ID of the server to stop")]):
    """Stop an active MCP server."""
    with httpx.Client() as client:
        response = client.post(f"{API_BASE}/mcp-servers/{server_id}/stop")
        _handle_response(response, "Server stopped successfully:")


@app.command("delete")
def delete_server(
    server_id: Annotated[uuid.UUID, typer.Argument(help="ID of the server to delete")],
):
    """Delete an MCP server."""
    with httpx.Client() as client:
        response = client.delete(f"{API_BASE}/mcp-servers/{server_id}")
        if response.status_code == 204:
            typer.secho("✅ Server deleted successfully", fg=typer.colors.GREEN)
        else:
            _handle_response(response, "Server deleted:")


if __name__ == "__main__":
    app()
