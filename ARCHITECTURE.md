# CineMatch — Architecture Documentation
### Production-Grade Movie Recommendation System

**Stack:** React 19 + Vite + TypeScript + Tailwind + Framer Motion (frontend) · FastAPI + Python 3.12 + scikit-learn (backend) · MovieLens 32M + TMDB (data)

---

## 1. System Overview

```
MovieLens 32M (CSV)  ──┐
                        ├─► Offline Build Pipeline ─► Artifacts (Parquet + Pickled matrices)
TMDB API (metadata) ───┘                                       │
                                                                 ▼
                                                    FastAPI (loads artifacts at startup)
                                                                 │
                                                          REST API (JSON)
                                                                 │
                                                    React 19 SPA (Vite + TS + Tailwind)
```

**Core principle:** the recommendation engine (ML) is decoupled from presentation (TMDB metadata). MovieLens IDs are the system's source of truth; TMDB only decorates a movie with poster/cast/overview once we already know which movie we're talking about. If TMDB is down or rate-limited, recommendations still work — just with degraded (placeholder) visuals.

**Core principle #2 — no live preprocessing.** MovieLens 32M is too large to vectorize on every FastAPI boot. All heavy computation (TF-IDF, cosine similarity matrix) happens in an **offline build step** that produces artifacts on disk. FastAPI startup just deserializes those artifacts. This keeps boot time in seconds, not minutes, and means the ML pipeline can be re-run independently of the API.

---

## 2. Backend — Clean Architecture

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routes_movies.py        # /movies, /movies/{id}, /movies/search, etc.
│   │   │   ├── routes_recommendations.py
│   │   │   └── routes_health.py
│   │   └── deps.py                     # shared FastAPI Depends() providers
│   │
│   ├── core/
│   │   ├── config.py                   # Pydantic Settings (env vars, TMDB key, paths)
│   │   ├── logging.py
│   │   └── lifespan.py                 # startup/shutdown: load artifacts into memory
│   │
│   ├── data/
│   │   ├── raw/                        # original MovieLens CSVs (gitignored)
│   │   ├── processed/                  # cleaned parquet files
│   │   └── artifacts/                  # tfidf_matrix.pkl, similarity_matrix.pkl, movie_index.pkl
│   │
│   ├── repositories/
│   │   ├── movie_repository.py         # in-memory dataset access — no business logic
│   │   └── tmdb_repository.py          # HTTP client to TMDB, with on-disk response cache
│   │
│   ├── services/
│   │   ├── movie_service.py            # browse/filter/sort/paginate movies
│   │   ├── search_service.py           # search orchestration
│   │   └── recommendation_service.py   # orchestrates ML engine + enrichment
│   │
│   ├── ml/
│   │   ├── pipeline/
│   │   │   ├── cleaning.py             # drop nulls, normalize genres/tags
│   │   │   ├── feature_engineering.py  # combine genres+tags+overview+cast+director into one text blob
│   │   │   └── build_artifacts.py      # CLI script: run offline, produces /data/artifacts/*
│   │   ├── vectorizer.py               # TF-IDF wrapper
│   │   └── engine/
│   │       ├── base.py                 # RecommenderStrategy(ABC) — .recommend(movie_id, k) -> List[Recommendation]
│   │       ├── content_based.py        # ContentBasedRecommender(RecommenderStrategy)
│   │       └── registry.py             # maps engine name -> implementation (swap point for future collaborative/hybrid)
│   │
│   ├── schemas/
│   │   ├── movie.py                    # MovieOut, MovieDetailOut, PaginatedMovies
│   │   └── recommendation.py           # RecommendationOut (includes score + explanation)
│   │
│   ├── middleware/
│   │   ├── cors.py
│   │   └── error_handler.py            # domain exceptions -> consistent JSON error shape
│   │
│   ├── exceptions/
│   │   └── domain.py                   # MovieNotFoundError, TMDBUnavailableError, etc.
│   │
│   └── main.py                          # app factory, mounts routers + middleware
│
└── scripts/
    └── build_artifacts.py               # entrypoint: python -m scripts.build_artifacts
