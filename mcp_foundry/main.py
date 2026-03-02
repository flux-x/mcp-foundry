from contextlib import asynccontextmanager

from fastapi import FastAPI

from mcp_foundry.api import datasources, mcp_servers
from mcp_foundry.core.config import settings
from mcp_foundry.mcp_runtime.registry import restore_active_servers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await restore_active_servers(app)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(datasources.router)
app.include_router(mcp_servers.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
