from __future__ import annotations


class TestMoviesEndpoint:
    def test_list_movies_returns_all_synthetic_movies(self, client):
        resp = client.get("/api/v1/movies")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_items"] == 6

    def test_list_movies_filters_by_genre(self, client):
        resp = client.get("/api/v1/movies", params={"genre": "Sci-Fi"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_items"] == 2
        assert all("Sci-Fi" in item["genres"] for item in body["items"])

    def test_get_movie_by_id(self, client):
        resp = client.get("/api/v1/movies/1")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Galaxy Raiders"

    def test_get_missing_movie_returns_consistent_error_shape(self, client):
        resp = client.get("/api/v1/movies/9999")
        assert resp.status_code == 404
        body = resp.json()
        assert body["error"]["code"] == "MOVIE_NOT_FOUND"
        assert body["error"]["status"] == 404

    def test_search_finds_partial_case_insensitive_match(self, client):
        resp = client.get("/api/v1/movies/search", params={"q": "galaxy"})
        assert resp.status_code == 200
        titles = [m["title"] for m in resp.json()]
        assert "Galaxy Raiders" in titles

    def test_trending_endpoint_ranks_recent_activity_first(self, client):
        resp = client.get("/api/v1/movies/trending")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert items[0]["movie_id"] == 1

    def test_genres_endpoint_returns_counts(self, client):
        resp = client.get("/api/v1/movies/genres")
        assert resp.status_code == 200
        genres = {g["genre"]: g["count"] for g in resp.json()}
        assert genres["Sci-Fi"] == 2

    def test_page_size_over_limit_is_rejected(self, client):
        resp = client.get("/api/v1/movies", params={"page_size": 500})
        assert resp.status_code == 422


class TestRecommendationsEndpoint:
    def test_recommend_for_movie(self, client):
        resp = client.get("/api/v1/recommendations/1", params={"k": 3})
        assert resp.status_code == 200
        body = resp.json()
        assert body["seed_movie_ids"] == [1]
        assert all(r["movie"]["movie_id"] != 1 for r in body["recommendations"])

    def test_recommend_for_unknown_movie_404s(self, client):
        resp = client.get("/api/v1/recommendations/9999")
        assert resp.status_code == 404

    def test_batch_recommend(self, client):
        resp = client.post("/api/v1/recommendations/batch", json={"movie_ids": [1, 2], "k": 3})
        assert resp.status_code == 200
        body = resp.json()
        assert set(body["seed_movie_ids"]) == {1, 2}

    def test_batch_recommend_with_unknown_seed_404s(self, client):
        resp = client.post("/api/v1/recommendations/batch", json={"movie_ids": [1, 9999]})
        assert resp.status_code == 404


class TestHealthEndpoint:
    def test_health_response_shape_is_internally_consistent(self, client):
        """
        /health reads real app.state (set only by the actual lifespan hook),
        not the synthetic repository the other tests override via DI — so
        its result legitimately depends on whether real parquet/pickle
        artifacts happen to exist on disk wherever the suite runs (CI vs. a
        dev machine that already ran build_artifacts.py). Rather than assert
        one specific status, assert the response is internally consistent
        for whichever state it's actually in.
        """
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        body = resp.json()

        assert body["status"] in ("ok", "degraded")
        assert isinstance(body["artifacts_loaded"], bool)
        assert body["status"] == ("ok" if body["artifacts_loaded"] else "degraded")

        if body["artifacts_loaded"]:
            assert body["movie_count"] > 0
        else:
            assert body["movie_count"] == 0
