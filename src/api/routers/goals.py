from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_goal_service
from src.core.services.user.goal_service import GoalService
from src.core.models import GoalCategory
from src.core.shared.errors import ValidationError, NotFoundError

router = APIRouter()


class CreateGoalRequest(BaseModel):
	goal_category: GoalCategory
	goal_type: str
	priority_level: int
	description: Optional[str] = None
	target_value: Optional[float] = None
	target_date: Optional[datetime] = None


class UpdateProgressRequest(BaseModel):
	current_value: Optional[float] = None
	progress_percentage: Optional[float] = None
	is_achieved: Optional[bool] = None
	achieved_at: Optional[datetime] = None


@router.post("/users/{user_id}/goals")
def create_goal(user_id: str, req: CreateGoalRequest, svc: GoalService = Depends(get_goal_service)):
	try:
		goal = svc.create_goal(
			user_id=user_id,
			goal_category=req.goal_category,
			goal_type=req.goal_type,
			priority_level=req.priority_level,
			description=req.description,
			target_value=req.target_value,
			target_date=req.target_date,
		)
		return {"goal_id": goal.id, "goal_type": goal.goal_type, "priority": goal.priority_level}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}/goals")
def list_goals(user_id: str, active_only: bool = True, svc: GoalService = Depends(get_goal_service)):
	goals = svc.list_goals(user_id, active_only=active_only)
	return {"goals": [{"id": g.id, "type": g.goal_type, "priority": g.priority_level, "progress": g.progress_percentage} for g in goals]}


@router.patch("/goals/{goal_id}/progress")
def update_progress(goal_id: str, req: UpdateProgressRequest, svc: GoalService = Depends(get_goal_service)):
	try:
		goal = svc.update_progress(
			goal_id,
			current_value=req.current_value,
			progress_percentage=req.progress_percentage,
			is_achieved=req.is_achieved,
			achieved_at=req.achieved_at,
		)
		return {"goal_id": goal.id, "progress": goal.progress_percentage, "is_achieved": goal.is_achieved}
	except (ValidationError, NotFoundError) as e:
		raise HTTPException(status_code=400, detail=str(e))