```

### Layer responsibilities (strict boundaries)

| Layer | Allowed to do | Never does |
|---|---|---|
| **api/** | Validate request, call one service, format response | Touch pandas, ML, or raw data |
| **services/** | Business logic, orchestrate repositories + ml engine | Own an HTTP client or parse a DataFrame directly |
| **repositories/** | Load/query in-memory data, call TMDB HTTP client | Contain filtering/business rules |
| **ml/** | Feature engineering, vectorization, similarity, strategy pattern | Know about HTTP, FastAPI, or TMDB |

This means: swapping content-based → collaborative filtering later touches only `ml/engine/` and one line in `registry.py`. The API contract (`RecommendationOut`) and the frontend never change.

### Dependency Injection

`api/deps.py` exposes `get_movie_repository()`, `get_recommendation_service()`, etc., as FastAPI `Depends()` providers, each a singleton constructed once at startup (`core/lifespan.py`) and reused across requests — no re-loading data per request.

---

## 3. Data Pipeline (offline, run before the API ever starts)

```
raw MovieLens CSVs (movies.csv, ratings.csv, tags.csv, links.csv)
        │
        ▼
cleaning.py           → drop malformed rows, normalize genre pipe-strings, dedupe tags
        │
        ▼
TMDB enrichment        → via links.csv (movieId -> tmdbId), fetch overview/cast/director/keywords
        │                 (cached to disk as JSON per movie — TMDB is rate-limited, never re-fetch)
        ▼
feature_engineering.py → build one weighted text "document" per movie:
                          genres (x3 weight) + director (x2) + top-3 cast + keywords + overview
        │
        ▼
vectorizer.py          → TF-IDF over all documents (scikit-learn TfidfVectorizer)
        │
        ▼
similarity computation → cosine_similarity(tfidf_matrix) — or top-k nearest neighbors
                          via sklearn NearestNeighbors for memory efficiency at 32M scale
        │
        ▼
artifacts/              → tfidf_matrix.pkl, similarity_index.pkl (top-50 neighbors per movie,
                           not a full N×N matrix — full matrix at ~87k movies is fine, but we
                           store top-k only to keep memory + load time bounded)
        │
        ▼
FastAPI startup          → deserialize artifacts, hold in memory for app lifetime
```

**Why top-k neighbors instead of a full similarity matrix:** MovieLens 32M has ~87,000 unique movies. A full cosine similarity matrix is 87k × 87k floats (~30GB dense, or manageable sparse but still wasteful). We only ever need "top 20 similar movies" per lookup, so `NearestNeighbors` with cosine metric gives us a much smaller, purpose-built index.

**Why cache TMDB responses to disk:** TMDB's free tier rate-limits requests. Enrichment happens once during the build step, not per API request. The API layer reads pre-fetched JSON, never calls TMDB live during a user request (except optionally as a fallback for brand-new movies not yet cached).

---

## 4. ML Architecture — Strategy Pattern for Future Extensibility

```python
# ml/engine/base.py
class RecommenderStrategy(ABC):
    @abstractmethod
    def recommend(self, movie_id: int, k: int = 10) -> list[Recommendation]: ...

# ml/engine/content_based.py
class ContentBasedRecommender(RecommenderStrategy):
    """Phase 1: TF-IDF + cosine similarity over genres/tags/overview/cast/director."""

# Future, same interface:
# class CollaborativeRecommender(RecommenderStrategy): ...    # user-item ratings matrix
# class HybridRecommender(RecommenderStrategy): ...           # weighted blend of both
```

`recommendation_service.py` depends only on `RecommenderStrategy`, resolved via `registry.py`. Each `Recommendation` includes a `score` (0–1 similarity) and a generated `explanation` string (e.g. "Shares Sci-Fi, Psychological Thriller, and director Christopher Nolan") built by comparing the target movie's feature tags against the source movie's.

---

## 5. REST API Design

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/movies` | Paginated browse, supports `?genre=&sort=&page=&page_size=` |
| `GET /api/v1/movies/{id}` | Full detail (MovieLens + TMDB merged) |
| `GET /api/v1/movies/search?q=` | Debounced-friendly search endpoint |
| `GET /api/v1/movies/trending` | TMDB-informed trending window |
| `GET /api/v1/movies/popular` | Ranked by MovieLens rating volume |
| `GET /api/v1/movies/top-rated` | Ranked by weighted average rating (IMDB-style Bayesian) |
| `GET /api/v1/movies/recent` | Recently added/released |
| `GET /api/v1/movies/genres` | List of genres with counts |
| `GET /api/v1/recommendations/{movie_id}?k=10` | Content-based similar movies |
| `POST /api/v1/recommendations/batch` | Multiple seed movies → blended recommendation (for the "pick your favorites" flow) |
| `GET /api/v1/health` | Liveness/readiness, reports artifact load status |

