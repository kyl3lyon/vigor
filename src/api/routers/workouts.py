from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_session_service, get_tracking_service, get_complete_workout_use_case
from src.core.services.workout.session_service import SessionService
from src.core.services.workout.tracking_service import TrackingService
from src.core.use_cases.complete_workout_use_case import CompleteWorkoutUseCase
from src.core.shared.errors import ValidationError, NotFoundError

router = APIRouter()


class StartWorkoutRequest(BaseModel):
	user_id: str
	title: Optional[str] = None
	notes: Optional[str] = None


class AddExerciseRequest(BaseModel):
	exercise_id: str
	order_index: int


class LogSetRequest(BaseModel):
	set_number: int
	weight_kg: Optional[float] = None
	reps: Optional[int] = None
	rpe: Optional[float] = None
	is_failure: bool = False


class CompleteWorkoutRequest(BaseModel):
	session_rpe: Optional[float] = None
	duration_seconds: Optional[int] = None


@router.post("/workouts")
def start_workout(req: StartWorkoutRequest, svc: SessionService = Depends(get_session_service)):
	try:
		w = svc.start_workout(user_id=req.user_id, title=req.title, notes=req.notes)
		return {"workout_id": w.id, "started_at": w.started_at.isoformat() if w.started_at else None}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/workouts/{workout_id}/exercises")
def add_exercise(workout_id: str, req: AddExerciseRequest, svc: SessionService = Depends(get_session_service)):
	try:
		we = svc.add_exercise(workout_id=workout_id, exercise_id=req.exercise_id, order_index=req.order_index)
		return {"workout_exercise_id": we.id, "exercise_id": we.exercise_id}
	except (ValidationError, NotFoundError) as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/workouts/{workout_id}/exercises/{we_id}/sets")
def log_set(workout_id: str, we_id: str, req: LogSetRequest, svc: TrackingService = Depends(get_tracking_service)):
	try:
		s = svc.log_set(
			workout_exercise_id=we_id,
			set_number=req.set_number,
			weight_kg=req.weight_kg,
			reps=req.reps,
			rpe=req.rpe,
			is_failure=req.is_failure,
		)
		return {"set_id": s.id, "set_number": s.set_number}
	except (ValidationError, NotFoundError) as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/workouts/{workout_id}/complete")
def complete_workout(workout_id: str, req: CompleteWorkoutRequest, uc: CompleteWorkoutUseCase = Depends(get_complete_workout_use_case)):
	try:
		result = uc.execute(workout_id=workout_id, session_rpe=req.session_rpe, duration_seconds=req.duration_seconds)
		return {
			"workout_id": result.workout.id,
			"completed_at": result.workout.completed_at.isoformat() if result.workout.completed_at else None,
			"total_volume_kg": result.volume_metrics.total_volume_kg,
			"achievements_count": len(result.achievements),
			"prs_detected": len(result.prs_detected),
		}
	except (ValidationError, NotFoundError) as e:
		raise HTTPException(status_code=400, detail=str(e))

