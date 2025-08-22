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
	 PersonalRecord,
)


def test_exercise_definition_search_and_find():
	"""
	Test that the exercise definition repository can save and retrieve exercise definitions, and that the secondary indexes are updated correctly.
	"""
	repo = InMemoryExerciseDefinitionRepository()
	ex1 = ExerciseDefinition(
		name="Bench Press",
		primary_muscles=[MuscleGroup.CHEST],
		equipment=EquipmentType.BARBELL,
		mechanics=MechanicsType.COMPOUND,
		movement_pattern=MovementPattern.HORIZONTAL_PRESS,
	)
	repo.save(ex1)
	assert repo.find_by_name("Bench Press") is not None
	res = repo.search(muscle_groups=["chest"], equipment=["barbell"])
	assert len(res) == 1


def test_workout_and_exercise_repos():
	"""
	Test that the workout and workout exercise repositories can save and retrieve workouts and workout exercises.
	"""
	w_repo = InMemoryWorkoutRepository()
	we_repo = InMemoryWorkoutExerciseRepository()
	s_repo = InMemoryExerciseSetRepository()

	w = Workout(user_id="u1")
	w_repo.save(w)
	assert w_repo.get_by_id(w.id) is not None

	we = WorkoutExercise(workout_id=w.id, exercise_id="ex1", order_index=0)
	we_repo.save(we)
	assert we_repo.get_by_id(we.id) is not None
	assert len(we_repo.list_by_workout(w.id)) == 1

	s = ExerciseSet(workout_exercise_id=we.id, set_number=1, load_type=None, weight_kg=50.0, reps=10)
	s_repo.save(s)
	assert len(s_repo.list_for_workout_exercise(we.id)) == 1


def test_personal_record_repo_best():
	"""
	Test that the personal record repository can save and retrieve personal records.
	"""
	pr_repo = InMemoryPersonalRecordRepository()
	pr1 = PersonalRecord(user_id="u1", exercise_id="ex1", record_type=None, achieved_at=None, weight_kg=100.0)  # type: ignore[arg-type]
	pr2 = PersonalRecord(user_id="u1", exercise_id="ex1", record_type=None, achieved_at=None, weight_kg=110.0)  # type: ignore[arg-type]
	pr_repo.save(pr1)
	pr_repo.save(pr2)
	best = pr_repo.get_best_one_rm("u1", "ex1")
	assert best is not None and best.weight_kg == 110.0

