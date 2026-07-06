# CineMatch

A production-grade movie recommendation web app. Content-based recommendations
over the MovieLens dataset, enriched with TMDB metadata, served through a
FastAPI backend and a React SPA.

**Stack:** React 19 + Vite + TypeScript + Tailwind + Framer Motion (frontend)
· FastAPI + Python 3.12 + scikit-learn (backend) · MovieLens 32M + TMDB (data)

Full architecture writeup: [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## What it does

- Browse, search, and filter movies (genre, sort, pagination)
- Trending / popular / top-rated / recently-added rails on the home page
- Movie detail pages with TMDB-enriched metadata (cast, overview, trailer)
- Content-based recommendations from a single movie, or blended from
  multiple picks ("pick your favorites" flow)
- Favorites, persisted locally

## Architecture at a glance

```
MovieLens 32M (CSV) ──┐
                       ├─► Offline build pipeline ─► Artifacts (parquet + pickles)
TMDB API (metadata) ──┘                                     │
                                                             ▼
                                                FastAPI (loads artifacts at startup)
                                                             │
                                                       REST API (JSON)
                                                             │
                                                React 19 SPA (Vite + TS + Tailwind)
```

The recommendation engine (TF-IDF + cosine similarity, precomputed offline) is
fully decoupled from presentation (TMDB metadata) — MovieLens IDs are the
system's source of truth, and TMDB only ever decorates a movie once we already
know which one we're talking about. If TMDB is down, recommendations still work.

Backend follows a strict layered architecture — `api/` → `services/` →
`repositories/`/`ml/` — so swapping the recommendation strategy later only
touches the `ml/` layer, never the API contract or the frontend.

## Local setup

### Prerequisites
- Docker + Docker Compose
- A [TMDB API key](https://www.themoviedb.org/settings/api) (free)
- MovieLens 32M dataset (`movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`)
  from [grouplens.org](https://grouplens.org/datasets/movielens/32m/)

### 1. Environment variables

Create `backend/.env`:

```env
TMDB_API_KEY=your_key_here
TMDB_ACCESS_TOKEN=your_v4_bearer_token_here
```

### 2. Add the MovieLens data

Drop the four CSVs into `backend/app/data/raw/`.

### 3. Build the recommendation artifacts

```bash
cd backend
pip install -r requirements.txt
python -m app.ml.pipeline.build_artifacts
```

This cleans the data, engineers features, fits TF-IDF, computes a top-k
nearest-neighbor similarity index, and writes everything to
`backend/app/data/processed/` and `backend/app/data/artifacts/`.

### 4. Run everything

```bash
docker compose up --build
```

- Frontend: [http://localhost](http://localhost)
- Backend API: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## Running tests

```bash
cd backend
pytest
```

## Deployment

See [`DEPLOY.md`](./DEPLOY.md) for the full Railway deployment guide,
including the two things that trip people up: Railway builds from git (so
built artifacts need to be committed, not just built locally), and the
private-network wiring between the frontend and backend services.

## Project structure

```
backend/
├── app/
│   ├── api/v1/          # Route handlers — thin, delegate to services
│   ├── core/            # Config, logging, startup/shutdown lifecycle
│   ├── repositories/    # In-memory data access, TMDB HTTP client
│   ├── services/        # Business logic, orchestration
│   ├── ml/              # Offline pipeline + recommendation engine
│   ├── schemas/         # Pydantic response models
│   ├── middleware/      # Error handling
│   └── exceptions/      # Domain exceptions
└── tests/

frontend/
└── src/
    ├── app/             # App shell, providers
    ├── routes/          # Router definitions
    ├── layouts/         # Header/footer shells
    ├── components/      # Cross-feature UI (MovieCard, MovieRail, etc.)
    ├── services/         # Base API client
    └── features/
        ├── home/
        ├── search/
        ├── movie/
        ├── recommendations/
        ├── favorites/
        └── genres/
```

See `ARCHITECTURE.md` for the full layer-responsibility breakdown and the
reasoning behind key design decisions (why top-k neighbors instead of a full
similarity matrix, why TMDB responses are cached to disk, the frontend state
management split, etc).

## Author

Built by [Haziq](https://github.com/nothaziq).
