import uuid

from qdrant_client.models import PointStruct

from mcp_foundry.core.embeddings import embed
from mcp_foundry.core.qdrant import ensure_collection, get_qdrant

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping fixed-size chunks by word count.

    Args:
        text: Raw text to chunk.

    Returns:
        List of text chunk strings.
    """
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start + CHUNK_SIZE
        chunks.append(" ".join(words[start:end]))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


async def ingest_pages(
    pages: list[dict],
    collection_name: str,
    datasource_id: str,
) -> int:
    """Chunk, embed, and upsert pages into a Qdrant collection.

    Args:
        pages: List of dicts with keys url, title, text.
        collection_name: Target Qdrant collection name.
        datasource_id: UUID string used as payload field for filtering.

    Returns:
        Total number of points upserted.
    """
    await ensure_collection(collection_name)
    client = get_qdrant()
    total = 0

    for page in pages:
        chunks = _chunk_text(page["text"])
        if not chunks:
            continue

        vectors = embed(chunks)
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "datasource_id": datasource_id,
                    "url": page["url"],
                    "title": page["title"],
                    "chunk_index": i,
                    "text": chunk,
                },
            )
            for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=False))
        ]
        await client.upsert(collection_name=collection_name, points=points)
        total += len(points)

    return total
