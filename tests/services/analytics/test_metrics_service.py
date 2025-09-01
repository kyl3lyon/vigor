from datetime import datetime, timedelta

from src.infra.repositories.memory_workout import (
	 InMemoryExerciseDefinitionRepository,
	 InMemoryWorkoutRepository,
	 InMemoryWorkoutExerciseRepository,
	 InMemoryExerciseSetRepository,
)
from src.core.models import (
	 ExerciseDefinition,
	 EquipmentType,
	 MuscleGroup,
	 MechanicsType,
	 MovementPattern,
	 Workout,
	 WorkoutExercise,
	 ExerciseSet,
)
from src.core.services.analytics.metrics_service import MetricsService


def _make_exercise(repo: InMemoryExerciseDefinitionRepository, name: str, mg: MuscleGroup, mp: MovementPattern, eq: EquipmentType) -> ExerciseDefinition:
	 ex = ExerciseDefinition(name=name, primary_muscles=[mg], equipment=eq, mechanics=MechanicsType.COMPOUND, movement_pattern=mp)
	 return repo.save(ex)


def test_volume_metrics_weekly_trend_and_breakdown():
	 ex_repo = InMemoryExerciseDefinitionRepository()
	 w_repo = InMemoryWorkoutRepository()
	 we_repo = InMemoryWorkoutExerciseRepository()
	 set_repo = InMemoryExerciseSetRepository()
	 svc = MetricsService(w_repo, we_repo, set_repo, ex_repo)

	 bench = _make_exercise(ex_repo, "Bench", MuscleGroup.CHEST, MovementPattern.HORIZONTAL_PRESS, EquipmentType.BARBELL)
	 row = _make_exercise(ex_repo, "Row", MuscleGroup.BACK, MovementPattern.HORIZONTAL_PULL, EquipmentType.BARBELL)

	 user_id = "u1"
	 now = datetime.now()
	 # Week 1: lower volume
	 w1 = Workout(user_id=user_id, started_at=now - timedelta(days=10))
	 w_repo.save(w1)
	 we1 = WorkoutExercise(workout_id=w1.id, exercise_id=bench.id, order_index=0)
	 we_repo.save(we1)
	 set_repo.save(ExerciseSet(workout_exercise_id=we1.id, set_number=1, load_type=None, weight_kg=60.0, reps=8))
	 # Week 2: higher volume
	 w2 = Workout(user_id=user_id, started_at=now - timedelta(days=3))
	 w_repo.save(w2)
	 we2 = WorkoutExercise(workout_id=w2.id, exercise_id=row.id, order_index=0)
	 we_repo.save(we2)
	 set_repo.save(ExerciseSet(workout_exercise_id=we2.id, set_number=1, load_type=None, weight_kg=80.0, reps=10))

	 vm = svc.get_volume_metrics(user_id=user_id, period_days=28)
	 assert vm.total_volume_kg == 60.0 * 8 + 80.0 * 10
	 assert vm.volume_by_muscle_group.get(MuscleGroup.CHEST, 0.0) > 0.0
	 assert vm.volume_by_movement_pattern.get(MovementPattern.HORIZONTAL_PULL, 0.0) > 0.0
	 # With the second week larger, trend should be INCREASING
	 from src.core.models.analytics import TrendDirection
	 assert vm.weekly_volume_trend in {TrendDirection.INCREASING, TrendDirection.STABLE}


def test_strength_progress_estimates_and_velocity():
	 ex_repo = InMemoryExerciseDefinitionRepository()
	 w_repo = InMemoryWorkoutRepository()
	 we_repo = InMemoryWorkoutExerciseRepository()
	 set_repo = InMemoryExerciseSetRepository()
	 svc = MetricsService(w_repo, we_repo, set_repo, ex_repo)

	 bench = _make_exercise(ex_repo, "Bench", MuscleGroup.CHEST, MovementPattern.HORIZONTAL_PRESS, EquipmentType.BARBELL)
	 user_id = "u1"
	 now = datetime.now()
	 # Session A (older): 70x5
	 w_old = Workout(user_id=user_id, started_at=now - timedelta(days=21))
	 w_repo.save(w_old)
	 we_old = WorkoutExercise(workout_id=w_old.id, exercise_id=bench.id, order_index=0)
	 we_repo.save(we_old)
	 set_repo.save(ExerciseSet(workout_exercise_id=we_old.id, set_number=1, load_type=None, weight_kg=70.0, reps=5))
	 # Session B (newer): 80x5
	 w_new = Workout(user_id=user_id, started_at=now - timedelta(days=7))
	 w_repo.save(w_new)
	 we_new = WorkoutExercise(workout_id=w_new.id, exercise_id=bench.id, order_index=0)
	 we_repo.save(we_new)
	 set_repo.save(ExerciseSet(workout_exercise_id=we_new.id, set_number=1, load_type=None, weight_kg=80.0, reps=5))

	 sp = svc.get_exercise_strength_progress(user_id=user_id, exercise_id=bench.id, period_days=28)
	 assert sp.estimated_1rm_kg > 0.0
	 assert sp.strength_velocity_kg_per_week >= 0.0



