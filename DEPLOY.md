# Deploying CineMatch to Railway

Two services, one repo: `backend` (FastAPI, Dockerfile) and `frontend` (nginx + built React app, Dockerfile).

## 0. Build your artifacts locally first

Railway builds from this git repo — it has no equivalent to docker-compose's
local bind mount, so whatever isn't committed doesn't exist in production.

With your `.env` and MovieLens CSVs already in place locally:

```bash
cd backend
python -m app.ml.pipeline.build_artifacts
```

This should populate `app/data/processed/movies_processed.parquet` and
`app/data/artifacts/*.pkl`. Those two paths are now tracked in git (raw CSVs
and the TMDB disk cache stay ignored — not needed at runtime, see
`backend/.gitignore`). Commit and push them:

```bash
git add backend/app/data/processed backend/app/data/artifacts
git commit -m "Add built recommendation artifacts"
git push
```

## 1. Create the Railway project

In the Railway dashboard: **New Project → Deploy from GitHub repo**, pick this repo.
Railway will try to auto-detect a service — delete it, then add two services manually
so each points at the right subfolder.

## 2. Backend service

- **New → GitHub Repo** (same repo again) → name it exactly `backend`
  (the frontend's nginx config depends on this exact name for private networking).
- Settings → Build:
  - **Root Directory**: `/backend`
  - **Builder**: Dockerfile (auto-detected once Root Directory is set)
  - **Config File Path**: `/backend/railway.json` — Railway does **not** infer
    this from Root Directory, it must be set explicitly.
- Variables tab, add:
  - `TMDB_API_KEY` — from your local `.env`
  - `TMDB_ACCESS_TOKEN` — from your local `.env`
  - `PORT` = `8000` — set this explicitly rather than leaving it to Railway's
    auto-injection, so the frontend's nginx config can reach a predictable,
    fixed private address (`backend.railway.internal:8000`).
- **Do not** generate a public domain for this service — it only needs to be
  reachable from the frontend over Railway's private network.

## 3. Frontend service

- **New → GitHub Repo** → name it `frontend`.
- Settings → Build:
  - **Root Directory**: `/frontend`
  - **Config File Path**: `/frontend/railway.json`
- Variables tab, add:
  - `BACKEND_HOST` = `backend.railway.internal:8000`
    (overrides the `backend:8000` default baked in for local docker-compose)
- Settings → Networking → **Generate Domain**, targeting port `${PORT}`
  (Railway assigns this dynamically; nginx now listens on whatever it is —
  see the `nginx.conf.template` change).

## 4. Verify

Once both deploys go green:

```bash
curl https://<your-frontend-domain>.up.railway.app/api/v1/health
```

should return the same JSON your local `docker compose up` gives you at
`localhost:8000/api/v1/health`. If it 502s, check the backend's logs first —
almost always either the artifacts weren't actually committed, or `PORT`
wasn't set to `8000` on the backend service.

## Notes / things that only matter once, not every deploy

- Redeploys only need `git push` — Railway auto-builds from the branch you connected.
- If you ever rebuild artifacts with different data (e.g. a fresh MovieLens
  snapshot), you must re-commit `app/data/processed` and `app/data/artifacts`
  for the change to reach Railway — rerunning the build script locally alone
  does nothing to production.
- This intentionally skips TMDB live enrichment cache in production (`tmdb_cache/`
  stays git/docker-ignored) — per `movie_repository.py`, only the parquet +
  artifact pickles are read at FastAPI startup, so this doesn't affect anything
  users see.
