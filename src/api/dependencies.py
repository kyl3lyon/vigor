import os
from functools import lru_cache

from src.infra.repositories.memory_user import (
	InMemoryUserRepository,
	InMemoryUserProfileRepository,
	InMemoryUserPreferencesRepository,
	InMemoryFitnessGoalRepository,
	InMemoryUserMemoryRepository,
)
from src.infra.repositories.memory_workout import (
	InMemoryExerciseDefinitionRepository,
	InMemoryWorkoutRepository,
	InMemoryWorkoutExerciseRepository,
	InMemoryExerciseSetRepository,
	InMemoryPersonalRecordRepository,
)
from src.infra.repositories.memory_planning import (
	InMemoryWorkoutTemplateRepository,
	InMemoryWorkoutExerciseTemplateRepository,
	InMemoryTrainingProgramRepository,
	InMemoryProgramPhaseRepository,
	InMemoryProgramEnrollmentRepository,
	InMemoryScheduledWorkoutRepository,
)

USE_SQLITE = os.getenv("DB_PATH") is not None
if USE_SQLITE:
	from src.infra.repositories.sqlite_connection import get_connection
	from src.infra.repositories.sqlite_user import (
		SQLiteUserRepository,
		SQLiteUserProfileRepository,
		SQLiteUserPreferencesRepository,
		SQLiteFitnessGoalRepository,
		SQLiteUserMemoryRepository,
	)
	from src.infra.repositories.sqlite_workout import (
		SQLiteExerciseDefinitionRepository,
		SQLiteWorkoutRepository,
		SQLiteWorkoutExerciseRepository,
		SQLiteExerciseSetRepository,
		SQLitePersonalRecordRepository,
	)
	from src.infra.repositories.sqlite_planning import (
		SQLiteWorkoutTemplateRepository,
		SQLiteWorkoutExerciseTemplateRepository,
		SQLiteScheduledWorkoutRepository,
	)
	_CONN = get_connection(os.getenv("DB_PATH", "vigor.db"))

# Shared singleton repos for in-memory mode
_user_repo = InMemoryUserRepository()
_profile_repo = InMemoryUserProfileRepository()
_prefs_repo = InMemoryUserPreferencesRepository()
_goal_repo = InMemoryFitnessGoalRepository()
_memory_repo = InMemoryUserMemoryRepository()
_ex_repo = InMemoryExerciseDefinitionRepository()
_workout_repo = InMemoryWorkoutRepository()
_we_repo = InMemoryWorkoutExerciseRepository()
_set_repo = InMemoryExerciseSetRepository()
_pr_repo = InMemoryPersonalRecordRepository()
_wt_repo = InMemoryWorkoutTemplateRepository()
_wet_repo = InMemoryWorkoutExerciseTemplateRepository()
_prog_repo = InMemoryTrainingProgramRepository()
_phase_repo = InMemoryProgramPhaseRepository()
_enroll_repo = InMemoryProgramEnrollmentRepository()
_sched_repo = InMemoryScheduledWorkoutRepository()
from src.core.services.user.user_service import UserService
from src.core.services.user.profile_service import ProfileService
from src.core.services.user.goal_service import GoalService
from src.core.services.workout.exercise_service import ExerciseService
from src.core.services.workout.session_service import SessionService
from src.core.services.workout.tracking_service import TrackingService
from src.core.services.planning.template_service import TemplateService
from src.core.services.planning.program_service import ProgramService
from src.core.services.planning.schedule_service import ScheduleService
from src.core.services.analytics.metrics_service import MetricsService
from src.core.services.analytics.insight_service import InsightService
from src.core.use_cases.complete_workout_use_case import CompleteWorkoutUseCase


@lru_cache
def get_user_service() -> UserService:
	if USE_SQLITE:
		return UserService(SQLiteUserRepository(_CONN))
	return UserService(_user_repo)


@lru_cache
def get_profile_service() -> ProfileService:
	if USE_SQLITE:
		return ProfileService(SQLiteUserProfileRepository(_CONN), SQLiteUserPreferencesRepository(_CONN))
	return ProfileService(_profile_repo, _prefs_repo)


@lru_cache
def get_goal_service() -> GoalService:
	if USE_SQLITE:
		return GoalService(SQLiteFitnessGoalRepository(_CONN))
	return GoalService(_goal_repo)


@lru_cache
def get_exercise_service() -> ExerciseService:
	if USE_SQLITE:
		return ExerciseService(SQLiteExerciseDefinitionRepository(_CONN))
	return ExerciseService(_ex_repo)


@lru_cache
def get_session_service() -> SessionService:
	if USE_SQLITE:
		return SessionService(SQLiteWorkoutRepository(_CONN), SQLiteWorkoutExerciseRepository(_CONN))
	return SessionService(_workout_repo, _we_repo)


@lru_cache
def get_tracking_service() -> TrackingService:
	if USE_SQLITE:
		return TrackingService(
			SQLiteExerciseSetRepository(_CONN),
			SQLiteWorkoutExerciseRepository(_CONN),
			SQLitePersonalRecordRepository(_CONN),
		)
	return TrackingService(_set_repo, _we_repo, _pr_repo)


@lru_cache
def get_template_service() -> TemplateService:
	if USE_SQLITE:
		return TemplateService(SQLiteWorkoutTemplateRepository(_CONN), SQLiteWorkoutExerciseTemplateRepository(_CONN))
	return TemplateService(_wt_repo, _wet_repo)


@lru_cache
def get_program_service() -> ProgramService:
	return ProgramService(_prog_repo, _phase_repo, _enroll_repo)


@lru_cache
def get_schedule_service() -> ScheduleService:
	if USE_SQLITE:
		return ScheduleService(SQLiteScheduledWorkoutRepository(_CONN))
	return ScheduleService(_sched_repo)


@lru_cache
def get_metrics_service() -> MetricsService:
	if USE_SQLITE:
		return MetricsService(
			SQLiteWorkoutRepository(_CONN),
			SQLiteWorkoutExerciseRepository(_CONN),
			SQLiteExerciseSetRepository(_CONN),
			SQLiteExerciseDefinitionRepository(_CONN),
		)
	return MetricsService(_workout_repo, _we_repo, _set_repo, _ex_repo)


@lru_cache
def get_insight_service() -> InsightService:
	if USE_SQLITE:
		return InsightService(
			SQLiteWorkoutRepository(_CONN),
			SQLiteWorkoutExerciseRepository(_CONN),
			SQLiteExerciseSetRepository(_CONN),
			SQLiteExerciseDefinitionRepository(_CONN),
			SQLitePersonalRecordRepository(_CONN),
		)
	return InsightService(_workout_repo, _we_repo, _set_repo, _ex_repo, _pr_repo)


@lru_cache
def get_complete_workout_use_case() -> CompleteWorkoutUseCase:
	if USE_SQLITE:
		return CompleteWorkoutUseCase(
			session_service=get_session_service(),
			tracking_service=get_tracking_service(),
			metrics_service=get_metrics_service(),
			insight_service=get_insight_service(),
			we_repo=SQLiteWorkoutExerciseRepository(_CONN),
			set_repo=SQLiteExerciseSetRepository(_CONN),
		)
	return CompleteWorkoutUseCase(
		session_service=get_session_service(),
		tracking_service=get_tracking_service(),
		metrics_service=get_metrics_service(),
		insight_service=get_insight_service(),
		we_repo=_we_repo,
		set_repo=_set_repo,
	)

