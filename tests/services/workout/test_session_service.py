from src.infra.repositories.memory_workout import InMemoryWorkoutRepository, InMemoryWorkoutExerciseRepository
from src.core.services.workout.session_service import SessionService
from src.core.shared.errors import ValidationError


def test_start_add_complete_workout():
	 w_repo = InMemoryWorkoutRepository()
	 we_repo = InMemoryWorkoutExerciseRepository()
	 svc = SessionService(w_repo, we_repo)
	 # start
	 w = svc.start_workout(user_id="u1", title="Push Day")
	 assert w.started_at is not None
	 # add exercise
	 we = svc.add_exercise(workout_id=w.id, exercise_id="ex1", order_index=0)
	 assert we_repo.get_by_id(we.id) is not None
	 # invalid order
	 try:
		 svc.add_exercise(workout_id=w.id, exercise_id="ex2", order_index=-1)
		 assert False, "expected ValidationError"
	 except ValidationError:
		 pass
	 # complete
	 w2 = svc.complete_workout(w.id, session_rpe=8.0, duration_seconds=3600)
	 assert w2.completed_at is not None and w2.session_rpe == 8.0 and w2.duration_seconds == 3600


