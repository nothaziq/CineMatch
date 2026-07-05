"""
DI providers. Every route depends on these rather than constructing services
directly — makes routes trivially testable with overridden dependencies.
"""
from __future__ import annotations

from fastapi import Depends, Request

from app.exceptions.domain import ArtifactsNotLoadedError
from app.repositories.movie_repository import MovieRepository
from app.services.movie_service import MovieService
from app.services.recommendation_service import RecommendationService
from app.services.search_service import SearchService


def get_movie_repository(request: Request) -> MovieRepository:
    repo = getattr(request.app.state, "movie_repository", None)
    if repo is None:
        raise ArtifactsNotLoadedError()
    return repo


def get_movie_service(repo: MovieRepository = Depends(get_movie_repository)) -> MovieService:
    return MovieService(repo)


def get_search_service(
    repo: MovieRepository = Depends(get_movie_repository),
    movie_service: MovieService = Depends(get_movie_service),
) -> SearchService:
    return SearchService(repo, movie_service)


def get_recommendation_service(
    repo: MovieRepository = Depends(get_movie_repository),
    movie_service: MovieService = Depends(get_movie_service),
) -> RecommendationService:
    return RecommendationService(repo, movie_service)
