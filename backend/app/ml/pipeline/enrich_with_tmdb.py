"""
TMDB enrichment stage — run after cleaning, before feature engineering.

Reads movieId -> tmdbId from links.csv, fetches each movie's TMDB bundle
(cached to disk per movie so re-runs are free/resumable), and produces a
DataFrame in the exact shape build_feature_documents() expects via its
tmdb_metadata parameter.

Run standalone as:
    python -m app.ml.pipeline.enrich_with_tmdb

Or import enrich_movies() directly from build_artifacts.py once you're
ready to wire it into the full pipeline run.
"""
from __future__ import annotations

import logging
import time

import pandas as pd

from app.core.config import settings
from app.ml.pipeline.cleaning import load_links
from app.repositories.tmdb_repository import TMDBRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def enrich_movies(movie_ids: list[int] | None = None) -> pd.DataFrame:
    """
    Returns a DataFrame with columns:
    movieId, overview, director, cast, keywords, production_companies,
    poster_path, backdrop_path, runtime, release_date

    If movie_ids is None, enriches every movie found in links.csv.
    """
    links = load_links(settings.raw_data_dir)
    if movie_ids is not None:
        links = links[links["movieId"].isin(movie_ids)]

    # tmdbId can be null (a handful of MovieLens entries have no TMDB match)
    links = links.dropna(subset=["tmdbId"])
    links["tmdbId"] = links["tmdbId"].astype(int)

    repo = TMDBRepository()

    rows: list[dict] = []
    total = len(links)
    start = time.time()

    for i, (_, link_row) in enumerate(links.iterrows(), start=1):
        bundle = repo.fetch_movie_bundle(int(link_row["tmdbId"]))
        if bundle is None:
            continue

        feature_row = TMDBRepository.to_feature_row(bundle)
        feature_row["movieId"] = link_row["movieId"]
        rows.append(feature_row)

        if i % 50 == 0 or i == total:
            elapsed = time.time() - start
            logger.info("Enriched %d/%d movies (%.1fs elapsed)", i, total, elapsed)

    df = pd.DataFrame(rows)
    logger.info("TMDB enrichment complete: %d/%d movies enriched", len(df), total)
    return df


def run() -> None:
    df = enrich_movies()
    settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
    out_path = settings.processed_data_dir / "tmdb_metadata.parquet"
    df.to_parquet(out_path, index=False)
    logger.info("Saved TMDB metadata to %s", out_path)


if __name__ == "__main__":
    run()
