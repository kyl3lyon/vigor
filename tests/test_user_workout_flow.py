from datetime import datetime

from src.core.models import EquipmentType, MuscleGroup, MechanicsType, MovementPattern
from src.core.services.user.user_service import UserService
from src.core.services.workout.exercise_service import ExerciseService
from src.core.services.workout.session_service import SessionService
from src.core.services.workout.tracking_service import TrackingService
from src.core.domain_logic.volume_aggregators import (
	 total_volume_kg,
	 volume_by_muscle_group,
	 volume_by_movement_pattern,
)
from src.infra.repositories.memory_user import (
	 InMemoryUserRepository,
)
from src.infra.repositories.memory_workout import (
	 InMemoryExerciseDefinitionRepository,
	 InMemoryWorkoutRepository,
	 InMemoryWorkoutExerciseRepository,
	 InMemoryExerciseSetRepository,
	 InMemoryPersonalRecordRepository,
)


def test_end_to_end_user_workout_flow():
	 # Arrange: repositories
	 user_repo = InMemoryUserRepository()
	 ex_repo = InMemoryExerciseDefinitionRepository()
	 workout_repo = InMemoryWorkoutRepository()
	 we_repo = InMemoryWorkoutExerciseRepository()
	 set_repo = InMemoryExerciseSetRepository()
	 pr_repo = InMemoryPersonalRecordRepository()

	 # Arrange: services
	 user_svc = UserService(user_repo)
	 exercise_svc = ExerciseService(ex_repo)
	 session_svc = SessionService(workout_repo, we_repo)
	 tracking_svc = TrackingService(set_repo, we_repo, pr_repo)

	 # Act 1: create a user
	 user = user_svc.create_user(email="test@example.com", username="tester")

	 # Act 2: create an exercise definition (Barbell Bench Press)
	 bench = exercise_svc.create_definition(
		 name="Barbell Bench Press",
		 primary_muscles=[MuscleGroup.CHEST],
		 equipment=EquipmentType.BARBELL,
		 mechanics=MechanicsType.COMPOUND,
		 movement_pattern=MovementPattern.HORIZONTAL_PRESS,
	 )

	 # Act 3: start a workout session
	 workout = session_svc.start_workout(user_id=user.id, title="Upper Body")

	 # Act 4: add exercise to workout
	 we = session_svc.add_exercise(workout_id=workout.id, exercise_id=bench.id, order_index=0)

	 # Act 5: log sets, including a top set
	 s1 = tracking_svc.log_set(we.id, set_number=1, weight_kg=60.0, reps=8, rpe=6.5)
	 s2 = tracking_svc.log_set(we.id, set_number=2, weight_kg=70.0, reps=5, rpe=8.0)
	 s3 = tracking_svc.log_set(we.id, set_number=3, weight_kg=80.0, reps=3, rpe=9.0)

	 # Act 6: evaluate PR based on top set
	 pr = tracking_svc.evaluate_prs(user_id=user.id, exercise_id=bench.id, weight_kg=80.0, reps=3, achieved_at=datetime.now())

	 # Assert: entities and calculations
	 assert user_repo.find_by_email("test@example.com") is not None
	 assert workout_repo.get_by_id(workout.id) is not None
	 assert we_repo.get_by_id(we.id) is not None

	 sets = set_repo.list_for_workout_exercise(we.id)
	 assert len(sets) == 3
	 assert total_volume_kg(sets) > 0.0

	 # Build dictionaries needed for aggregation helpers
	 wes = {we.id: we}
	 exs = {bench.id: bench}
	 vol_by_mg = volume_by_muscle_group(sets, wes, exs)
	 vol_by_mp = volume_by_movement_pattern(sets, wes, exs)
	 assert vol_by_mg.get(MuscleGroup.CHEST, 0.0) > 0.0
	 assert vol_by_mp.get(MovementPattern.HORIZONTAL_PRESS, 0.0) > 0.0

	 # PR created or not None if better than previous
	 assert pr is not None
	 best = pr_repo.get_best_one_rm(user.id, bench.id)
	 assert best is not None and (best.weight_kg or 0.0) > 0.0


