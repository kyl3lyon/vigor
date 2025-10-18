from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.dependencies import get_metrics_service, get_insight_service
from src.core.services.analytics.metrics_service import MetricsService
from src.core.services.analytics.insight_service import InsightService

router = APIRouter()


@router.get("/users/{user_id}/analytics/volume")
def get_volume(user_id: str, period_days: int = 28, svc: MetricsService = Depends(get_metrics_service)):
	vm = svc.get_volume_metrics(user_id, period_days)
	return {
		"total_volume_kg": vm.total_volume_kg,
		"volume_by_muscle": {k.value: v for k, v in vm.volume_by_muscle_group.items()},
		"volume_by_movement": {k.value: v for k, v in vm.volume_by_movement_pattern.items()},
		"trend": vm.weekly_volume_trend.value,
	}


@router.get("/users/{user_id}/analytics/strength/{exercise_id}")
def get_strength(user_id: str, exercise_id: str, period_days: int = 84, svc: MetricsService = Depends(get_metrics_service)):
	sp = svc.get_exercise_strength_progress(user_id, exercise_id, period_days)
	return {
		"estimated_1rm_kg": sp.estimated_1rm_kg,
		"velocity_kg_per_week": sp.strength_velocity_kg_per_week,
	}


@router.get("/users/{user_id}/analytics/achievements")
def get_achievements(user_id: str, period_days: int = 365, svc: InsightService = Depends(get_insight_service)):
	ach = svc.detect_achievements(user_id, period_days)
	return {"achievements": [{"id": a.id, "title": a.title, "description": a.description, "points": a.points} for a in ach]}


@router.get("/users/{user_id}/analytics/balance")
def get_balance(user_id: str, period_days: int = 28, svc: InsightService = Depends(get_insight_service)):
	warnings = svc.find_balance_warnings(user_id, period_days)
	return {"warnings": warnings}

