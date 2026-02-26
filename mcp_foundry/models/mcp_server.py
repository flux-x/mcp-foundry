"""McpServer ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from mcp_foundry.core.database import Base


class McpServer(Base):
    """Represents a deployable MCP server backed by a Qdrant collection."""

    __tablename__ = "mcp_servers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    datasource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasources.id", ondelete="CASCADE"), nullable=False
    )
    tool_description: Mapped[str] = mapped_column(
        Text, nullable=False, default="Retrieve relevant documentation for a query."
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="stopped")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
