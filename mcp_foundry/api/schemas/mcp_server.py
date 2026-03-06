import uuid
from datetime import datetime

from pydantic import BaseModel


class McpServerCreate(BaseModel):
    name: str
    datasource_id: uuid.UUID | None = None
    tools_config: list[dict] | None = None
    tool_description: str = "Retrieve relevant documentation for a query."


class McpServerUpdate(BaseModel):
    name: str | None = None
    tool_description: str | None = None
    tools_config: list[dict] | None = None


class McpServerSchema(BaseModel):
    id: uuid.UUID
    name: str
    datasource_id: uuid.UUID | None
    tools_config: list[dict] | None
    tool_description: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
