"""
Stage 2 of the pipeline: turn cleaned tabular data into one "feature document"
of text per movie, ready for TF-IDF vectorization.

Design choice: rather than a custom weighted-vectorizer scheme, we repeat
high-signal tokens (genres, director) N times in the joined text. TF-IDF then
naturally assigns them more term-frequency weight. This keeps the vectorizer
itself a plain, swappable scikit-learn TfidfVectorizer.

TMDB fields (overview, cast, director, keywords, production companies) are
optional inputs here — this module works with MovieLens data alone (genres +
tags) and simply enriches further if a tmdb_metadata frame is supplied. This
is the seam where Phase 2 (TMDB integration) plugs in without changing this
function's contract.
"""
from __future__ import annotations

import pandas as pd

from app.core.config import settings


def _repeat(token: str, times: int) -> str:
    return " ".join([token.replace(" ", "_")] * times)


def build_feature_documents(
    movies: pd.DataFrame,
    tags_agg: pd.DataFrame,
    tmdb_metadata: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Returns movies with an added `feature_text` column: the combined,
    weighted text blob used as TF-IDF input.

    Expects:
      movies: output of clean_movies() — has movieId, genres_list, clean_title
      tags_agg: output of aggregate_tags() — has movieId, tags_blob
      tmdb_metadata (optional): movieId, overview, cast (list[str]), director (str),
                                 keywords (list[str]), production_companies (list[str])
    """
    df = movies.merge(tags_agg, on="movieId", how="left")
    df["tags_blob"] = df["tags_blob"].fillna("")

    if tmdb_metadata is not None:
        df = df.merge(tmdb_metadata, on="movieId", how="left")

    for col in ("overview", "director"):
        if col not in df.columns:
            df[col] = ""
        else:
            # Left join leaves NaN (a float) for movies TMDB didn't cover —
            # normalize to "" so downstream string ops never see a float.
            df[col] = df[col].apply(lambda v: v if isinstance(v, str) else "")

    for col in ("cast", "keywords", "production_companies"):
        if col not in df.columns:
            df[col] = [[] for _ in range(len(df))]
        else:
            # Same issue for list columns: unmatched rows get NaN, not [].
            df[col] = df[col].apply(lambda v: v if isinstance(v, list) else [])

    def build_row(row) -> str:
        parts: list[str] = []

        genres_text = " ".join(_repeat(g, settings.genre_weight) for g in row["genres_list"])
        parts.append(genres_text)

        if row["director"]:
            parts.append(_repeat(row["director"], settings.director_weight))

        cast = row["cast"] or []
        parts.append(" ".join(_repeat(actor, 1) for actor in cast[:5]))

        keywords = row["keywords"] or []
        parts.append(" ".join(_repeat(kw, 1) for kw in keywords))

        companies = row["production_companies"] or []
        parts.append(" ".join(_repeat(c, 1) for c in companies[:2]))

        parts.append(row["tags_blob"])
        parts.append(row.get("overview") or "")

        return " ".join(p for p in parts if p).strip()

    df["feature_text"] = df.apply(build_row, axis=1)

    # A movie with zero signal (no genres, no tags, no TMDB data yet) still needs
    # *some* token so it doesn't produce an all-zero TF-IDF vector that breaks
    # cosine similarity — fall back to its own title tokens.
    empty_mask = df["feature_text"].str.strip() == ""
    df.loc[empty_mask, "feature_text"] = df.loc[empty_mask, "clean_title"]

    return df
