from dataclasses import replace
from datetime import datetime
from typing import Optional

from src.core.models import ExerciseSet, WorkoutExercise, PersonalRecord, PRType
from src.core.repositories.protocols import ExerciseSetRepository, WorkoutExerciseRepository, PersonalRecordRepository
from src.core.shared.errors import ValidationError, NotFoundError
from src.core.domain_logic.strength_estimators import blended_1rm_estimate


class TrackingService:
	 def __init__(self, set_repo: ExerciseSetRepository, we_repo: WorkoutExerciseRepository, pr_repo: PersonalRecordRepository) -> None:
		 self._sets = set_repo
		 self._wes = we_repo
		 self._prs = pr_repo

	 def log_set(
		 self,
		 workout_exercise_id: str,
		 *,
		 set_number: int,
		 weight_kg: Optional[float] = None,
		 reps: Optional[int] = None,
		 rpe: Optional[float] = None,
		 is_failure: bool = False,
	 ) -> ExerciseSet:
		 if set_number < 1:
			 raise ValidationError("set_number: must be >= 1")
		 we = self._require_we(workout_exercise_id)
		 # Determine load_type based on weight presence
		 from src.core.models import LoadType
		 load_type = LoadType.EXTERNAL if weight_kg is not None else LoadType.NONE
		 s = ExerciseSet(
			 workout_exercise_id=we.id,
			 set_number=set_number,
			 load_type=load_type,
			 weight_kg=weight_kg,
			 reps=reps,
			 rpe=rpe,
			 is_failure=is_failure,
		 )
		 return self._sets.save(s)

	 def evaluate_prs(self, user_id: str, exercise_id: str, *, weight_kg: float, reps: int, achieved_at: Optional[datetime] = None) -> Optional[PersonalRecord]:
		 est = blended_1rm_estimate(weight_kg, reps)
		 if est is None:
			 return None
		 best = self._prs.get_best_one_rm(user_id, exercise_id)
		 if best is None or (est > (best.weight_kg or 0.0)):
			 pr = PersonalRecord(
				 user_id=user_id,
				 exercise_id=exercise_id,
				 record_type=PRType.ONE_RM,
				 achieved_at=achieved_at or datetime.now(),
				 weight_kg=est,
			 )
			 return self._prs.save(pr)
		 return None

	 def _require_we(self, workout_exercise_id: str) -> WorkoutExercise:
		 we = self._wes.get_by_id(workout_exercise_id)
		 if we is None:
			 raise NotFoundError("workout_exercise: not found")
		 return we


