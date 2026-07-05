from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_movie_service, get_search_service
from app.schemas.movie import GenreCount, MovieDetailOut, MovieOut, PaginatedMovies
from app.services.movie_service import MovieService
from app.services.search_service import SearchService

router = APIRouter(prefix="/movies", tags=["movies"])

SortOption = Literal["popularity", "top_rated", "recent", "title"]


@router.get("", response_model=PaginatedMovies)
def list_movies(
    genre: str | None = Query(default=None),
    sort: SortOption = Query(default="popularity"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: MovieService = Depends(get_movie_service),
) -> PaginatedMovies:
    return service.browse(genre=genre, sort_by=sort, page=page, page_size=page_size)


@router.get("/search", response_model=list[MovieOut])
def search_movies(
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=50),
    service: SearchService = Depends(get_search_service),
) -> list[MovieOut]:
    return service.search(q, limit=limit)


@router.get("/trending", response_model=PaginatedMovies)
def trending_movies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: MovieService = Depends(get_movie_service),
) -> PaginatedMovies:
    # Phase 1: "trending" approximated by popularity (rating_count). A true
    # trending signal (recent rating velocity) needs ratings timestamps —
    # noted as a future-roadmap item, not faked here.
    return service.browse(sort_by="popularity", page=page, page_size=page_size)


@router.get("/popular", response_model=PaginatedMovies)
def popular_movies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: MovieService = Depends(get_movie_service),
) -> PaginatedMovies:
    return service.browse(sort_by="popularity", page=page, page_size=page_size)


@router.get("/top-rated", response_model=PaginatedMovies)
def top_rated_movies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: MovieService = Depends(get_movie_service),
) -> PaginatedMovies:
    return service.browse(sort_by="top_rated", page=page, page_size=page_size)


@router.get("/recent", response_model=PaginatedMovies)
def recent_movies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: MovieService = Depends(get_movie_service),
) -> PaginatedMovies:
    return service.browse(sort_by="recent", page=page, page_size=page_size)


@router.get("/genres", response_model=list[GenreCount])
def list_genres(service: MovieService = Depends(get_movie_service)) -> list[GenreCount]:
    return service.list_genres()


@router.get("/{movie_id}", response_model=MovieDetailOut)
def get_movie(movie_id: int, service: MovieService = Depends(get_movie_service)) -> MovieDetailOut:
    return service.get_movie_detail(movie_id)
