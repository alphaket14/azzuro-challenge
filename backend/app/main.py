import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import insights, properties, reviews, summary

app = FastAPI(title="Azzurro Hotels Review Intelligence API")

frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(properties.router)
app.include_router(reviews.router)
app.include_router(summary.router)
app.include_router(insights.router)


@app.get("/health")
def health():
    return {"status": "ok"}
