from __future__ import annotations

from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import MovieOut
from app.services.movie_service import MovieService


class SearchService:
    def __init__(self, repo: MovieRepository, movie_service: MovieService) -> None:
        self.repo = repo
        self.movie_service = movie_service

    def search(self, query: str, limit: int = 20) -> list[MovieOut]:
        query = query.strip()
        if not query:
            return []
        rows = self.repo.search_by_title(query, limit=limit)
        return [self.movie_service.to_movie_out(row) for _, row in rows.iterrows()]
