# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Environment (uses uv)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run the API (in-memory, no persistence)
uvicorn src.api.main:app --reload          # http://localhost:8000, docs at /docs

# Run the API with SQLite persistence
export DB_PATH=vigor.db
python -c "from src.infra.repositories.sqlite_connection import init_db; init_db('vigor.db')"
uvicorn src.api.main:app --reload

# Tests
pytest -q                                   # full suite
pytest tests/services/workout/test_tracking_service.py            # single file
pytest tests/services/workout/test_tracking_service.py::test_name # single test

# Demo (exercises the domain end-to-end via in-memory repos)
python -m examples.demo_full_flow
```

`pytest.ini` sets `pythonpath = . src`, so imports work without installing the package. Source files use **tabs** for indentation — match existing style.

## Architecture

Layered / clean-architecture design with strict dependency inversion. The dependency direction is always `api → core ← infra`; `core` never imports from `api` or `infra`.

- **`src/core/models`** — Domain entities as `@dataclass`es with `uuid`-defaulted `id` fields and `Enum` value types (User, Workout, Schedule/planning, Analytics).
- **`src/core/repositories/protocols.py`** — Repository interfaces declared as `typing.Protocol`. This is the seam between core and infra; services depend only on these protocols.
- **`src/core/services`** — Business logic, grouped by domain (`user/`, `workout/`, `planning/`, `analytics/`). Each service takes repository protocols via its constructor and validates inputs.
- **`src/core/use_cases`** — Cross-domain orchestration that composes multiple services. Example: `CompleteWorkoutUseCase` completes the session, scans each set to detect 1RM PRs, computes volume metrics, and detects achievements in one `execute()`.
- **`src/core/domain_logic`** — Pure, stateless calculations (1RM estimators in `strength_estimators.py`, volume math in `volume_aggregators.py`). No I/O, no repositories.
- **`src/core/shared/errors.py`** — `DomainError` hierarchy: `ValidationError`, `NotFoundError`, `ConflictError`. Services raise these; the API layer translates them.
- **`src/infra/repositories`** — Two interchangeable implementations of every protocol: `memory_*.py` (dict-backed) and `sqlite_*.py`. SQLite schema lives in `sqlite_schema.py`; `sqlite_connection.py` provides `get_connection`/`init_db`.
- **`src/api`** — FastAPI. `main.py` mounts routers under `/api`; each router defines Pydantic request models, calls a service/use-case, and catches `ValidationError`/`NotFoundError` to raise `HTTPException(400)`.

### Dependency injection (`src/api/dependencies.py`)

This module is the composition root and the place to wire new services.

- **Persistence is selected by the `DB_PATH` env var.** `USE_SQLITE = os.getenv("DB_PATH") is not None`. When set, providers construct `SQLite*` repos against a single shared connection; otherwise they use module-level singleton in-memory repos.
- Each `get_*_service()` provider is `@lru_cache`d, so every request shares one service instance (and, in memory mode, one set of repos).
- **Gotcha:** planning's `ProgramService` (programs/phases/enrollments) has no SQLite implementation and always uses in-memory repos even when `DB_PATH` is set. Only templates and scheduled workouts are persisted in SQLite.

## Conventions

- Services validate and raise domain errors (e.g. `ValidationError("set_number: must be >= 1")`); routers are thin and only map those errors to HTTP responses.
- Tests use the in-memory adapters by default, follow Arrange-Act-Assert, and prefer explicit fixtures over shared global state.
