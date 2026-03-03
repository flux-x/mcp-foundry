import asyncio
import uuid
from datetime import UTC, datetime

from mcp_foundry.core.database import async_session_factory
from mcp_foundry.models.datasource import Datasource
from mcp_foundry.models.scraping_job import ScrapingJob
from mcp_foundry.scraping.celery_app import celery_app
from mcp_foundry.scraping.ingestion import ingest_pages
from mcp_foundry.scraping.scraper import scrape_url


@celery_app.task(bind=True, max_retries=0)
def run_scraping_job(self, job_id: str) -> dict:
    """Scrape and ingest a datasource; update job and datasource status.

    Args:
        job_id: UUID string of the ScrapingJob to run.

    Returns:
        Dict with status and pages_scraped.
    """
    return asyncio.run(_async_run(job_id))


async def _async_run(job_id: str) -> dict:
    async with async_session_factory() as session:
        job = await session.get(ScrapingJob, uuid.UUID(job_id))
        if job is None:
            return {"status": "error", "error": "Job not found"}

        datasource = await session.get(Datasource, job.datasource_id)
        if datasource is None:
            return {"status": "error", "error": "Datasource not found"}

        job.status = "running"
        job.started_at = datetime.now(tz=UTC)
        datasource.status = "scraping"
        await session.commit()

        try:
            pages = await scrape_url(datasource.url)
            await ingest_pages(
                pages,
                datasource.collection_name,
                str(datasource.id),
            )
            job.status = "completed"
            job.pages_scraped = len(pages)
            job.finished_at = datetime.now(tz=UTC)
            datasource.status = "ready"
            await session.commit()
            return {"status": "completed", "pages_scraped": len(pages)}
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            job.finished_at = datetime.now(tz=UTC)
            datasource.status = "error"
            await session.commit()
            return {"status": "failed", "error": str(exc)}
