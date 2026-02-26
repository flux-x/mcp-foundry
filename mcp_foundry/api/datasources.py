"""REST API router for datasource management."""

import contextlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_foundry.api.schemas.datasource import DatasourceCreate, DatasourceSchema
from mcp_foundry.core.database import get_db
from mcp_foundry.core.qdrant import delete_collection
from mcp_foundry.models.datasource import Datasource
from mcp_foundry.models.scraping_job import ScrapingJob
from mcp_foundry.scraping.tasks import run_scraping_job

router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.post("", response_model=DatasourceSchema, status_code=status.HTTP_201_CREATED)
async def create_datasource(
    body: DatasourceCreate, db: AsyncSession = Depends(get_db)
) -> DatasourceSchema:
    """Create a datasource and enqueue a scraping job."""
    ds = Datasource(
        name=body.name,
        url=str(body.url),
        status="pending",
        collection_name=f"ds_{uuid.uuid4().hex}",
    )
    db.add(ds)
    await db.flush()

    job = ScrapingJob(datasource_id=ds.id)
    db.add(job)
    await db.commit()
    await db.refresh(ds)
    await db.refresh(job)

    run_scraping_job.delay(str(job.id))

    result = DatasourceSchema.model_validate(ds)
    result.latest_job = None
    return result


@router.get("", response_model=list[DatasourceSchema])
async def list_datasources(db: AsyncSession = Depends(get_db)) -> list[DatasourceSchema]:
    """List all datasources."""
    rows = await db.execute(select(Datasource).order_by(Datasource.created_at.desc()))
    return [DatasourceSchema.model_validate(ds) for ds in rows.scalars()]


@router.get("/{datasource_id}", response_model=DatasourceSchema)
async def get_datasource(
    datasource_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> DatasourceSchema:
    """Get a datasource with its latest scraping job status."""
    ds = await db.get(Datasource, datasource_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Datasource not found")

    job_row = await db.execute(
        select(ScrapingJob)
        .where(ScrapingJob.datasource_id == datasource_id)
        .order_by(ScrapingJob.started_at.desc())
        .limit(1)
    )
    job = job_row.scalar_one_or_none()

    result = DatasourceSchema.model_validate(ds)
    if job:
        from mcp_foundry.api.schemas.datasource import ScrapingJobSchema

        result.latest_job = ScrapingJobSchema.model_validate(job)
    return result


@router.delete("/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_datasource(datasource_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a datasource and its Qdrant collection."""
    ds = await db.get(Datasource, datasource_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Datasource not found")

    with contextlib.suppress(Exception):
        await delete_collection(ds.collection_name)

    await db.delete(ds)
    await db.commit()
