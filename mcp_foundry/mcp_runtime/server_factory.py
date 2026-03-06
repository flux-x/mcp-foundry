import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field, create_model
from qdrant_client.models import FieldCondition, Filter, MatchValue

from mcp_foundry.core.embeddings import embed
from mcp_foundry.core.qdrant import get_qdrant
from mcp_foundry.models.datasource import Datasource
from mcp_foundry.models.mcp_server import McpServer

RETRIEVE_TOP_K = 5


def build_mcp_app(server: McpServer, datasource: Datasource | None) -> FastMCP:
    """Build a FastMCP app with configured tools.

    Args:
        server: McpServer ORM instance.
        datasource: Associated Datasource ORM instance (optional).

    Returns:
        Configured FastMCP instance.
    """
    mcp = FastMCP(name=server.name)

    if datasource:
        collection = datasource.collection_name
        ds_id = str(datasource.id)
        description = server.tool_description

        @mcp.tool(description=description)
        async def retrieve(query: str) -> str:
            """Search the documentation collection and return relevant context.

            Args:
                query: Natural language query to search for.

            Returns:
                Concatenated relevant text chunks.
            """
            vectors = embed([query])
            client = get_qdrant()
            results = await client.search(  # type: ignore
                collection_name=collection,
                query_vector=vectors[0],
                query_filter=Filter(
                    must=[FieldCondition(key="datasource_id", match=MatchValue(value=ds_id))]
                ),
                limit=RETRIEVE_TOP_K,
                with_payload=True,
            )
            if not results:
                return "No relevant documentation found."

            parts = []
            for hit in results:
                payload = hit.payload or {}
                parts.append(
                    f"### [{payload.get('title', 'Source')}]({payload.get('url', '')})\n"
                    f"{payload.get('text', '')}"
                )
            return "\n\n---\n\n".join(parts)

    if server.tools_config:
        for tool_cfg in server.tools_config:
            _register_generic_tool(mcp, tool_cfg)

    return mcp


def _register_generic_tool(mcp: FastMCP, config: dict) -> None:
    """Register a generic webhook-backed tool."""
    name = config.get("name")
    description = config.get("description", "")
    webhook_url = config.get("webhook_url")
    parameters_schema = config.get("parameters", {})

    if not name or not webhook_url:
        return

    # Build an actual Pydantic schema class from the jsonschema dict
    # so that fastmcp can inspect it appropriately.
    fields = {}
    properties = parameters_schema.get("properties", {})
    required = parameters_schema.get("required", [])

    for prop_name, prop_info in properties.items():
        prop_type = str
        if prop_info.get("type") == "integer":
            prop_type = int
        elif prop_info.get("type") == "number":
            prop_type = float
        elif prop_info.get("type") == "boolean":
            prop_type = bool

        if prop_name not in required:
            fields[prop_name] = (
                prop_type | None,
                Field(default=None, description=prop_info.get("description", "")),
            )
        else:
            fields[prop_name] = (
                prop_type,
                Field(..., description=prop_info.get("description", "")),
            )

    DynamicArgs = create_model(f"{name}_Args", **fields)

    # Use a closure wrapper to capture tool-specific routing config
    async def _dynamic_tool(**kwargs) -> str:
        # Pydantic validation handles parsing kwargs correctly
        validated_args = DynamicArgs(**kwargs)
        async with httpx.AsyncClient() as client:
            try:
                # Forward to generic webhook
                response = await client.post(webhook_url, json=validated_args.model_dump())
                response.raise_for_status()
                result = response.text
                return result
            except httpx.HTTPError as e:
                return f"Error executing tool {name}: {str(e)}"

    _dynamic_tool.__name__ = name
    _dynamic_tool.__doc__ = description

    # Manually pass the pydantic model schema directly or via signature if preferred
    # FastMCP uses standard Python type hints or Pydantic models for argument validation
    # the easiest way in Python 3.12+ for dynamic tools is overriding the signature.
    import inspect

    sig = inspect.signature(_dynamic_tool)
    new_params = []
    for f_name, (f_type, f_field) in fields.items():
        default = inspect.Parameter.empty if f_field.is_required() else f_field.default
        new_params.append(
            inspect.Parameter(
                f_name,
                inspect.Parameter.KEYWORD_ONLY,
                annotation=f_type,
                default=default,
            )
        )
    _dynamic_tool.__signature__ = sig.replace(parameters=new_params)  # type: ignore

    mcp.tool(name=name, description=description)(_dynamic_tool)
