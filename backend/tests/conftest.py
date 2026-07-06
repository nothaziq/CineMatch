"""
Shared fixtures for the backend test suite.

Everything here runs on small, synthetic, hand-built data — never the real
32M-row MovieLens set. That's a deliberate mirror of how this pipeline was
verified during the original build: prove the logic is correct on a data
shape you can eyeball first, then trust it at 87k-movie scale. These tests
never touch backend/app/data/raw or backend/app/data/artifacts.
"""
from __future__ import annotations

import time

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_movie_repository
from app.main import app
from app.ml.engine.content_based import ContentBasedRecommender
from app.ml.pipeline.cleaning import (
    aggregate_ratings,
    aggregate_tags,
    clean_movies,
    clean_tags,
    compute_trending_scores,
    compute_weighted_ratings,
)
from app.ml.pipeline.feature_engineering import build_feature_documents
from app.ml.vectorizer import FeatureVectorizer
from app.repositories.movie_repository import MovieRepository


@pytest.fixture
def raw_movies_df() -> pd.DataFrame:
    """Six movies spanning multiple genres, one with no genres listed."""
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3, 4, 5, 6],
            "title": [
                "Galaxy Raiders (1999)",
                "Galaxy Raiders II (2001)",
                "Heartfelt Melody (2005)",
                "Silent Cabin (2015)",
                "Mystery Untitled (2020)",
                "Old Classic (1950)",
            ],
            "genres": [
                "Action|Sci-Fi",
                "Action|Sci-Fi|Adventure",
                "Romance|Drama",
                "Horror|Thriller",
                "(no genres listed)",
                "Drama",
            ],
        }
    )


@pytest.fixture
def raw_ratings_df() -> pd.DataFrame:
    """
    Ratings with timestamps. Movie 1 has heavy *recent* activity (should
    trend), movie 6 has lots of old ratings only (popular but not trending),
    movie 5 has no ratings at all (should default to zero everywhere).
    """
    now = int(time.time())
    day = 86400
    rows: list[dict] = []

    # Movie 1: 10 ratings, all within the last 5 days -> should trend highest.
    for i in range(10):
        rows.append({"userId": i, "movieId": 1, "rating": 4.5, "timestamp": now - i * (day // 2)})

    # Movie 6: 20 ratings, all ~200 days old -> outside any reasonable trending window.
    for i in range(20):
        rows.append({"userId": 100 + i, "movieId": 6, "rating": 4.8, "timestamp": now - 200 * day - i * day})

    # Movie 2: a couple of recent ratings, lower volume than movie 1.
    for i in range(2):
        rows.append({"userId": 200 + i, "movieId": 2, "rating": 3.5, "timestamp": now - i * day})

    # Movie 3: a single 5.0 rating — a "fluke" perfect score with no real
    # sample size behind it. Plain average would let this outrank movie 6
    # (20 ratings averaging 4.8); the Bayesian weighted rating should not.
    rows.append({"userId": 300, "movieId": 3, "rating": 5.0, "timestamp": now - 10 * day})

    return pd.DataFrame(rows)


@pytest.fixture
def raw_tags_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "userId": [1, 2, 3],
            "movieId": [1, 2, 3],
            "tag": ["space opera", " Space Opera ", "tearjerker"],
        }
    )


@pytest.fixture
def raw_links_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3, 4, 5, 6],
            "imdbId": ["0000001", "0000002", "0000003", "0000004", "0000005", "0000006"],
            "tmdbId": [11, 12, 13, 14, None, 16],
        }
    )


@pytest.fixture
def built_movie_repository(raw_movies_df, raw_ratings_df, raw_tags_df, raw_links_df) -> MovieRepository:
    """
    Runs the real cleaning -> feature-engineering -> vectorization ->
    recommender pipeline end-to-end on synthetic data, entirely in memory
    (no parquet/pickle round-trip), and wraps the result in a real
    MovieRepository. This is the same code path build_artifacts.py runs,
    just skipping the disk I/O.
    """
    movies = clean_movies(raw_movies_df)
    tags = clean_tags(raw_tags_df)
    tags_agg = aggregate_tags(tags)
    ratings_agg = aggregate_ratings(raw_ratings_df)
    ratings_agg, global_mean_rating, _prior_m = compute_weighted_ratings(ratings_agg)
    trending_agg = compute_trending_scores(raw_ratings_df, window_days=90, half_life_days=21)

    movies = movies.merge(ratings_agg, on="movieId", how="left")
    movies["avg_rating"] = movies["avg_rating"].fillna(0.0)
    movies["rating_count"] = movies["rating_count"].fillna(0).astype(int)
    movies["weighted_rating"] = movies["weighted_rating"].fillna(global_mean_rating)
    movies = movies.merge(trending_agg, on="movieId", how="left")
    movies["trending_score"] = movies["trending_score"].fillna(0.0)
    movies["recent_rating_count"] = movies["recent_rating_count"].fillna(0).astype(int)
    movies = movies.merge(raw_links_df, on="movieId", how="left")

    featured = build_feature_documents(movies, tags_agg, tmdb_metadata=None)
    featured["director"] = ""

    vectorizer = FeatureVectorizer()
    tfidf_matrix = vectorizer.fit_transform(featured["feature_text"])

    movie_features = featured.set_index("movieId")[["genres_list", "director", "clean_title"]]
    recommender = ContentBasedRecommender(
        tfidf_matrix=tfidf_matrix,
        movie_ids=featured["movieId"].tolist(),
        movie_features=movie_features,
        top_k=10,
    )

    processed = featured.drop(columns=["feature_text"])
    return MovieRepository(processed, recommender)


@pytest.fixture
def client(built_movie_repository) -> TestClient:
    """
    TestClient with the movie repository dependency overridden to the
    synthetic in-memory one — never triggers the real lifespan hook, so no
    parquet/pickle files are read from disk during tests.
    """
    app.dependency_overrides[get_movie_repository] = lambda: built_movie_repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
