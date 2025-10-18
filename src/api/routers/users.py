from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_user_service, get_profile_service
from src.core.services.user.user_service import UserService
from src.core.services.user.profile_service import ProfileService
from src.core.models import Gender, ActivityLevel, ExperienceLevel, UnitSystem, TrainingSplit
from src.core.shared.errors import ValidationError, ConflictError, NotFoundError

router = APIRouter()


class CreateUserRequest(BaseModel):
	email: str
	username: str
	timezone: str = "UTC"
	preferred_language: str = "en"


class UpsertProfileRequest(BaseModel):
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	height_cm: Optional[float] = None
	current_weight_kg: Optional[float] = None
	date_of_birth: Optional[date] = None
	gender: Optional[Gender] = None
	activity_level: Optional[ActivityLevel] = None
	experience_level: Optional[ExperienceLevel] = None


class UpsertPreferencesRequest(BaseModel):
	preferred_units: Optional[UnitSystem] = None
	preferred_split: Optional[TrainingSplit] = None
	sessions_per_week: Optional[int] = None
	session_duration_preference_minutes: Optional[int] = None
	workout_reminders: Optional[bool] = None
	workout_reminder_time: Optional[str] = None
	rest_day_preferences: Optional[List[str]] = None
	gym_location: Optional[str] = None
	available_equipment: Optional[List[str]] = None
	exercise_dislikes: Optional[List[str]] = None
	exercise_restrictions: Optional[List[str]] = None
	injury_notes: Optional[str] = None
	progress_updates: Optional[bool] = None
	achievement_notifications: Optional[bool] = None


@router.post("/users")
def create_user(req: CreateUserRequest, svc: UserService = Depends(get_user_service)):
	try:
		user = svc.create_user(email=req.email, username=req.username, timezone=req.timezone, preferred_language=req.preferred_language)
		return {"user_id": user.id, "email": user.email, "username": user.username}
	except (ValidationError, ConflictError) as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}")
def get_user(user_id: str, svc: UserService = Depends(get_user_service)):
	try:
		user = svc._require_user(user_id)
		return {"user_id": user.id, "email": user.email, "username": user.username, "is_active": user.is_active}
	except NotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))


@router.post("/users/{user_id}/profile")
def upsert_profile(user_id: str, req: UpsertProfileRequest, svc: ProfileService = Depends(get_profile_service)):
	try:
		profile = svc.upsert_profile(
			user_id=user_id,
			first_name=req.first_name,
			last_name=req.last_name,
			height_cm=req.height_cm,
			current_weight_kg=req.current_weight_kg,
			date_of_birth=req.date_of_birth,
			gender=req.gender,
			activity_level=req.activity_level,
			experience_level=req.experience_level,
		)
		return {"user_id": profile.user_id, "height_cm": profile.height_cm, "weight_kg": profile.current_weight_kg}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/preferences")
def upsert_preferences(user_id: str, req: UpsertPreferencesRequest, svc: ProfileService = Depends(get_profile_service)):
	try:
		prefs = svc.upsert_preferences(
			user_id=user_id,
			preferred_units=req.preferred_units,
			preferred_split=req.preferred_split,
			sessions_per_week=req.sessions_per_week,
			session_duration_preference_minutes=req.session_duration_preference_minutes,
			workout_reminders=req.workout_reminders,
			workout_reminder_time=req.workout_reminder_time,
			rest_day_preferences=req.rest_day_preferences,
			gym_location=req.gym_location,
			available_equipment=req.available_equipment,
			exercise_dislikes=req.exercise_dislikes,
			exercise_restrictions=req.exercise_restrictions,
			injury_notes=req.injury_notes,
			progress_updates=req.progress_updates,
			achievement_notifications=req.achievement_notifications,
		)
		return {"user_id": prefs.user_id, "sessions_per_week": prefs.sessions_per_week, "preferred_split": getattr(prefs.preferred_split, "value", None)}
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))

