from fastapi import FastAPI

from src.routes.data import router as data_router

app = FastAPI(
    title="Source Data API",
    version="1.0.0",
)

app.include_router(data_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
