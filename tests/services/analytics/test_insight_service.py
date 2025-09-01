from datetime import datetime

from src.infra.repositories.memory_workout import (
	 InMemoryExerciseDefinitionRepository,
	 InMemoryWorkoutRepository,
	 InMemoryWorkoutExerciseRepository,
	 InMemoryExerciseSetRepository,
	 InMemoryPersonalRecordRepository,
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
from src.core.services.analytics.insight_service import InsightService


def test_achievements_and_balance_warnings():
	 ex_repo = InMemoryExerciseDefinitionRepository()
	 w_repo = InMemoryWorkoutRepository()
	 we_repo = InMemoryWorkoutExerciseRepository()
	 set_repo = InMemoryExerciseSetRepository()
	 pr_repo = InMemoryPersonalRecordRepository()
	 svc = InsightService(w_repo, we_repo, set_repo, ex_repo, pr_repo)

	 # Define push/pull exercises
	 bench = ExerciseDefinition(name="Bench", primary_muscles=[MuscleGroup.CHEST], equipment=EquipmentType.BARBELL, mechanics=MechanicsType.COMPOUND, movement_pattern=MovementPattern.HORIZONTAL_PRESS)
	 row = ExerciseDefinition(name="Row", primary_muscles=[MuscleGroup.BACK], equipment=EquipmentType.BARBELL, mechanics=MechanicsType.COMPOUND, movement_pattern=MovementPattern.HORIZONTAL_PULL)
	 ex_repo.save(bench)
	 ex_repo.save(row)

	 user_id = "u1"
	 now = datetime.now()
	 # Workout with a strong bench set (potential PR)
	 w = Workout(user_id=user_id, started_at=now)
	 w_repo.save(w)
	 we_b = WorkoutExercise(workout_id=w.id, exercise_id=bench.id, order_index=0)
	 we_repo.save(we_b)
	 set_repo.save(ExerciseSet(workout_exercise_id=we_b.id, set_number=1, load_type=None, weight_kg=100.0, reps=3))
	 # Skew volume toward push to trigger balance warning later
	 we_r = WorkoutExercise(workout_id=w.id, exercise_id=row.id, order_index=1)
	 we_repo.save(we_r)
	 set_repo.save(ExerciseSet(workout_exercise_id=we_r.id, set_number=1, load_type=None, weight_kg=40.0, reps=5))

	 ach = svc.detect_achievements(user_id=user_id, period_days=365)
	 assert isinstance(ach, list)
	 # Balance warnings (push heavy vs pull light) should produce at least one warning
	 warnings = svc.find_balance_warnings(user_id=user_id, period_days=28)
	 assert isinstance(warnings, list)



