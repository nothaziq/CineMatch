"""
Recommendation service: orchestrates the ML engine (via RecommenderStrategy,
resolved by whatever's loaded on the repository) and formats results.

Note this depends on RecommenderStrategy's interface, not ContentBasedRecommender
directly — swapping in a collaborative/hybrid engine later means changing what
MovieRepository.load() constructs, not this service.
"""
from __future__ import annotations

from app.exceptions.domain import MovieNotFoundError
from app.ml.engine.base import Recommendation
from app.repositories.movie_repository import MovieRepository
from app.schemas.recommendation import RecommendationListOut, RecommendationOut
from app.services.movie_service import MovieService


def _build_explanation(rec: Recommendation) -> str:
    if not rec.shared_features:
        return "Recommended based on overall content similarity."
    if len(rec.shared_features) == 1:
        return f"Recommended because it shares {rec.shared_features[0]}."
    joined = ", ".join(rec.shared_features[:-1]) + f", and {rec.shared_features[-1]}"
    return f"Recommended because it shares {joined}."


class RecommendationService:
    def __init__(self, repo: MovieRepository, movie_service: MovieService) -> None:
        self.repo = repo
        self.movie_service = movie_service

    def recommend_for_movie(self, movie_id: int, k: int = 10) -> RecommendationListOut:
        # Raises MovieNotFoundError if invalid — let it propagate to the error middleware.
        self.repo.get_by_id(movie_id)

        raw_recs = self.repo.recommender.recommend(movie_id, k=k)
        return self._to_response([movie_id], raw_recs)

    def recommend_for_multiple(self, movie_ids: list[int], k: int = 10) -> RecommendationListOut:
        for mid in movie_ids:
            self.repo.get_by_id(mid)  # validates every seed exists; raises MovieNotFoundError otherwise

        raw_recs = self.repo.recommender.recommend_for_multiple(movie_ids, k=k)
        return self._to_response(movie_ids, raw_recs)

    def _to_response(self, seed_ids: list[int], raw_recs: list[Recommendation]) -> RecommendationListOut:
        recommendations: list[RecommendationOut] = []
        for rec in raw_recs:
            try:
                row = self.repo.get_by_id(rec.movie_id)
            except MovieNotFoundError:
                continue
            movie_out = self.movie_service.to_movie_out(row)
            recommendations.append(
                RecommendationOut(
                    movie=movie_out,
                    score=rec.score,
                    explanation=_build_explanation(rec),
                )
            )
        return RecommendationListOut(seed_movie_ids=seed_ids, recommendations=recommendations)
