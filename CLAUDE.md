# CLAUDE.md

This document operationalizes how Claude Code should work in this repository. It explains what the application is, how to evolve it, where to acquire context, and the mandatory engineering standards for code, comments, and logs.

## Application Brief (What this is and where it is going)

Vigor is a modular strength training platform that tracks workouts, schedules programming, and produces analytics/insights. The system follows Clean Architecture with strict dependency direction and domain separation. Near-term capabilities include robust workout session management and set tracking. Mid-term roadmap adds analytics (volume/1RM trends), program scheduling, and domain events. Long-term goals include adaptive planning and AI-driven insights.

- **Core domains**: `models`, `repositories`, `domain_logic`, `services`, `use_cases`, `infra`, `shared`, `tests`.
- **Dependency direction**: `models` → `repositories.protocols` → `repositories.impl`; `domain_logic` → used by `services`; `services` → used by `use_cases`.
- **AI responsibilities**: generate high-fidelity code, maintain invariants, extract rules from Cursor Rules files, and keep tests green.

## Operating Protocol for AI Agents

- **Mindset**
  - Code as if another engineer’s mission depends on this working properly.
  - Code as if there may not be a second chance to fix it.

- **No Meta-Chatter**
  - Do not add notes to self, apologies, or placeholders unless explicitly requested.
  - Output only code and necessary documentation.

- **Error Handling and Robustness**
  - Validate inputs early and fail fast with explicit exceptions from `src/core/shared/errors.py`.
  - Ensure resilience against edge cases; avoid silent failures.

- **Naming Conventions**
  - Be deliberate and descriptive. Prefer full words to abbreviations.
  - Variables: short but precise (e.g., `start_time`, `user_payload`, `max_retry`).
  - Functions: verb phrases (e.g., `parse_config_file`, `fetch_user_records`).
  - Classes: clear nouns (e.g., `SessionManager`, `DataValidator`).

- **Commenting Principles**
  - Comment to clarify why and non-obvious how; avoid narrating obvious code.
  - Avoid addressing the reader directly; comments should read like documentation.

- **Code Quality and Style**
  - Python 3.12+, PEP 8 and PEP 257. Strict type hints; avoid `Any`.
  - Prefer small, single-purpose functions; refactor complex logic into helpers.
  - Use `dataclasses` with `field(default_factory=...)` for mutables.
  - Reference related entities by ID, not embedding full objects.

- **Logging Doctrine (Bell Labs rigor)**
  - Verbose, precise, structured logs that expose state and parameters.
  - Levels: DEBUG (decisions/computations), INFO (domain events/state transitions), WARNING (recoverable anomalies), ERROR (domain/infra failures).
  - Include identifiers and parameters in all logs; no PII leakage.
  - Example:
    ```python
    logger.info(
        "event=WorkoutStarted user_id=%s workout_id=%s template_id=%s parameters=%s",
        user_id,
        workout.id,
        template_id,
        {"exercise_count": len(workout.exercises)},
    )
    ```

## Information Sources (Read before coding)

- **Cursor Rules**: Global and package-specific rules in `.cursor/rules/` auto-attach during edits. Treat them as the source of truth for responsibilities, invariants, logging, and coding standards.
- **Tests**: `tests/` defines expected behavior; prefer implementing to pass tests over speculative features.
- **Repository layout**: Follow the directory responsibilities outlined below; do not introduce circular imports.
- **README.md / CLAUDE.md**: High-level goals, commands, and operating procedures.

## Architecture Overview

Vigor is structured as follows:
```
src/core/
├── models/          # Domain entities (User, Workout, etc.)
├── repositories/    # Abstract interfaces for persistence
│   └── protocols.py
├── domain_logic/    # Pure computation functions
├── services/        # Business rules and orchestration
├── use_cases/       # Cross-domain orchestrators
└── shared/          # Cross-cutting concerns (errors, etc.)

src/infra/           # Infrastructure implementations
└── repositories/    # In-memory repository implementations

tests/               # Integration and unit tests
```

### Domain Models

- **User Domain** (`models/user.py`)
  - `User`, `UserProfile`, `UserPreferences`, `UserMemory`, `FitnessGoal`

- **Workout Domain** (`models/workout.py`)
  - `ExerciseDefinition`, `Workout`, `WorkoutExercise`, `ExerciseSet`, `PersonalRecord`

### Dependency Rules

1. models → repositories.protocols → repositories.impl
2. domain_logic (pure) → consumed by services
3. services → depend on repositories.protocols, domain_logic, shared
4. use_cases → orchestrate multiple services and repositories
5. infra → implements repository protocols
6. API/UI → talk to use_cases/services only

## Change Management Workflow

1. Commence with a brief discovery pass: read relevant files and Cursor Rules for the target area.
2. Propose minimal, cohesive edits aligned with dependency direction and package responsibilities.
3. Execute tests locally; keep a green test suite.
4. Add/adjust unit tests close to the unit when introducing new behavior.
5. Keep services ≤ ~300 lines; split when approaching complexity limits.
6. Avoid circular imports and cross-service implementation imports; orchestrate in `use_cases` if needed.

## Initialization and Scaffolding Boundaries

- Do not create directories or opinionated scaffolding during initialization.
- Operate within the existing repository layout. When a new file is essential, place it in the minimal stable location consistent with responsibilities.
- Prefer editing existing files over expanding surface area.

## Immediate Priorities and Roadmap

- Immediate: ensure `workout.session_service` and `workout.tracking_service` support starting workouts, logging sets, and completing sessions; wire through `use_cases`.
- Next: add `analytics.metrics_service` using `domain_logic` aggregators and estimators; compute volume and strength estimates.
- Then: introduce `planning.schedule_service` and `program_service`; manage scheduled workouts and templates.
- Progressive enhancement: events for `WorkoutCompleted`, PR detection, and AI-driven insights.

## Development Commands

### Testing
```bash
# Run all tests
pytest -q

# Run tests with Python path
python -m pytest -q

# Run specific test
pytest tests/test_user_workout_flow.py -q
```

### Environment Setup
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install pytest

# Or run tests without venv
uvx pytest -q
```

## Code Standards (Enforced)

- Python 3.12+; PEP 8 and PEP 257.
- Strict type hints on public APIs and models; avoid `Any`.
- Dataclasses: `field(default_factory=...)` for mutables; required fields have no defaults; use UUIDs and timestamps.
- Explicit exceptions from `src/core/shared/errors.py` for domain and infra failures.
- Structured, parameterized logs; include identifiers and inputs.
- Tests: write/modify tests alongside feature changes; keep them fast and explicit.

## Cursor Rules Integration

- Global standards live in `.cursor/rules/` and auto-attach when editing code.
- Use these rules to determine responsibilities, non-goals, logging doctrine, and coding standards per package.
- When rules and code diverge, reconcile by aligning code to rules or updating tests and rules in the same change set with rationale.