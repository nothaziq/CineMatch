"""
Repository for TMDB metadata access.

Responsibilities: talk to TMDB over HTTP, cache every response to disk so we
never re-fetch a movie we already have, and respect TMDB's rate limit. This
is a repository, not a service — no feature-engineering or business logic
lives here, only "get me raw data for this tmdb_id."

Caching design: one JSON file per tmdb_id under tmdb_cache_dir. On any run,
a movie whose cache file already exists is skipped entirely — this makes the
enrichment step resumable if it's interrupted partway through 87k movies,
and keeps repeated pipeline runs free after the first.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class TMDBRateLimitError(Exception):
    pass


class TMDBRepository:
    def __init__(self) -> None:
        if not settings.tmdb_access_token and not settings.tmdb_api_key:
            raise ValueError(
                "No TMDB credentials configured. Set TMDB_ACCESS_TOKEN (preferred) "
                "or TMDB_API_KEY in your .env file."
            )
        self.session = requests.Session()
        if settings.tmdb_access_token:
            self.session.headers.update(
                {"Authorization": f"Bearer {settings.tmdb_access_token}"}
            )
        self.cache_dir = settings.tmdb_cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._request_count = 0
        self._window_start = time.time()

    def _throttle(self) -> None:
        """Simple fixed-window rate limiter honoring TMDB's burst limit."""
        now = time.time()
        elapsed = now - self._window_start
        if elapsed >= settings.tmdb_window_seconds:
            self._window_start = now
            self._request_count = 0

        if self._request_count >= settings.tmdb_requests_per_window:
            sleep_for = settings.tmdb_window_seconds - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._window_start = time.time()
            self._request_count = 0

        self._request_count += 1

    def _cache_path(self, tmdb_id: int) -> Path:
        return self.cache_dir / f"{tmdb_id}.json"

    def _get(self, path: str, params: dict | None = None) -> dict | None:
        params = params or {}
        if not settings.tmdb_access_token and settings.tmdb_api_key:
            params["api_key"] = settings.tmdb_api_key

        self._throttle()
        url = f"{settings.tmdb_base_url}{path}"
        try:
            resp = self.session.get(url, params=params, timeout=10)
        except requests.RequestException as exc:
            logger.warning("TMDB request failed for %s: %s", path, exc)
            return None

        if resp.status_code == 429:
            retry_after = float(resp.headers.get("Retry-After", "1"))
            logger.info("TMDB rate limit hit, sleeping %.1fs", retry_after)
            time.sleep(retry_after)
            return self._get(path, params)

        if resp.status_code == 404:
            return None

        if not resp.ok:
            logger.warning("TMDB returned %s for %s", resp.status_code, path)
            return None

        return resp.json()

    def fetch_movie_bundle(self, tmdb_id: int, force_refresh: bool = False) -> dict | None:
        """
        Fetch movie details + credits + keywords in one logical call, using
        TMDB's append_to_response to do it in a single HTTP request rather
        than three. Result is cached to disk keyed by tmdb_id.
        """
        cache_path = self._cache_path(tmdb_id)
        if cache_path.exists() and not force_refresh:
            with open(cache_path, "r") as f:
                return json.load(f)

        data = self._get(
            f"/movie/{tmdb_id}",
            params={"append_to_response": "credits,keywords"},
        )
        if data is None:
            return None

        with open(cache_path, "w") as f:
            json.dump(data, f)

        return data

    @staticmethod
    def to_feature_row(bundle: dict) -> dict:
        """
        Flatten a raw TMDB bundle into the shape feature_engineering.py expects:
        overview (str), director (str), cast (list[str]),
        keywords (list[str]), production_companies (list[str]).
        """
        credits = bundle.get("credits", {})
        crew = credits.get("crew", [])
        director = next((c["name"] for c in crew if c.get("job") == "Director"), "")

        cast = [c["name"] for c in credits.get("cast", [])[:5]]

        keywords_block = bundle.get("keywords", {})
        keywords = [k["name"] for k in keywords_block.get("keywords", [])]

        companies = [c["name"] for c in bundle.get("production_companies", [])]

        return {
            "overview": bundle.get("overview") or "",
            "director": director,
            "cast": cast,
            "keywords": keywords,
            "production_companies": companies,
            "poster_path": bundle.get("poster_path"),
            "backdrop_path": bundle.get("backdrop_path"),
            "runtime": bundle.get("runtime"),
            "release_date": bundle.get("release_date"),
        }

    @staticmethod
    def image_url(path: str | None, size: str = "w500") -> str | None:
        """size options: w92/w154/w185/w342/w500/w780/original for posters,
        w300/w780/w1280/original for backdrops."""
        if not path:
            return None
        return f"{settings.tmdb_image_base_url}/{size}{path}"
