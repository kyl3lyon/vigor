from dataclasses import replace
from datetime import datetime
from typing import Optional, List

from src.core.models import Workout, WorkoutExercise
from src.core.repositories.protocols import WorkoutRepository, WorkoutExerciseRepository
from src.core.shared.errors import ValidationError, NotFoundError


class SessionService:
	 def __init__(self, workout_repo: WorkoutRepository, we_repo: WorkoutExerciseRepository) -> None:
		 self._workouts = workout_repo
		 self._wes = we_repo

	 def start_workout(self, user_id: str, title: Optional[str] = None, notes: Optional[str] = None) -> Workout:
		 if not user_id:
			 raise ValidationError("user_id: required")
		 w = Workout(user_id=user_id, title=title, notes=notes, started_at=datetime.now())
		 return self._workouts.save(w)

	 def add_exercise(self, workout_id: str, exercise_id: str, order_index: int) -> WorkoutExercise:
		 if order_index < 0:
			 raise ValidationError("order_index: must be >= 0")
		 workout = self._require_workout(workout_id)
		 we = WorkoutExercise(workout_id=workout.id, exercise_id=exercise_id, order_index=order_index)
		 return self._wes.save(we)

	 def complete_workout(self, workout_id: str, *, session_rpe: Optional[float] = None, duration_seconds: Optional[int] = None) -> Workout:
		 workout = self._require_workout(workout_id)
		 updated = replace(
			 workout,
			 session_rpe=session_rpe if session_rpe is not None else workout.session_rpe,
			 duration_seconds=duration_seconds if duration_seconds is not None else workout.duration_seconds,
			 completed_at=datetime.now(),
			 updated_at=datetime.now(),
		 )
		 return self._workouts.update(updated)

	 def _require_workout(self, workout_id: str) -> Workout:
		 w = self._workouts.get_by_id(workout_id)
		 if w is None:
			 raise NotFoundError("workout: not found")
		 return w


