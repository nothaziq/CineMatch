from __future__ import annotations

from app.ml.pipeline.cleaning import (
    aggregate_ratings,
    aggregate_tags,
    clean_movies,
    clean_tags,
    compute_trending_scores,
)


class TestCleanMovies:
    def test_splits_genres_into_list(self, raw_movies_df):
        df = clean_movies(raw_movies_df)
        row = df[df["movieId"] == 1].iloc[0]
        assert row["genres_list"] == ["Action", "Sci-Fi"]

    def test_no_genres_listed_becomes_empty_list(self, raw_movies_df):
        df = clean_movies(raw_movies_df)
        row = df[df["movieId"] == 5].iloc[0]
        assert row["genres_list"] == []

    def test_extracts_year_and_strips_from_title(self, raw_movies_df):
        df = clean_movies(raw_movies_df)
        row = df[df["movieId"] == 1].iloc[0]
        assert row["year"] == 1999
        assert row["clean_title"] == "Galaxy Raiders"

    def test_drops_null_titles(self, raw_movies_df):
        with_null = raw_movies_df.copy()
        with_null.loc[len(with_null)] = [99, None, "Comedy"]
        df = clean_movies(with_null)
        assert 99 not in df["movieId"].values


class TestCleanTags:
    def test_lowercases_and_dedupes(self, raw_tags_df):
        df = clean_tags(raw_tags_df)
        # "space opera" and " Space Opera " for the same movie should collapse to one row.
        movie_1_tags = df[df["movieId"] == 1]
        assert len(movie_1_tags) == 1
        assert movie_1_tags.iloc[0]["tag"] == "space opera"

    def test_aggregate_tags_joins_per_movie(self, raw_tags_df):
        cleaned = clean_tags(raw_tags_df)
        agg = aggregate_tags(cleaned)
        row = agg[agg["movieId"] == 3].iloc[0]
        assert row["tags_blob"] == "tearjerker"


class TestAggregateRatings:
    def test_computes_mean_and_count(self, raw_ratings_df):
        agg = aggregate_ratings(raw_ratings_df)
        movie_1 = agg[agg["movieId"] == 1].iloc[0]
        assert movie_1["rating_count"] == 10
        assert movie_1["avg_rating"] == 4.5

    def test_movie_with_no_ratings_absent(self, raw_ratings_df):
        agg = aggregate_ratings(raw_ratings_df)
        assert 5 not in agg["movieId"].values


class TestComputeTrendingScores:
    def test_recent_activity_scores_highest(self, raw_ratings_df):
        """Movie 1 (10 ratings in the last 5 days) should outrank movie 6
        (20 ratings, but ~200 days old) even though movie 6 has more volume."""
        trending = compute_trending_scores(raw_ratings_df, window_days=90, half_life_days=21)
        movie_1_score = trending.loc[trending["movieId"] == 1, "trending_score"].iloc[0]
        assert 6 not in trending["movieId"].values  # entirely outside the 90-day window
        assert movie_1_score > 0

    def test_old_ratings_fall_outside_window(self, raw_ratings_df):
        trending = compute_trending_scores(raw_ratings_df, window_days=90, half_life_days=21)
        assert 6 not in trending["movieId"].values

    def test_movie_with_no_ratings_absent(self, raw_ratings_df):
        trending = compute_trending_scores(raw_ratings_df, window_days=90, half_life_days=21)
        assert 5 not in trending["movieId"].values

    def test_empty_ratings_returns_empty_frame(self):
        import pandas as pd

        empty = pd.DataFrame(columns=["movieId", "userId", "rating", "timestamp"])
        trending = compute_trending_scores(empty, window_days=90, half_life_days=21)
        assert trending.empty
        assert list(trending.columns) == ["movieId", "trending_score", "recent_rating_count"]

    def test_missing_timestamp_column_returns_empty_frame(self):
        import pandas as pd

        no_timestamp = pd.DataFrame({"movieId": [1], "userId": [1], "rating": [4.0]})
        trending = compute_trending_scores(no_timestamp, window_days=90, half_life_days=21)
        assert trending.empty

    def test_narrower_window_excludes_more(self, raw_ratings_df):
        """A 1-day window should catch strictly fewer of movie 1's ratings
        (or an equal-or-lower score) than a 90-day window."""
        wide = compute_trending_scores(raw_ratings_df, window_days=90, half_life_days=21)
        narrow = compute_trending_scores(raw_ratings_df, window_days=1, half_life_days=21)

        wide_score = wide.loc[wide["movieId"] == 1, "trending_score"].iloc[0]
        narrow_score = narrow.loc[narrow["movieId"] == 1, "trending_score"].iloc[0] if 1 in narrow["movieId"].values else 0
        assert narrow_score <= wide_score
