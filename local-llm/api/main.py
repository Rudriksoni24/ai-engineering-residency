from fastapi import FastAPI

from api.routes.generation import router as generation_router
from api.routes.health import router as health_router


app = FastAPI(
    title="Local LLM Service",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(generation_router)