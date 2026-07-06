"""
Entrypoint for the offline build pipeline.

Run this whenever MovieLens data changes or the pipeline logic is updated.
FastAPI never runs this at request time — it only loads what this script
produces. Run as:

    python -m app.ml.pipeline.build_artifacts
"""
from __future__ import annotations

import logging
import sys
import time

import pandas as pd

from app.core.config import settings
from app.ml.engine.content_based import ContentBasedRecommender
from app.ml.pipeline.cleaning import (
    aggregate_ratings,
    aggregate_tags,
    clean_movies,
    clean_tags,
    compute_trending_scores,
    compute_weighted_ratings,
    load_links,
    load_movies,
    load_ratings,
    load_tags,
)
from app.ml.pipeline.feature_engineering import build_feature_documents
from app.ml.vectorizer import FeatureVectorizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run() -> None:
    start = time.time()
    raw_dir = settings.raw_data_dir

    for required_file in ("movies.csv", "ratings.csv", "tags.csv", "links.csv"):
        if not (raw_dir / required_file).exists():
            logger.error(
                "Missing %s in %s. Place MovieLens 32M CSVs there before running the build.",
                required_file,
                raw_dir,
            )
            sys.exit(1)

    logger.info("Loading raw MovieLens data from %s", raw_dir)
    movies_raw = load_movies(raw_dir)
    ratings_raw = load_ratings(raw_dir)
    tags_raw = load_tags(raw_dir)
    links_raw = load_links(raw_dir)

    logger.info("Cleaning...")
    movies = clean_movies(movies_raw)
    tags = clean_tags(tags_raw)
    tags_agg = aggregate_tags(tags)
    ratings_agg = aggregate_ratings(ratings_raw)
    ratings_agg, global_mean_rating, prior_votes_used = compute_weighted_ratings(
        ratings_agg, prior_votes=settings.bayesian_prior_votes
    )
    logger.info(
        "Weighted rating prior: C (global mean rating) = %.3f, m (prior votes) = %.1f",
        global_mean_rating,
        prior_votes_used,
    )
    trending_agg = compute_trending_scores(
        ratings_raw,
        window_days=settings.trending_window_days,
        half_life_days=settings.trending_half_life_days,
    )

    movies = movies.merge(ratings_agg, on="movieId", how="left")
    movies["avg_rating"] = movies["avg_rating"].fillna(0.0)
    movies["rating_count"] = movies["rating_count"].fillna(0).astype(int)
    # A movie with zero ratings has no evidence at all — the Bayesian formula
    # at v=0 reduces to exactly C (the global mean), so that's what an
    # unrated movie should score, not 0.0 (which would misrepresent it as
    # the worst-reviewed movie in the catalog).
    movies["weighted_rating"] = movies["weighted_rating"].fillna(global_mean_rating)
    movies = movies.merge(trending_agg, on="movieId", how="left")
    movies["trending_score"] = movies["trending_score"].fillna(0.0)
    movies["recent_rating_count"] = movies["recent_rating_count"].fillna(0).astype(int)
    movies = movies.merge(links_raw, on="movieId", how="left")

    tmdb_metadata = None
    tmdb_cache_path = settings.processed_data_dir / "tmdb_metadata.parquet"
    if tmdb_cache_path.exists():
        logger.info("Loading previously-enriched TMDB metadata from %s", tmdb_cache_path)
        tmdb_metadata = pd.read_parquet(tmdb_cache_path)
    elif settings.tmdb_access_token or settings.tmdb_api_key:
        logger.info(
            "TMDB credentials found but no cached metadata yet. Run "
            "`python -m app.ml.pipeline.enrich_with_tmdb` first, then re-run "
            "this build for richer features. Continuing with genres/tags only for now."
        )
    else:
        logger.info("No TMDB credentials configured — building features from genres/tags only.")

    logger.info("Building feature documents...")
    featured = build_feature_documents(movies, tags_agg, tmdb_metadata=tmdb_metadata)
    # Director column doesn't exist yet without TMDB — placeholder for the merge seam.
    if "director" not in featured.columns:
        featured["director"] = ""

    logger.info("Vectorizing %d movies...", len(featured))
    vectorizer = FeatureVectorizer()
    tfidf_matrix = vectorizer.fit_transform(featured["feature_text"])

    logger.info("Building nearest-neighbor recommendation index (top_k=%d)...", settings.similarity_top_k)
    movie_features = featured.set_index("movieId")[["genres_list", "director", "clean_title"]]
    recommender = ContentBasedRecommender(
        tfidf_matrix=tfidf_matrix,
        movie_ids=featured["movieId"].tolist(),
        movie_features=movie_features,
        top_k=settings.similarity_top_k,
    )

    settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
    featured.drop(columns=["feature_text"]).to_parquet(
        settings.processed_data_dir / "movies_processed.parquet", index=False
    )

    recommender.save(settings.artifacts_dir)

    elapsed = time.time() - start
    logger.info("Done in %.1fs. Artifacts written to %s", elapsed, settings.artifacts_dir)


if __name__ == "__main__":
    run()
