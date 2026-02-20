from fastapi import FastAPI

from mcp_foundry.core.config import settings

app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
