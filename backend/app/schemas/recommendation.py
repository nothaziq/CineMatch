from __future__ import annotations

from pydantic import BaseModel

from app.schemas.movie import MovieOut


class RecommendationOut(BaseModel):
    movie: MovieOut
    score: float
    explanation: str


class RecommendationBatchRequest(BaseModel):
    movie_ids: list[int]
    k: int = 10


class RecommendationListOut(BaseModel):
    seed_movie_ids: list[int]
    recommendations: list[RecommendationOut]