**Consistent error shape:**
```json
{ "error": { "code": "MOVIE_NOT_FOUND", "message": "...", "status": 404 } }
```

---

## 6. Frontend — Feature-Based Architecture

```
frontend/src/
├── app/                  # App shell, providers (QueryClient, Router, Theme)
├── routes/               # Route definitions, lazy-loaded pages
├── layouts/              # AppLayout, header/footer shells
├── theme/                # Design tokens, Tailwind config extensions
├── components/           # Truly generic, cross-feature UI atoms (Button, Skeleton, Card shell)
├── hooks/                # Cross-feature hooks (useDebounce, useLocalStorage, useMediaQuery)
├── services/             # Base API client (axios instance, interceptors)
├── types/                # Shared API contract types (mirrors backend schemas)
│
└── features/
    ├── home/
    │   ├── components/   # HeroSection, TrendingRail, GenreRail
    │   ├── hooks/         # useHomeData (TanStack Query)
    │   └── services/
    ├── search/
    │   ├── components/   # SearchBar, ResultsGrid, FilterPanel
    │   └── hooks/         # useSearch (debounced + infinite query)
    ├── movie/
    │   ├── components/   # PosterHero, CastList, TrailerEmbed, SimilarMoviesRail
    │   └── hooks/         # useMovieDetail
    ├── recommendations/
    │   ├── components/   # MovieMultiSelect, RecommendationCard, ExplanationBadge
    │   └── hooks/         # useRecommendations
    └── favorites/
        ├── components/
        └── services/      # localStorageAdapter — abstracted so it can be swapped for a backend API later
```

**State management split:**
- Server state (movies, recommendations) → TanStack Query, never duplicated into component state.
- Client-only state (favorites, theme, recent searches) → localStorage, wrapped behind a small adapter interface (`StorageAdapter`) so swapping to a real backend later means changing one implementation file, not every component that reads favorites.

**Design system note:** dark theme, glassmorphism panels, one confident accent color, restrained motion — detailed visual direction (type scale, spacing, color tokens) gets nailed down when we scaffold the frontend, using the frontend-design conventions for this environment.

---

## 7. Performance Strategy

| Concern | Approach |
|---|---|
| Backend cold start | Artifacts pre-built offline, loaded once via lifespan hook |
| Similarity lookup | O(k) via precomputed nearest-neighbor index, not live cosine computation |
| TMDB rate limits | Disk-cached JSON per movie, fetched once at build time |
| Frontend data fetching | TanStack Query cache + stale-while-revalidate |
| Images | Lazy-loaded, TMDB's own responsive image sizes (`w200`/`w500`/`original`) selected by viewport |
| Search | Debounced (≈300ms) + backend-side pagination, never fetch-all |
| Bundle size | Route-based code splitting via React Router lazy loading |

---

## 8. Build Phases

1. **Backend data pipeline** — cleaning → feature engineering → artifact build script, runnable standalone against your MovieLens 32M files.
2. **Backend API** — repositories/services/routes wired to the artifacts, TMDB repository with disk caching.
3. **Frontend scaffold** — Vite/TS/Tailwind setup, design tokens, base layout, routing skeleton.
4. **Feature build-out** — Home → Search → Movie Detail → Recommendations → Favorites, in that order (each depends on the previous existing).
5. **Polish pass** — animations, empty/error/loading states, accessibility audit, responsive QA.

---

## 9. Open Items / Your Inputs Needed Later

- TMDB API key (free, from themoviedb.org → Settings → API) — needed before step 2 can fetch real metadata; step 1 works with MovieLens data alone.
- Confirm which MovieLens 32M files you have locally (`movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`) and their path, so the build script points at the right location.
