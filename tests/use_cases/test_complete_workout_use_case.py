from src.infra.repositories.memory_user import InMemoryUserRepository
from src.infra.repositories.memory_workout import (
	InMemoryExerciseDefinitionRepository,
	InMemoryWorkoutRepository,
	InMemoryWorkoutExerciseRepository,
	InMemoryExerciseSetRepository,
	InMemoryPersonalRecordRepository,
)
from src.core.services.user.user_service import UserService
from src.core.services.workout.exercise_service import ExerciseService
from src.core.services.workout.session_service import SessionService
from src.core.services.workout.tracking_service import TrackingService
from src.core.services.analytics.metrics_service import MetricsService
from src.core.services.analytics.insight_service import InsightService
from src.core.use_cases.complete_workout_use_case import CompleteWorkoutUseCase
from src.core.models import EquipmentType, MuscleGroup, MechanicsType, MovementPattern


def test_complete_workout_use_case_recomputes_metrics_and_insights():
	user_repo = InMemoryUserRepository()
	ex_repo = InMemoryExerciseDefinitionRepository()
	w_repo = InMemoryWorkoutRepository()
	we_repo = InMemoryWorkoutExerciseRepository()
	set_repo = InMemoryExerciseSetRepository()
	pr_repo = InMemoryPersonalRecordRepository()

	user_svc = UserService(user_repo)
	ex_svc = ExerciseService(ex_repo)
	session_svc = SessionService(w_repo, we_repo)
	tracking_svc = TrackingService(set_repo, we_repo, pr_repo)
	metrics_svc = MetricsService(w_repo, we_repo, set_repo, ex_repo)
	insight_svc = InsightService(w_repo, we_repo, set_repo, ex_repo, pr_repo)

	use_case = CompleteWorkoutUseCase(
		session_service=session_svc,
		tracking_service=tracking_svc,
		metrics_service=metrics_svc,
		insight_service=insight_svc,
		we_repo=we_repo,
		set_repo=set_repo,
	)

	user = user_svc.create_user(email="test@example.com", username="test")
	bench = ex_svc.create_definition(
		name="Bench",
		primary_muscles=[MuscleGroup.CHEST],
		equipment=EquipmentType.BARBELL,
		mechanics=MechanicsType.COMPOUND,
		movement_pattern=MovementPattern.HORIZONTAL_PRESS,
	)
	w = session_svc.start_workout(user_id=user.id, title="Push")
	we = session_svc.add_exercise(w.id, bench.id, 0)
	tracking_svc.log_set(we.id, set_number=1, weight_kg=80.0, reps=5)

	result = use_case.execute(workout_id=w.id, session_rpe=8.0, duration_seconds=3600)
	assert result.workout.completed_at is not None
	assert result.volume_metrics.total_volume_kg > 0
	assert isinstance(result.achievements, list)

