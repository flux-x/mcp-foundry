from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler

from mcp_foundry.core.config import settings


def _same_domain(base: str, target: str) -> bool:
    return urlparse(base).netloc == urlparse(target).netloc


async def scrape_url(root_url: str) -> list[dict]:
    """Crawl root_url and linked same-domain pages, returning page dicts.

    Args:
        root_url: The entry-point URL to crawl.

    Returns:
        List of dicts with keys: url, title, text.
    """
    visited: set[str] = set()
    queue: list[str] = [root_url]
    results: list[dict] = []

    async with AsyncWebCrawler() as crawler:
        while queue and len(visited) < settings.SCRAPING_MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            try:
                result = await crawler.arun(url=url)
            except Exception:
                continue

            if not result.success:
                continue

            results.append(
                {
                    "url": url,
                    "title": result.metadata.get("title", ""),
                    "text": result.markdown or "",
                }
            )

            for link in result.links.get("internal", []):
                href = link.get("href", "")
                if not href:
                    continue
                absolute = urljoin(url, href).split("#")[0]
                if _same_domain(root_url, absolute) and absolute not in visited:
                    queue.append(absolute)

    return results
