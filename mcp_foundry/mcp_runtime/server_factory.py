"""Build MCP server ASGI apps for a given McpServer configuration."""

from mcp.server.fastmcp import FastMCP
from qdrant_client.models import FieldCondition, Filter, MatchValue

from mcp_foundry.core.embeddings import embed
from mcp_foundry.core.qdrant import get_qdrant
from mcp_foundry.models.datasource import Datasource
from mcp_foundry.models.mcp_server import McpServer

RETRIEVE_TOP_K = 5


def build_mcp_app(server: McpServer, datasource: Datasource) -> FastMCP:
    """Build a FastMCP app with a single retrieval tool for the given server config.

    Args:
        server: McpServer ORM instance.
        datasource: Associated Datasource ORM instance.

    Returns:
        Configured FastMCP instance.
    """
    mcp = FastMCP(name=server.name)
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

    return mcp
