# Vigor

Modular strength training platform with service-oriented design and analytics.

## Setup

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Run the API

```bash
# In-memory mode (no persistence)
uvicorn src.api.main:app --reload

# SQLite mode (persistent)
export DB_PATH=vigor.db
python -c "from src.infra.repositories.sqlite_connection import init_db; init_db('vigor.db')"
uvicorn src.api.main:app --reload
```

API will be available at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Run Tests

```bash
pytest -q
```

## Run Demo

```bash
python -m examples.demo_full_flow
```

## Architecture

- `src/core/models`: Domain models (User, Workout, Schedule, Analytics)
- `src/core/repositories/protocols.py`: Repository interfaces
- `src/core/services`: Business logic (user, workout, planning, analytics)
- `src/core/use_cases`: Cross-domain orchestration
- `src/core/domain_logic`: Pure calculations (1RM, volume)
- `src/infra/repositories`: In-memory and SQLite implementations
- `src/api`: FastAPI routers and dependencies
- `tests`: Comprehensive unit and integration tests