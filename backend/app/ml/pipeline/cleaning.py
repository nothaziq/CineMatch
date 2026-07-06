"""
Stage 1 of the pipeline: load raw MovieLens CSVs and clean them.

Responsibilities here are strictly "make the data trustworthy" —
no feature engineering, no vectorization. That separation means we can
unit test cleaning rules (e.g. "drop movies with no genres") independently
of anything ML-related.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_MOVIE_COLUMNS = {"movieId", "title", "genres"}
REQUIRED_RATING_COLUMNS = {"userId", "movieId", "rating"}
REQUIRED_TAG_COLUMNS = {"userId", "movieId", "tag"}
REQUIRED_LINKS_COLUMNS = {"movieId", "imdbId", "tmdbId"}


def _validate_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def load_movies(raw_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_dir / "movies.csv")
    _validate_columns(df, REQUIRED_MOVIE_COLUMNS, "movies.csv")
    return df


def load_ratings(raw_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_dir / "ratings.csv")
    _validate_columns(df, REQUIRED_RATING_COLUMNS, "ratings.csv")
    return df


def load_tags(raw_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_dir / "tags.csv")
    _validate_columns(df, REQUIRED_TAG_COLUMNS, "tags.csv")
    return df


def load_links(raw_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_dir / "links.csv")
    _validate_columns(df, REQUIRED_LINKS_COLUMNS, "links.csv")
    return df


def clean_movies(movies: pd.DataFrame) -> pd.DataFrame:
    """
    - Drop rows with null titles (unusable).
    - Normalize genres: MovieLens uses "(no genres listed)" as a sentinel —
      convert to an empty list rather than treating it as a real genre.
    - Extract release year from the "Title (Year)" convention into its own column.
    """
    df = movies.dropna(subset=["title"]).copy()

    df["genres_list"] = df["genres"].apply(
        lambda g: [] if g == "(no genres listed)" else g.split("|")
    )

    year_extract = df["title"].str.extract(r"\((\d{4})\)\s*$")
    df["year"] = pd.to_numeric(year_extract[0], errors="coerce").astype("Int64")
    df["clean_title"] = df["title"].str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True)

    df = df.drop_duplicates(subset=["movieId"])
    logger.info("Cleaned movies: %d rows (from %d raw)", len(df), len(movies))
    return df


def clean_tags(tags: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, strip whitespace, drop nulls/empties, dedupe per movie."""
    df = tags.dropna(subset=["tag"]).copy()
    df["tag"] = df["tag"].str.strip().str.lower()
    df = df[df["tag"] != ""]
    df = df.drop_duplicates(subset=["movieId", "tag"])
    return df


def aggregate_ratings(ratings: pd.DataFrame) -> pd.DataFrame:
    """
    Per-movie rating stats used for popularity/top-rated ranking and,
    later, as a Bayesian-adjusted "weighted rating" (IMDB-style) so that
    a movie with 3 five-star ratings doesn't outrank one with 50,000 ratings
    averaging 4.5.
    """
    agg = ratings.groupby("movieId")["rating"].agg(["mean", "count"]).reset_index()
    agg = agg.rename(columns={"mean": "avg_rating", "count": "rating_count"})
    return agg


def compute_trending_scores(
    ratings: pd.DataFrame,
    window_days: int,
    half_life_days: int,
) -> pd.DataFrame:
    """
    Recency-windowed trending signal, built from ratings.csv's `timestamp`
    column (Unix epoch seconds).

    "Now" is the dataset's own max timestamp, not wall-clock time — MovieLens
    dumps are frozen snapshots, so treating real-world "today" as the
    reference point would put every rating outside the window and make
    everything score zero.

    Only ratings within `window_days` of that reference point count at all;
    within the window, each rating is weighted by exponential decay based on
    its age, so a movie getting rated heavily in the last week outranks one
    with the same volume spread evenly across the whole window. Movies with
    no ratings in the window naturally get a score of 0 (dropped from the
    groupby entirely, filled in by the caller).

    Returns columns: movieId, trending_score, recent_rating_count.
    """
    if "timestamp" not in ratings.columns or ratings.empty:
        return pd.DataFrame(columns=["movieId", "trending_score", "recent_rating_count"])

    reference_time = ratings["timestamp"].max()
    window_seconds = window_days * 86400
    half_life_seconds = max(half_life_days, 1) * 86400

    recent = ratings[ratings["timestamp"] >= reference_time - window_seconds].copy()
    if recent.empty:
        return pd.DataFrame(columns=["movieId", "trending_score", "recent_rating_count"])

    age_seconds = reference_time - recent["timestamp"]
    # Standard exponential decay: weight halves every `half_life_days`.
    recent["_decay_weight"] = 0.5 ** (age_seconds / half_life_seconds)

    grouped = recent.groupby("movieId").agg(
        trending_score=("_decay_weight", "sum"),
        recent_rating_count=("_decay_weight", "count"),
    ).reset_index()
    return grouped


def aggregate_tags(tags: pd.DataFrame) -> pd.DataFrame:
    """Collapse all tags for a movie into a single space-joined string per movieId."""
    grouped = tags.groupby("movieId")["tag"].apply(lambda tags_: " ".join(tags_)).reset_index()
    grouped = grouped.rename(columns={"tag": "tags_blob"})
    return grouped
