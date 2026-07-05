"""
Phase 1 recommender: TF-IDF + cosine-similarity nearest neighbors.

Uses sklearn's NearestNeighbors(metric="cosine") rather than computing a full
N x N similarity matrix. At MovieLens-32M scale (~87k movies) a full dense
matrix is wasteful; we only ever need "top-k similar movies" per lookup, so a
neighbor index is both faster to build and far smaller to persist.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from app.ml.engine.base import Recommendation, RecommenderStrategy


class ContentBasedRecommender(RecommenderStrategy):
    def __init__(
        self,
        tfidf_matrix: csr_matrix,
        movie_ids: list[int],
        movie_features: pd.DataFrame,  # indexed by movieId: genres_list, director, clean_title
        top_k: int = 30,
    ) -> None:
        self.movie_ids = movie_ids
        self.id_to_row = {mid: i for i, mid in enumerate(movie_ids)}
        self.movie_features = movie_features
        self.top_k = top_k

        self._model = NearestNeighbors(metric="cosine", algorithm="brute")
        self._model.fit(tfidf_matrix)
        self._tfidf_matrix = tfidf_matrix

    # ---- building the explanation string ----

    def _shared_features(self, movie_id_a: int, movie_id_b: int) -> list[str]:
        a = self.movie_features.loc[movie_id_a]
        b = self.movie_features.loc[movie_id_b]

        shared_genres = sorted(set(a["genres_list"]) & set(b["genres_list"]))
        shared: list[str] = list(shared_genres[:3])

        if a["director"] and a["director"] == b["director"]:
            shared.append(a["director"])

        return shared

    # ---- core lookups ----

    def recommend(self, movie_id: int, k: int = 10) -> list[Recommendation]:
        if movie_id not in self.id_to_row:
            return []

        row = self.id_to_row[movie_id]
        n_neighbors = min(k + 1, len(self.movie_ids))  # +1 because the movie itself is its own nearest neighbor
        distances, indices = self._model.kneighbors(
            self._tfidf_matrix[row], n_neighbors=n_neighbors
        )

        results: list[Recommendation] = []
        for dist, idx in zip(distances[0], indices[0]):
            candidate_id = self.movie_ids[idx]
            if candidate_id == movie_id:
                continue
            score = round(1.0 - float(dist), 4)  # cosine distance -> similarity
            results.append(
                Recommendation(
                    movie_id=candidate_id,
                    score=score,
                    shared_features=self._shared_features(movie_id, candidate_id),
                )
            )
        return results[:k]

    def recommend_for_multiple(self, movie_ids: list[int], k: int = 10) -> list[Recommendation]:
        seed_set = set(movie_ids)
        aggregated: dict[int, list[float]] = {}
        features_by_id: dict[int, list[str]] = {}

        for seed in movie_ids:
            for rec in self.recommend(seed, k=k * 2):  # over-fetch, then merge/rank
                if rec.movie_id in seed_set:
                    continue
                aggregated.setdefault(rec.movie_id, []).append(rec.score)
                features_by_id.setdefault(rec.movie_id, rec.shared_features)

        blended = [
            Recommendation(
                movie_id=mid,
                score=round(float(np.mean(scores)), 4),
                shared_features=features_by_id[mid],
            )
            for mid, scores in aggregated.items()
        ]
        blended.sort(key=lambda r: r.score, reverse=True)
        return blended[:k]

    # ---- persistence ----

    def save(self, artifacts_dir: Path) -> None:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        with open(artifacts_dir / "content_recommender.pkl", "wb") as f:
            pickle.dump(
                {
                    "tfidf_matrix": self._tfidf_matrix,
                    "movie_ids": self.movie_ids,
                    "movie_features": self.movie_features,
                    "top_k": self.top_k,
                },
                f,
            )

    @classmethod
    def load(cls, artifacts_dir: Path) -> "ContentBasedRecommender":
        with open(artifacts_dir / "content_recommender.pkl", "rb") as f:
            data = pickle.load(f)
        return cls(
            tfidf_matrix=data["tfidf_matrix"],
            movie_ids=data["movie_ids"],
            movie_features=data["movie_features"],
            top_k=data["top_k"],
        )
