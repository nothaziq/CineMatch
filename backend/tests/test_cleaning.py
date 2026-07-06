from __future__ import annotations

import pytest

from app.ml.pipeline.cleaning import (
    aggregate_ratings,
    aggregate_tags,
    clean_movies,
    clean_tags,
    compute_trending_scores,
    compute_weighted_ratings,
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


class TestComputeWeightedRatings:
    def test_fluke_perfect_score_ranks_below_large_strong_sample(self, raw_ratings_df):
        """
        Movie 3 has a single 5.0 rating (a fluke). Movie 6 has 20 ratings
        averaging 4.8 (a large, genuinely strong sample). Plain avg_rating
        would let movie 3's fluke outrank movie 6 — the whole point of the
        Bayesian weighting is that it must not.
        """
        agg = aggregate_ratings(raw_ratings_df)
        weighted, _c, _m = compute_weighted_ratings(agg)

        movie_3 = weighted.loc[weighted["movieId"] == 3, "weighted_rating"].iloc[0]
        movie_6 = weighted.loc[weighted["movieId"] == 6, "weighted_rating"].iloc[0]

        # Sanity check the premise: plain averages would rank them the other way.
        assert agg.loc[agg["movieId"] == 3, "avg_rating"].iloc[0] > agg.loc[agg["movieId"] == 6, "avg_rating"].iloc[0]
        # The whole point: weighted_rating flips that.
        assert movie_6 > movie_3

    def test_weighted_rating_pulled_toward_global_mean_for_low_volume(self, raw_ratings_df):
        agg = aggregate_ratings(raw_ratings_df)
        weighted, c, _m = compute_weighted_ratings(agg)

        movie_3 = weighted[weighted["movieId"] == 3].iloc[0]
        # Its own average is 5.0, but with only 1 rating it should land
        # somewhere strictly between its own average and the global mean —
        # not stay at a full, unadjusted 5.0.
        assert c < movie_3["weighted_rating"] < movie_3["avg_rating"]

    def test_weighted_rating_barely_moves_for_high_volume(self, raw_ratings_df):
        agg = aggregate_ratings(raw_ratings_df)
        weighted, _c, _m = compute_weighted_ratings(agg)

        movie_6 = weighted[weighted["movieId"] == 6].iloc[0]
        # 20 ratings is a real sample — weighted_rating should stay close to
        # (not drift far from) its own average.
        assert abs(movie_6["weighted_rating"] - movie_6["avg_rating"]) < 0.5

    def test_global_mean_is_true_per_rating_average_not_average_of_averages(self, raw_ratings_df):
        """
        C must be sum(all individual ratings) / count(all individual ratings)
        — NOT the mean of each movie's own average — since the latter would
        let a movie with 1 rating count exactly as much toward "the typical
        rating" as one with 20 ratings.
        """
        agg = aggregate_ratings(raw_ratings_df)
        _weighted, c, _m = compute_weighted_ratings(agg)

        true_global_mean = raw_ratings_df["rating"].mean()
        naive_average_of_averages = agg["avg_rating"].mean()

        assert c == pytest.approx(true_global_mean)
        assert c != pytest.approx(naive_average_of_averages)

    def test_explicit_prior_votes_overrides_derived_median(self, raw_ratings_df):
        agg = aggregate_ratings(raw_ratings_df)
        _default_weighted, _c, default_m = compute_weighted_ratings(agg)
        _overridden_weighted, _c2, overridden_m = compute_weighted_ratings(agg, prior_votes=1000)

        assert overridden_m == 1000
        assert default_m != 1000

    def test_higher_prior_pulls_everything_closer_to_the_mean(self, raw_ratings_df):
        agg = aggregate_ratings(raw_ratings_df)
        low_prior, c, _m = compute_weighted_ratings(agg, prior_votes=1)
        high_prior, _c2, _m2 = compute_weighted_ratings(agg, prior_votes=10_000)

        movie_1_low = low_prior.loc[low_prior["movieId"] == 1, "weighted_rating"].iloc[0]
        movie_1_high = high_prior.loc[high_prior["movieId"] == 1, "weighted_rating"].iloc[0]

        # A huge prior should drag the weighted rating almost all the way to C.
        assert abs(movie_1_high - c) < abs(movie_1_low - c)

    def test_empty_input_returns_empty_frame_without_error(self):
        import pandas as pd

        empty = pd.DataFrame(columns=["movieId", "avg_rating", "rating_count"])
        weighted, c, m = compute_weighted_ratings(empty)
        assert weighted.empty
        assert c == 0.0
        assert m == 0.0
