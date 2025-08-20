from typing import Optional, List, Dict

from src.core.models import (
	 ExerciseDefinition,
	 Workout,
	 WorkoutExercise,
	 ExerciseSet,
	 PersonalRecord,
)
from src.core.repositories.protocols import (
	 ExerciseDefinitionRepository,
	 WorkoutRepository,
	 WorkoutExerciseRepository,
	 ExerciseSetRepository,
	 PersonalRecordRepository,
)


class InMemoryExerciseDefinitionRepository(ExerciseDefinitionRepository):
	 def __init__(self) -> None:
		 self._by_id: Dict[str, ExerciseDefinition] = {}
		 self._by_name: Dict[str, List[ExerciseDefinition]] = {}

	 def save(self, ex: ExerciseDefinition) -> ExerciseDefinition:
		 self._by_id[ex.id] = ex
		 self._by_name.setdefault(ex.name.lower(), []).append(ex)
		 return ex

	 def get_by_id(self, exercise_id: str) -> Optional[ExerciseDefinition]:
		 return self._by_id.get(exercise_id)

	 def find_by_name(self, name: str) -> Optional[ExerciseDefinition]:
		 arr = self._by_name.get(name.lower())
		 return arr[0] if arr else None

	 def search(self, *, muscle_groups: Optional[List[str]] = None, equipment: Optional[List[str]] = None) -> List[ExerciseDefinition]:
		 out: List[ExerciseDefinition] = []
		 for ex in self._by_id.values():
			 if muscle_groups is not None:
				 if not any(mg.value in muscle_groups for mg in ex.primary_muscles):
					 continue
			 if equipment is not None and ex.equipment.value not in equipment:
				 continue
			 out.append(ex)
		 return out


class InMemoryWorkoutRepository(WorkoutRepository):
	 def __init__(self) -> None:
		 self._by_id: Dict[str, Workout] = {}
		 self._by_user: Dict[str, List[Workout]] = {}

	 def save(self, workout: Workout) -> Workout:
		 self._by_id[workout.id] = workout
		 self._by_user.setdefault(workout.user_id, []).append(workout)
		 return workout

	 def get_by_id(self, workout_id: str) -> Optional[Workout]:
		 return self._by_id.get(workout_id)

	 def update(self, workout: Workout) -> Workout:
		 self._by_id[workout.id] = workout
		 arr = self._by_user.get(workout.user_id, [])
		 for i, w in enumerate(arr):
			 if w.id == workout.id:
				 arr[i] = workout
				 break
		 return workout

	 def list_by_user_recent(self, user_id: str, limit: int = 20) -> List[Workout]:
		 return list(self._by_user.get(user_id, []))[-limit:]


class InMemoryWorkoutExerciseRepository(WorkoutExerciseRepository):
	 def __init__(self) -> None:
		 self._by_id: Dict[str, WorkoutExercise] = {}
		 self._by_workout: Dict[str, List[WorkoutExercise]] = {}

	 def save(self, we: WorkoutExercise) -> WorkoutExercise:
		 self._by_id[we.id] = we
		 self._by_workout.setdefault(we.workout_id, []).append(we)
		 return we

	 def list_by_workout(self, workout_id: str) -> List[WorkoutExercise]:
		 return list(self._by_workout.get(workout_id, []))

	 def get_by_id(self, workout_exercise_id: str) -> Optional[WorkoutExercise]:
		 return self._by_id.get(workout_exercise_id)


class InMemoryExerciseSetRepository(ExerciseSetRepository):
	 def __init__(self) -> None:
		 self._by_we: Dict[str, List[ExerciseSet]] = {}

	 def save(self, s: ExerciseSet) -> ExerciseSet:
		 self._by_we.setdefault(s.workout_exercise_id, []).append(s)
		 return s

	 def list_for_workout_exercise(self, workout_exercise_id: str) -> List[ExerciseSet]:
		 return list(self._by_we.get(workout_exercise_id, []))


class InMemoryPersonalRecordRepository(PersonalRecordRepository):
	 def __init__(self) -> None:
		 self._by_user_ex: Dict[tuple[str, str], List[PersonalRecord]] = {}

	 def save(self, pr: PersonalRecord) -> PersonalRecord:
		 key = (pr.user_id, pr.exercise_id)
		 self._by_user_ex.setdefault(key, []).append(pr)
		 return pr

	 def list_by_user_and_exercise(self, user_id: str, exercise_id: str) -> List[PersonalRecord]:
		 return list(self._by_user_ex.get((user_id, exercise_id), []))

	 def get_best_one_rm(self, user_id: str, exercise_id: str) -> Optional[PersonalRecord]:
		 prs = self._by_user_ex.get((user_id, exercise_id), [])
		 best = None
		 best_val = -1.0
		 for pr in prs:
			 if pr.weight_kg is not None and pr.weight_kg > best_val:
				 best = pr
				 best_val = pr.weight_kg
		 return best


