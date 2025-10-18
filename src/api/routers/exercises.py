from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_exercise_service
from src.core.services.workout.exercise_service import ExerciseService
from src.core.models import EquipmentType, MuscleGroup, MechanicsType, MovementPattern
from src.core.shared.errors import ValidationError

router = APIRouter()


class CreateExerciseRequest(BaseModel):
	name: str
	primary_muscles: List[MuscleGroup]
	equipment: EquipmentType
	mechanics: MechanicsType
	movement_pattern: MovementPattern
	secondary_muscles: Optional[List[MuscleGroup]] = None
	aliases: Optional[List[str]] = None
	is_unilateral: bool = False


@router.post("/exercises")
def create_exercise(req: CreateExerciseRequest, svc: ExerciseService = Depends(get_exercise_service)):
	try:
		ex = svc.create_definition(
			name=req.name,
			primary_muscles=req.primary_muscles,
			equipment=req.equipment,
			mechanics=req.mechanics,
			movement_pattern=req.movement_pattern,
			secondary_muscles=req.secondary_muscles,
			aliases=req.aliases,
			is_unilateral=req.is_unilateral,
		)
		return {"exercise_id": ex.id, "name": ex.name}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/exercises")
def search_exercises(
	muscle_groups: Optional[str] = None,
	equipment: Optional[str] = None,
	svc: ExerciseService = Depends(get_exercise_service),
):
	mg = [MuscleGroup(m) for m in muscle_groups.split(",")] if muscle_groups else None
	eq = [EquipmentType(e) for e in equipment.split(",")] if equipment else None
	results = svc.search(muscle_groups=mg, equipment=eq)
	return {"exercises": [{"id": ex.id, "name": ex.name, "equipment": ex.equipment.value} for ex in results]}

