"""
Strategy interface for recommendation engines.

Anything that implements `.recommend()` can be dropped into
`recommendation_service.py` via `registry.py` without the API layer or
frontend ever knowing which algorithm is running underneath. This is the
seam that lets collaborative filtering or a hybrid model replace/join
content-based recommendations later.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Recommendation:
    movie_id: int
    score: float
    shared_features: list[str]  # e.g. ["Sci-Fi", "Christopher Nolan"] — used to build the explanation string


class RecommenderStrategy(ABC):
    @abstractmethod
    def recommend(self, movie_id: int, k: int = 10) -> list[Recommendation]:
        """Return up to k recommendations for the given movie_id, best first."""
        raise NotImplementedError

    @abstractmethod
    def recommend_for_multiple(self, movie_ids: list[int], k: int = 10) -> list[Recommendation]:
        """
        Blend recommendations across several seed movies (the 'pick your
        favorites' flow). Default strategies may just average similarity
        scores across seeds and exclude the seeds themselves from results.
        """
        raise NotImplementedError
