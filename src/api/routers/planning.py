from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_template_service, get_program_service, get_schedule_service
from src.core.services.planning.template_service import TemplateService
from src.core.services.planning.program_service import ProgramService
from src.core.services.planning.schedule_service import ScheduleService
from src.core.shared.errors import ValidationError, NotFoundError

router = APIRouter()


class CreateTemplateRequest(BaseModel):
	name: str
	description: Optional[str] = None
	estimated_duration_minutes: Optional[int] = None


class AddExerciseTemplateRequest(BaseModel):
	exercise_id: str
	order_index: int
	target_sets: Optional[int] = None
	target_reps_min: Optional[int] = None
	target_reps_max: Optional[int] = None
	target_rpe: Optional[float] = None


class CreateProgramRequest(BaseModel):
	name: str
	description: Optional[str] = None
	duration_weeks: Optional[int] = None


class AddPhaseRequest(BaseModel):
	name: str
	order_index: int
	start_week: Optional[int] = None
	end_week: Optional[int] = None
	is_deload: bool = False
	deload_percentage: Optional[float] = None


class EnrollRequest(BaseModel):
	user_id: str
	start_date: date


class ScheduleWorkoutRequest(BaseModel):
	user_id: str
	scheduled_date: date
	template_id: Optional[str] = None
	program_enrollment_id: Optional[str] = None
	program_phase_id: Optional[str] = None
	priority: int = 3


@router.post("/templates")
def create_template(req: CreateTemplateRequest, svc: TemplateService = Depends(get_template_service)):
	try:
		t = svc.create_template(name=req.name, description=req.description, estimated_duration_minutes=req.estimated_duration_minutes)
		return {"template_id": t.id, "name": t.name}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates")
def list_templates(svc: TemplateService = Depends(get_template_service)):
	templates = svc.list_templates()
	return {"templates": [{"id": t.id, "name": t.name} for t in templates]}


@router.post("/templates/{template_id}/exercises")
def add_exercise_template(template_id: str, req: AddExerciseTemplateRequest, svc: TemplateService = Depends(get_template_service)):
	try:
		wet = svc.add_exercise_template(
			workout_template_id=template_id,
			exercise_id=req.exercise_id,
			order_index=req.order_index,
			target_sets=req.target_sets,
			target_reps_min=req.target_reps_min,
			target_reps_max=req.target_reps_max,
			target_rpe=req.target_rpe,
		)
		return {"wet_id": wet.id, "exercise_id": wet.exercise_id}
	except (ValidationError, NotFoundError) as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/programs")
def create_program(req: CreateProgramRequest, svc: ProgramService = Depends(get_program_service)):
	try:
		p = svc.create_program(name=req.name, description=req.description, duration_weeks=req.duration_weeks)
		return {"program_id": p.id, "name": p.name}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/programs/{program_id}/phases")
def add_phase(program_id: str, req: AddPhaseRequest, svc: ProgramService = Depends(get_program_service)):
	try:
		phase = svc.add_phase(
			program_id=program_id,
			name=req.name,
			order_index=req.order_index,
			start_week=req.start_week,
			end_week=req.end_week,
			is_deload=req.is_deload,
			deload_percentage=req.deload_percentage,
		)
		return {"phase_id": phase.id, "name": phase.name}
	except (ValidationError, NotFoundError) as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/programs/{program_id}/enroll")
def enroll(program_id: str, req: EnrollRequest, svc: ProgramService = Depends(get_program_service)):
	try:
		e = svc.enroll(user_id=req.user_id, program_id=program_id, start_date=req.start_date)
		return {"enrollment_id": e.id}
	except (ValidationError, NotFoundError) as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/schedule")
def schedule_workout(req: ScheduleWorkoutRequest, svc: ScheduleService = Depends(get_schedule_service)):
	try:
		s = svc.schedule_workout(
			user_id=req.user_id,
			scheduled_date=req.scheduled_date,
			template_id=req.template_id,
			program_enrollment_id=req.program_enrollment_id,
			program_phase_id=req.program_phase_id,
			priority=req.priority,
		)
		return {"scheduled_id": s.id, "date": s.scheduled_date.isoformat()}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}/schedule")
def list_schedule(user_id: str, start_date: date, end_date: date, svc: ScheduleService = Depends(get_schedule_service)):
	items = svc.list_for_user(user_id, start_date, end_date)
	return {"scheduled": [{"id": s.id, "date": s.scheduled_date.isoformat(), "template_id": s.template_id} for s in items]}


@router.patch("/schedule/{scheduled_id}/reschedule")
def reschedule(scheduled_id: str, new_date: date, svc: ScheduleService = Depends(get_schedule_service)):
	try:
		s = svc.reschedule(scheduled_id, new_date)
		return {"scheduled_id": s.id, "new_date": s.scheduled_date.isoformat(), "reschedule_count": s.reschedule_count}
	except NotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))


@router.patch("/schedule/{scheduled_id}/complete")
def mark_complete(scheduled_id: str, actual_workout_id: str, svc: ScheduleService = Depends(get_schedule_service)):
	try:
		s = svc.mark_completed(scheduled_id, actual_workout_id)
		return {"scheduled_id": s.id, "actual_workout_id": s.actual_workout_id}
	except NotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))

