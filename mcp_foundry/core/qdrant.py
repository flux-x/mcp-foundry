from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from mcp_foundry.core.config import settings

_client: AsyncQdrantClient | None = None


def get_qdrant() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
    return _client


async def ensure_collection(name: str, vector_size: int = settings.EMBEDDING_DIM) -> None:
    client = get_qdrant()
    existing = await client.get_collections()
    names = {c.name for c in existing.collections}
    if name not in names:
        await client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


async def delete_collection(name: str) -> None:
    await get_qdrant().delete_collection(name)
