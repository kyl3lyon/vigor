from collections import defaultdict
from typing import Dict, List

from src.core.models import ExerciseSet, WorkoutExercise, ExerciseDefinition, MuscleGroup, MovementPattern


def total_volume_kg(sets: List[ExerciseSet]) -> float:
	 total = 0.0
	 for s in sets:
		 if s.weight_kg is not None and s.reps is not None:
			 total += s.weight_kg * float(s.reps)
	 return total


def volume_by_muscle_group(
	 sets: List[ExerciseSet],
	 workout_exercises: Dict[str, WorkoutExercise],
	 exercises: Dict[str, ExerciseDefinition],
) -> Dict[MuscleGroup, float]:
	 volumes: Dict[MuscleGroup, float] = defaultdict(float)
	 for s in sets:
		 we = workout_exercises.get(s.workout_exercise_id)
		 if we is None:
			 continue
		 ex = exercises.get(we.exercise_id)
		 if ex is None:
			 continue
		 if s.weight_kg is not None and s.reps is not None:
			 v = s.weight_kg * float(s.reps)
			 for mg in ex.primary_muscles:
				 volumes[mg] += v
	 return dict(volumes)


def volume_by_movement_pattern(
	 sets: List[ExerciseSet],
	 workout_exercises: Dict[str, WorkoutExercise],
	 exercises: Dict[str, ExerciseDefinition],
) -> Dict[MovementPattern, float]:
	 volumes: Dict[MovementPattern, float] = defaultdict(float)
	 for s in sets:
		 we = workout_exercises.get(s.workout_exercise_id)
		 if we is None:
			 continue
		 ex = exercises.get(we.exercise_id)
		 if ex is None:
			 continue
		 if s.weight_kg is not None and s.reps is not None:
			 v = s.weight_kg * float(s.reps)
			 volumes[ex.movement_pattern] += v
	 return dict(volumes)


