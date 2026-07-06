"""
Application lifespan: loads the movie repository (and therefore the parquet
data + pickled recommender) exactly once when the app starts, and makes it
available via app.state for the rest of the app's lifetime. No per-request
reloading, no lazy loading — startup either succeeds with everything in
memory, or fails fast.
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.repositories.movie_repository import MovieRepository

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading movie repository and recommender artifacts...")
    start = time.perf_counter()
    try:
        app.state.movie_repository = MovieRepository.load()
        app.state.artifacts_loaded = True
        app.state.startup_seconds = time.perf_counter() - start
        logger.info(
            "Artifacts loaded: %d movies in memory (%.2fs).",
            len(app.state.movie_repository.all()),
            app.state.startup_seconds,
        )
    except FileNotFoundError as exc:
        # Don't crash the whole process — health check should be able to
        # report "not ready" rather than the server failing to bind at all.
        logger.error("Failed to load artifacts: %s", exc)
        app.state.movie_repository = None
        app.state.artifacts_loaded = False
        app.state.startup_seconds = time.perf_counter() - start

    yield

    logger.info("Shutting down.")
