"""Pydantic schemas for datasource API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class DatasourceCreate(BaseModel):
    name: str
    url: HttpUrl


class ScrapingJobSchema(BaseModel):
    id: uuid.UUID
    status: str
    pages_scraped: int
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None

    model_config = {"from_attributes": True}


class DatasourceSchema(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    status: str
    collection_name: str
    created_at: datetime
    updated_at: datetime
    latest_job: ScrapingJobSchema | None = None

    model_config = {"from_attributes": True}
