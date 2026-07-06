from __future__ import annotations

import json

import pytest

from app.core.config import settings
from app.repositories.tmdb_repository import TMDBRepository


@pytest.fixture
def tmdb_repo(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "tmdb_access_token", "fake-token-for-tests")
    monkeypatch.setattr(settings, "tmdb_cache_dir", tmp_path)
    return TMDBRepository()


class TestFetchMovieBundleCaching:
    def test_fresh_cache_with_videos_is_served_without_a_request(self, tmdb_repo, monkeypatch):
        """A cache entry that already has the current shape (includes
        'videos') should be served as-is, with no HTTP call at all."""
        cache_path = tmdb_repo._cache_path(42)
        cache_path.write_text(json.dumps({"overview": "cached", "videos": {"results": []}}))

        def fail_if_called(*args, **kwargs):
            raise AssertionError("Should not hit the network for a fresh, complete cache entry")

        monkeypatch.setattr(tmdb_repo.session, "get", fail_if_called)

        result = tmdb_repo.fetch_movie_bundle(42)
        assert result["overview"] == "cached"

    def test_stale_cache_missing_videos_triggers_one_refetch(self, tmdb_repo, monkeypatch):
        """
        Regression test: a bundle cached before 'videos' was added to
        append_to_response must NOT be served forever as-is — it should
        transparently trigger exactly one refetch so trailer data actually
        gets populated on the next pipeline run, instead of silently staying
        empty no matter how many times enrich_with_tmdb.py reruns.
        """
        cache_path = tmdb_repo._cache_path(99)
        cache_path.write_text(json.dumps({"overview": "old shape, no videos key"}))

        call_count = {"n": 0}

        class FakeResponse:
            status_code = 200
            ok = True

            def json(self):
                return {"overview": "fresh from TMDB", "videos": {"results": [{"key": "abc123", "site": "YouTube", "type": "Trailer", "official": True}]}}

        def fake_get(url, params=None, timeout=None):
            call_count["n"] += 1
            return FakeResponse()

        monkeypatch.setattr(tmdb_repo.session, "get", fake_get)

        result = tmdb_repo.fetch_movie_bundle(99)

        assert call_count["n"] == 1  # actually hit the network, didn't just re-serve stale cache
        assert result["videos"]["results"][0]["key"] == "abc123"

        # And the cache on disk should now be updated with the new shape.
        updated_cache = json.loads(cache_path.read_text())
        assert "videos" in updated_cache

    def test_force_refresh_always_refetches_regardless_of_cache_shape(self, tmdb_repo, monkeypatch):
        cache_path = tmdb_repo._cache_path(7)
        cache_path.write_text(json.dumps({"overview": "cached", "videos": {"results": []}}))

        call_count = {"n": 0}

        class FakeResponse:
            status_code = 200
            ok = True

            def json(self):
                return {"overview": "forced refresh", "videos": {"results": []}}

        def fake_get(url, params=None, timeout=None):
            call_count["n"] += 1
            return FakeResponse()

        monkeypatch.setattr(tmdb_repo.session, "get", fake_get)

        result = tmdb_repo.fetch_movie_bundle(7, force_refresh=True)
        assert call_count["n"] == 1
        assert result["overview"] == "forced refresh"


class TestExtractTrailerKey:
    def test_prefers_official_trailer(self):
        bundle = {
            "videos": {
                "results": [
                    {"key": "teaser1", "site": "YouTube", "type": "Teaser", "official": True},
                    {"key": "unofficial", "site": "YouTube", "type": "Trailer", "official": False},
                    {"key": "official1", "site": "YouTube", "type": "Trailer", "official": True},
                ]
            }
        }
        assert TMDBRepository._extract_trailer_key(bundle) == "official1"

    def test_falls_back_to_any_trailer_if_no_official_one(self):
        bundle = {
            "videos": {
                "results": [
                    {"key": "unofficial", "site": "YouTube", "type": "Trailer", "official": False},
                ]
            }
        }
        assert TMDBRepository._extract_trailer_key(bundle) == "unofficial"

    def test_falls_back_to_teaser_if_no_trailer(self):
        bundle = {
            "videos": {
                "results": [
                    {"key": "teaser1", "site": "YouTube", "type": "Teaser", "official": False},
                ]
            }
        }
        assert TMDBRepository._extract_trailer_key(bundle) == "teaser1"

    def test_ignores_non_youtube_videos(self):
        bundle = {
            "videos": {
                "results": [
                    {"key": "vimeo1", "site": "Vimeo", "type": "Trailer", "official": True},
                ]
            }
        }
        assert TMDBRepository._extract_trailer_key(bundle) is None

    def test_no_videos_block_returns_none(self):
        assert TMDBRepository._extract_trailer_key({}) is None


class TestYoutubeEmbedUrl:
    def test_builds_embed_url(self):
        assert TMDBRepository.youtube_embed_url("abc123") == "https://www.youtube.com/embed/abc123"

    def test_none_key_returns_none(self):
        assert TMDBRepository.youtube_embed_url(None) is None

    def test_pandas_nan_returns_none_not_the_string_nan(self):
        """Regression test: pandas NaN is a truthy float. A naive `if not
        trailer_key` check would let it through and build a URL literally
        containing the text 'nan'."""
        nan = float("nan")
        assert TMDBRepository.youtube_embed_url(nan) is None
