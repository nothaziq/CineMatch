"""
Thin wrapper around scikit-learn's TfidfVectorizer.

Kept as its own module (rather than inlined in build_artifacts.py) so the
vectorization strategy can be swapped — e.g. for an embedding-based approach
later — without touching the pipeline orchestration script.
"""
from __future__ import annotations

import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import settings


class FeatureVectorizer:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=settings.tfidf_max_features,
            stop_words="english",
            ngram_range=(1, 1),
        )

    def fit_transform(self, feature_texts: pd.Series) -> csr_matrix:
        return self.vectorizer.fit_transform(feature_texts)

    def get_feature_names(self) -> list[str]:
        return list(self.vectorizer.get_feature_names_out())
