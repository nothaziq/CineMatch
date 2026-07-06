# Contributing to CineMatch

## Getting set up

Follow the **Local setup** section in [`README.md`](./README.md) first —
you'll need a TMDB API key and the MovieLens 32M dataset before anything runs.

## Branching

- `main` stays deployable — Railway auto-deploys from it.
- Work in feature branches: `feature/short-description` or `fix/short-description`.
- Open a PR into `main` rather than pushing directly, even solo — it keeps a
  reviewable history and CI (if/when added) a chance to run.

## Before opening a PR

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npx tsc --noEmit -p tsconfig.app.json
npm run build
```

Both should pass clean. If you touched the ML pipeline or artifacts, note in
the PR description whether `backend/app/data/processed` / `backend/app/data/artifacts`
need to be rebuilt and re-committed — Railway only sees what's in git, not
what's on your machine (see `DEPLOY.md`).

## Code boundaries (backend)

The layering in `ARCHITECTURE.md` is enforced by convention, not tooling, so
it's worth holding the line manually:

| Layer | Allowed to do | Never does |
|---|---|---|
| `api/` | Validate request, call one service, format response | Touch pandas, ML, or raw data |
| `services/` | Business logic, orchestrate repositories + ml engine | Own an HTTP client or parse a DataFrame directly |
| `repositories/` | Load/query in-memory data, call TMDB HTTP client | Contain filtering/business rules |
| `ml/` | Feature engineering, vectorization, similarity, strategy pattern | Know about HTTP, FastAPI, or TMDB |

If a PR crosses one of these lines, it's usually a sign the change belongs
in a different file.

## Commit messages

Short, imperative, present tense: `Add batch recommendation endpoint`, not
`Added` or `Adding`. Doesn't need to be more formal than that for a project
this size.
