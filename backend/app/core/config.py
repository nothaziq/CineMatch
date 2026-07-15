"""
Central configuration for paths and pipeline parameters.

Keeping every path in one place means the pipeline scripts, the repositories,
and the FastAPI lifespan hook all agree on where data lives — no hardcoded
strings scattered across modules.
"""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Root of the backend/app package
    app_dir: Path = Path(__file__).resolve().parent.parent

    # Raw MovieLens CSVs — place movies.csv, ratings.csv, tags.csv, links.csv here
    raw_data_dir: Path = app_dir / "data" / "raw"

    # Cleaned, feature-engineered parquet output
    processed_data_dir: Path = app_dir / "data" / "processed"

    # Final pickled artifacts consumed by FastAPI at startup
    artifacts_dir: Path = app_dir / "data" / "artifacts"

    # CORS — comma-separated list of allowed origins, e.g.
    # "https://cinematch.vercel.app,https://your-custom-domain.com".
    # Set this via the CORS_ORIGINS env var in Railway. Localhost dev
    # servers are always allowed on top of whatever's configured here.
    cors_origins_raw: str = Field(default="", alias="CORS_ORIGINS")

    # Optional regex to allow an entire family of origins (e.g. every Vercel
    # preview deployment for this project: r"https://cinematch-.*\.vercel\.app").
    # Set via CORS_ORIGIN_REGEX env var. Leave empty to disable.
    cors_origin_regex: str = Field(default="", alias="CORS_ORIGIN_REGEX")

    @property
    def cors_origins(self) -> list[str]:
        dev_defaults = ["http://localhost:5173", "http://localhost:3000"]
        extra = [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]
        return dev_defaults + extra

    # TMDB
    tmdb_api_key: str = ""
    tmdb_access_token: str = ""  # v4 Bearer token — preferred over the v3 api_key query param
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p"
    tmdb_cache_dir: Path = app_dir / "data" / "tmdb_cache"
    tmdb_requests_per_window: int = 40  # TMDB's documented free-tier burst limit
    tmdb_window_seconds: float = 1.0

    # ML pipeline params
    tfidf_max_features: int = 20_000
    similarity_top_k: int = 30  # neighbors stored per movie

    # Trending signal params. MovieLens timestamps are historical (the dataset
    # was frozen years ago), so "recent" is always relative to the dataset's
    # own most recent rating timestamp, never wall-clock time.
    trending_window_days: int = 90  # only ratings within this window count at all
    trending_half_life_days: int = 21  # exponential recency decay inside the window

    # IMDB-style Bayesian weighted rating for "top rated" (see
    # compute_weighted_ratings in cleaning.py). None means "derive m from the
    # data itself" (the median rating count among rated movies) rather than a
    # fixed magic number — set an explicit int here to override that.
    bayesian_prior_votes: int | None = None

    # Genre feature weighting — repeating a token in the combined text document
    # increases its TF-IDF weight without needing a separate weighted-vectorizer scheme.
    genre_weight: int = 3
    director_weight: int = 2

    class Config:
        env_file = ".env"


settings = Settings()
