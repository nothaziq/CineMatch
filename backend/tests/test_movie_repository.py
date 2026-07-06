from __future__ import annotations

import pytest

from app.exceptions.domain import MovieNotFoundError


class TestFilterAndSort:
    def test_filter_by_genre(self, built_movie_repository):
        rows, total = built_movie_repository.filter_and_sort(genre="Sci-Fi", page=1, page_size=10)
        assert total == 2
        assert set(rows["movieId"]) == {1, 2}

    def test_sort_by_trending(self, built_movie_repository):
        rows, _ = built_movie_repository.filter_and_sort(sort_by="trending", page=1, page_size=10)
        # Movie 1 has the strongest recent rating activity — should sort first.
        assert rows.iloc[0]["movieId"] == 1

    def test_trending_falls_back_to_popularity_if_column_missing(self, built_movie_repository):
        # Simulate artifacts built before trending_score existed.
        built_movie_repository._movies = built_movie_repository._movies.drop(columns=["trending_score"])
        rows, _ = built_movie_repository.filter_and_sort(sort_by="trending", page=1, page_size=10)
        # Should not raise, and should fall back to rating_count ordering.
        assert rows.iloc[0]["movieId"] == rows.sort_values("rating_count", ascending=False).iloc[0]["movieId"]

    def test_pagination_slices_correctly(self, built_movie_repository):
        page_1, total = built_movie_repository.filter_and_sort(sort_by="title", page=1, page_size=2)
        page_2, _ = built_movie_repository.filter_and_sort(sort_by="title", page=2, page_size=2)
        assert total == 6
        assert len(page_1) == 2
        assert len(page_2) == 2
        assert set(page_1["movieId"]).isdisjoint(set(page_2["movieId"]))

    def test_sort_by_title_is_alphabetical(self, built_movie_repository):
        rows, _ = built_movie_repository.filter_and_sort(sort_by="title", page=1, page_size=10)
        titles = list(rows["clean_title"])
        assert titles == sorted(titles)


class TestLookups:
    def test_get_by_id_returns_row(self, built_movie_repository):
        row = built_movie_repository.get_by_id(1)
        assert row["clean_title"] == "Galaxy Raiders"

    def test_get_by_id_raises_for_missing_movie(self, built_movie_repository):
        with pytest.raises(MovieNotFoundError):
            built_movie_repository.get_by_id(9999)

    def test_get_many_by_ids_skips_missing(self, built_movie_repository):
        rows = built_movie_repository.get_many_by_ids([1, 2, 9999])
        assert set(rows["movieId"]) == {1, 2}

    def test_search_by_title_case_insensitive(self, built_movie_repository):
        rows = built_movie_repository.search_by_title("galaxy")
        assert set(rows["movieId"]) == {1, 2}

    def test_genre_counts(self, built_movie_repository):
        counts = dict(built_movie_repository.genre_counts())
        assert counts["Action"] == 2
        assert counts["Sci-Fi"] == 2


class TestTotalPages:
    def test_zero_page_size_returns_zero(self):
        from app.repositories.movie_repository import MovieRepository

        assert MovieRepository.total_pages(total_items=10, page_size=0) == 0

    def test_rounds_up(self):
        from app.repositories.movie_repository import MovieRepository

        assert MovieRepository.total_pages(total_items=21, page_size=20) == 2
