from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_recommendation_service
from app.schemas.recommendation import RecommendationBatchRequest, RecommendationListOut
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{movie_id}", response_model=RecommendationListOut)
def recommend_for_movie(
    movie_id: int,
    k: int = Query(default=10, ge=1, le=50),
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationListOut:
    return service.recommend_for_movie(movie_id, k=k)


@router.post("/batch", response_model=RecommendationListOut)
def recommend_for_multiple(
    request: RecommendationBatchRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationListOut:
    return service.recommend_for_multiple(request.movie_ids, k=request.k)
