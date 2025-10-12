from fastapi import FastAPI

from src.core.config import settings

app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
