from __future__ import annotations

from app.services.movie_service import MovieService


class TestBrowse:
    def test_returns_paginated_shape(self, built_movie_repository):
        service = MovieService(built_movie_repository)
        result = service.browse(page=1, page_size=2)
        assert result.page == 1
        assert result.page_size == 2
        assert result.total_items == 6
        assert result.total_pages == 3
        assert len(result.items) == 2

    def test_page_size_is_clamped(self, built_movie_repository):
        service = MovieService(built_movie_repository)
        result = service.browse(page_size=1000)
        assert result.page_size == 100  # clamped to the max

    def test_negative_page_is_clamped_to_one(self, built_movie_repository):
        service = MovieService(built_movie_repository)
        result = service.browse(page=-5)
        assert result.page == 1


class TestMovieDetailOut:
    def test_missing_tmdb_id_becomes_none(self, built_movie_repository):
        """Movie 5 has no tmdbId in links.csv (None) — detail should surface
        that as a clean None, not NaN or a crash."""
        service = MovieService(built_movie_repository)
        detail = service.get_movie_detail(5)
        assert detail.tmdb_id is None

    def test_no_trailer_key_column_yields_none_trailer_url(self, built_movie_repository):
        """These synthetic fixtures never ran TMDB enrichment, so there's no
        trailer_key column at all — trailer_url must degrade to None, not error."""
        service = MovieService(built_movie_repository)
        detail = service.get_movie_detail(1)
        assert detail.trailer_url is None

    def test_empty_cast_and_keywords_default_to_empty_list(self, built_movie_repository):
        service = MovieService(built_movie_repository)
        detail = service.get_movie_detail(1)
        assert detail.cast == []
        assert detail.keywords == []
