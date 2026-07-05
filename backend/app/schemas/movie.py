"""
Response schemas — the API's public contract. The frontend's TypeScript
types should mirror these field-for-field.
"""
from __future__ import annotations

from pydantic import BaseModel


class MovieOut(BaseModel):
    """Lightweight shape used in lists (browse, search, trending, etc.)."""

    movie_id: int
    title: str
    year: int | None = None
    genres: list[str]
    avg_rating: float
    rating_count: int
    poster_url: str | None = None


class MovieDetailOut(MovieOut):
    """Full shape used on the movie detail page."""

    overview: str = ""
    director: str = ""
    cast: list[str] = []
    keywords: list[str] = []
    production_companies: list[str] = []
    runtime: int | None = None
    release_date: str | None = None
    backdrop_url: str | None = None
    tmdb_id: int | None = None
    imdb_id: str | None = None


class PaginatedMovies(BaseModel):
    items: list[MovieOut]
    page: int
    page_size: int
    total_items: int
    total_pages: int


class GenreCount(BaseModel):
    genre: str
    count: int
