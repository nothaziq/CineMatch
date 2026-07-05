"""
Movie service: orchestrates the repository and shapes results into the
API's schema types. This is where "business logic" lives — the repository
only knows how to fetch/filter raw rows, this service knows what a
MovieOut/MovieDetailOut should look like.
"""
from __future__ import annotations

import pandas as pd

from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import GenreCount, MovieDetailOut, MovieOut, PaginatedMovies


class MovieService:
    def __init__(self, repo: MovieRepository) -> None:
        self.repo = repo

    def to_movie_out(self, row: pd.Series) -> MovieOut:
        return MovieOut(
            movie_id=int(row["movieId"]),
            title=row["clean_title"],
            year=None if pd.isna(row.get("year")) else int(row["year"]),
            genres=row["genres_list"],
            avg_rating=round(float(row.get("avg_rating", 0.0)), 2),
            rating_count=int(row.get("rating_count", 0)),
            poster_url=MovieRepository.poster_url(row),
        )

    def _to_list(self, value) -> list:
        if value is None:
            return []
        try:
            if pd.isna(value):
                return []
        except (TypeError, ValueError):
            pass  # value is array-like; pd.isna on an array raises/returns array, not a bool — fall through
        return list(value)

    def to_movie_detail_out(self, row: pd.Series) -> MovieDetailOut:
        base = self.to_movie_out(row)
        tmdb_id = row.get("tmdbId")
        return MovieDetailOut(
            **base.model_dump(),
            overview=row.get("overview") or "",
            director=row.get("director") or "",
            cast=self._to_list(row.get("cast")),
            keywords=self._to_list(row.get("keywords")),
            production_companies=self._to_list(row.get("production_companies")),
            runtime=None if pd.isna(row.get("runtime")) else int(row["runtime"]),
            release_date=row.get("release_date"),
            backdrop_url=MovieRepository.backdrop_url(row),
            tmdb_id=None if pd.isna(tmdb_id) else int(tmdb_id),
            imdb_id=None if pd.isna(row.get("imdbId")) else str(row.get("imdbId")),
        )

    def get_movie_detail(self, movie_id: int) -> MovieDetailOut:
        row = self.repo.get_by_id(movie_id)
        return self.to_movie_detail_out(row)

    def browse(
        self,
        genre: str | None = None,
        sort_by: str = "popularity",
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedMovies:
        page = max(page, 1)
        page_size = max(min(page_size, 100), 1)

        rows, total_items = self.repo.filter_and_sort(
            genre=genre, sort_by=sort_by, page=page, page_size=page_size
        )
        items = [self.to_movie_out(row) for _, row in rows.iterrows()]

        return PaginatedMovies(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=MovieRepository.total_pages(total_items, page_size),
        )

    def list_genres(self) -> list[GenreCount]:
        return [GenreCount(genre=g, count=int(c)) for g, c in self.repo.genre_counts()]
