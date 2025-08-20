from typing import List, Optional

from src.core.models import ExerciseDefinition, EquipmentType, MuscleGroup, MechanicsType, MovementPattern
from src.core.repositories.protocols import ExerciseDefinitionRepository
from src.core.shared.errors import ValidationError


class ExerciseService:
	 def __init__(self, repo: ExerciseDefinitionRepository) -> None:
		 self._repo = repo

	 def create_definition(
		 self,
		 *,
		 name: str,
		 primary_muscles: List[MuscleGroup],
		 equipment: EquipmentType,
		 mechanics: MechanicsType,
		 movement_pattern: MovementPattern,
		 secondary_muscles: Optional[List[MuscleGroup]] = None,
		 aliases: Optional[List[str]] = None,
		 is_unilateral: bool = False,
	 ) -> ExerciseDefinition:
		 if not name:
			 raise ValidationError("name: required")
		 if not primary_muscles:
			 raise ValidationError("primary_muscles: required")
		 existing = self._repo.find_by_name(name)
		 if existing is not None:
			 # allow duplicate names only if mechanics/equipment/pattern differ
			 if (
				 existing.mechanics == mechanics
				 and existing.equipment == equipment
				 and existing.movement_pattern == movement_pattern
			 ):
				 raise ValidationError("exercise definition already exists with same mechanics/equipment/pattern")
		 ex = ExerciseDefinition(
			 name=name,
			 primary_muscles=primary_muscles,
			 equipment=equipment,
			 mechanics=mechanics,
			 movement_pattern=movement_pattern,
			 secondary_muscles=secondary_muscles or [],
			 aliases=aliases or [],
			 is_unilateral=is_unilateral,
		 )
		 return self._repo.save(ex)

	 def search(
		 self,
		 *,
		 muscle_groups: Optional[List[MuscleGroup]] = None,
		 equipment: Optional[List[EquipmentType]] = None,
	 ) -> List[ExerciseDefinition]:
		 mg = [m.value for m in muscle_groups] if muscle_groups else None
		 eq = [e.value for e in equipment] if equipment else None
		 return self._repo.search(muscle_groups=mg, equipment=eq)


