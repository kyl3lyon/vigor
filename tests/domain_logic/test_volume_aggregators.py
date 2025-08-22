from src.core.models import (
	 ExerciseSet,
	 WorkoutExercise,
	 ExerciseDefinition,
	 EquipmentType,
	 MuscleGroup,
	 MechanicsType,
	 MovementPattern,
)
from src.core.domain_logic.volume_aggregators import (
	 total_volume_kg,
	 volume_by_muscle_group,
	 volume_by_movement_pattern,
)


def _make_exercise_definition(exercise_id: str) -> ExerciseDefinition:
	 return ExerciseDefinition(
		 name="Bench Press",
		 primary_muscles=[MuscleGroup.CHEST],
		 equipment=EquipmentType.BARBELL,
		 mechanics=MechanicsType.COMPOUND,
		 movement_pattern=MovementPattern.HORIZONTAL_PRESS,
		 id=exercise_id,
	 )


def _make_workout_exercise(we_id: str, workout_id: str, exercise_id: str) -> WorkoutExercise:
	 return WorkoutExercise(workout_id=workout_id, exercise_id=exercise_id, order_index=0, id=we_id)


def test_total_volume_kg():
	 sets = [
		 ExerciseSet(workout_exercise_id="we1", set_number=1, load_type=None, weight_kg=60.0, reps=8),
		 ExerciseSet(workout_exercise_id="we1", set_number=2, load_type=None, weight_kg=70.0, reps=5),
	 ]
	 assert total_volume_kg(sets) == 60.0 * 8 + 70.0 * 5


def test_volume_by_muscle_group_and_movement():
	 ex_id = "ex1"
	 we_id = "we1"
	 w_id = "w1"
	 ex = _make_exercise_definition(ex_id)
	 we = _make_workout_exercise(we_id, w_id, ex_id)
	 sets = [
		 ExerciseSet(workout_exercise_id=we_id, set_number=1, load_type=None, weight_kg=60.0, reps=8),
		 ExerciseSet(workout_exercise_id=we_id, set_number=2, load_type=None, weight_kg=70.0, reps=5),
	 ]
	 wes = {we_id: we}
	 exs = {ex_id: ex}

	 v_mg = volume_by_muscle_group(sets, wes, exs)
	 v_mp = volume_by_movement_pattern(sets, wes, exs)

	 expected = 60.0 * 8 + 70.0 * 5
	 assert v_mg.get(MuscleGroup.CHEST, 0.0) == expected
	 assert v_mp.get(MovementPattern.HORIZONTAL_PRESS, 0.0) == expected

