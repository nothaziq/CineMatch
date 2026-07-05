"""
In-memory repository for movie data.

Loaded once (see core/lifespan.py) from the parquet + pickle artifacts the
offline pipeline produces. This class only knows how to read/query that
in-memory data — no filtering rules, no business logic, no HTTP concerns.
Services depend on this, never the other way around.
"""
from __future__ import annotations

import math

import pandas as pd

from app.core.config import settings
from app.exceptions.domain import MovieNotFoundError
from app.ml.engine.content_based import ContentBasedRecommender
from app.repositories.tmdb_repository import TMDBRepository


class MovieRepository:
    def __init__(self, movies: pd.DataFrame, recommender: ContentBasedRecommender) -> None:
        self._movies = movies.set_index("movieId", drop=False)
        self._recommender = recommender

    @classmethod
    def load(cls) -> "MovieRepository":
        movies_path = settings.processed_data_dir / "movies_processed.parquet"
        if not movies_path.exists():
            raise FileNotFoundError(
                f"{movies_path} not found. Run `python -m app.ml.pipeline.build_artifacts` first."
            )
        movies = pd.read_parquet(movies_path)
        recommender = ContentBasedRecommender.load(settings.artifacts_dir)
        return cls(movies, recommender)

    @property
    def recommender(self) -> ContentBasedRecommender:
        return self._recommender

    def get_by_id(self, movie_id: int) -> pd.Series:
        if movie_id not in self._movies.index:
            raise MovieNotFoundError(movie_id)
        return self._movies.loc[movie_id]

    def get_many_by_ids(self, movie_ids: list[int]) -> pd.DataFrame:
        existing = [mid for mid in movie_ids if mid in self._movies.index]
        return self._movies.loc[existing]

    def all(self) -> pd.DataFrame:
        return self._movies

    def search_by_title(self, query: str, limit: int = 20) -> pd.DataFrame:
        mask = self._movies["clean_title"].str.contains(query, case=False, na=False, regex=False)
        return self._movies[mask].head(limit)

    def filter_and_sort(
        self,
        genre: str | None = None,
        sort_by: str = "popularity",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[pd.DataFrame, int]:
        df = self._movies

        if genre:
            df = df[df["genres_list"].apply(lambda gs: genre in gs)]

        sort_columns = {
            "popularity": ("rating_count", False),
            "top_rated": ("avg_rating", False),
            "recent": ("year", False),
            "title": ("clean_title", True),
        }
        col, ascending = sort_columns.get(sort_by, sort_columns["popularity"])
        df = df.sort_values(by=col, ascending=ascending, na_position="last")

        total_items = len(df)
        start = (page - 1) * page_size
        end = start + page_size
        return df.iloc[start:end], total_items

    def genre_counts(self) -> list[tuple[str, int]]:
        exploded = self._movies["genres_list"].explode().dropna()
        counts = exploded.value_counts()
        return list(counts.items())

    @staticmethod
    def total_pages(total_items: int, page_size: int) -> int:
        if page_size <= 0:
            return 0
        return math.ceil(total_items / page_size)

    @staticmethod
    def poster_url(row: pd.Series) -> str | None:
        return TMDBRepository.image_url(row.get("poster_path"), size="w500")

    @staticmethod
    def backdrop_url(row: pd.Series) -> str | None:
        return TMDBRepository.image_url(row.get("backdrop_path"), size="w1280")
