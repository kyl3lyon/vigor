from src.infra.repositories.memory_workout import (
	 InMemoryExerciseSetRepository,
	 InMemoryWorkoutExerciseRepository,
	 InMemoryPersonalRecordRepository,
)
from src.core.services.workout.tracking_service import TrackingService
from src.core.models import WorkoutExercise
from src.core.shared.errors import ValidationError, NotFoundError


def test_log_set_defaults_and_pr_logic():
	 set_repo = InMemoryExerciseSetRepository()
	 we_repo = InMemoryWorkoutExerciseRepository()
	 pr_repo = InMemoryPersonalRecordRepository()
	 svc = TrackingService(set_repo, we_repo, pr_repo)
	 # missing WE should raise
	 try:
		 svc.log_set("missing", set_number=1, weight_kg=60.0, reps=8)
		 assert False, "expected NotFoundError"
	 except NotFoundError:
		 pass
	 # create WE and log sets
	 we = WorkoutExercise(workout_id="w1", exercise_id="ex1", order_index=0)
	 we_repo.save(we)
	 s = svc.log_set(we.id, set_number=1, weight_kg=60.0, reps=8)
	 # set_number bound
	 try:
		 svc.log_set(we.id, set_number=0, weight_kg=60.0, reps=8)
		 assert False, "expected ValidationError for set_number"
	 except ValidationError:
		 pass
	 # PR evaluate (first one creates)
	 pr1 = svc.evaluate_prs(user_id="u1", exercise_id="ex1", weight_kg=80.0, reps=3)
	 assert pr1 is not None
	 # non-improving should return None
	 pr2 = svc.evaluate_prs(user_id="u1", exercise_id="ex1", weight_kg=70.0, reps=2)
	 assert pr2 is None


