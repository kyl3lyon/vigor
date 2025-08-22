from src.infra.repositories.memory_workout import InMemoryExerciseDefinitionRepository
from src.core.services.workout.exercise_service import ExerciseService
from src.core.models import EquipmentType, MuscleGroup, MechanicsType, MovementPattern
from src.core.shared.errors import ValidationError


def test_create_definition_and_prevent_duplicate_same_mechanics():
	 repo = InMemoryExerciseDefinitionRepository()
	 svc = ExerciseService(repo)
	 ex = svc.create_definition(
		 name="Bench Press",
		 primary_muscles=[MuscleGroup.CHEST],
		 equipment=EquipmentType.BARBELL,
		 mechanics=MechanicsType.COMPOUND,
		 movement_pattern=MovementPattern.HORIZONTAL_PRESS,
	 )
	 assert repo.find_by_name("Bench Press") is not None
	 # same name and same mechanics/equipment/pattern -> reject
	 try:
		 svc.create_definition(
			 name="Bench Press",
			 primary_muscles=[MuscleGroup.CHEST],
			 equipment=EquipmentType.BARBELL,
			 mechanics=MechanicsType.COMPOUND,
			 movement_pattern=MovementPattern.HORIZONTAL_PRESS,
		 )
		 assert False, "expected ValidationError for duplicate definition"
	 except ValidationError:
		 pass


