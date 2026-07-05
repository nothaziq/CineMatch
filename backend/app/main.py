from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import routes_health, routes_movies, routes_recommendations
from app.core.lifespan import lifespan
from app.middleware.error_handler import register_error_handlers

app = FastAPI(
    title="CineMatch API",
    description="Content-based movie recommendation API powered by MovieLens + TMDB.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite/CRA dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(routes_health.router, prefix="/api/v1")
app.include_router(routes_movies.router, prefix="/api/v1")
app.include_router(routes_recommendations.router, prefix="/api/v1")
