from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request) -> dict:
    artifacts_loaded = getattr(request.app.state, "artifacts_loaded", False)
    movie_count = 0
    if artifacts_loaded:
        movie_count = len(request.app.state.movie_repository.all())

    return {
        "status": "ok" if artifacts_loaded else "degraded",
        "artifacts_loaded": artifacts_loaded,
        "movie_count": movie_count,
        "startup_seconds": getattr(request.app.state, "startup_seconds", None),
    }
