from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from src.core.services.workout.session_service import SessionService
from src.core.services.workout.tracking_service import TrackingService
from src.core.services.analytics.metrics_service import MetricsService
from src.core.services.analytics.insight_service import InsightService
from src.core.models import Workout, PersonalRecord
from src.core.models.analytics import VolumeMetrics, Achievement
from src.core.repositories.protocols import WorkoutExerciseRepository, ExerciseSetRepository


@dataclass
class CompleteWorkoutResult:
	workout: Workout
	volume_metrics: VolumeMetrics
	achievements: List[Achievement]
	prs_detected: List[PersonalRecord]


@dataclass
class CompleteWorkoutUseCase:
	session_service: SessionService
	tracking_service: TrackingService
	metrics_service: MetricsService
	insight_service: InsightService
	we_repo: WorkoutExerciseRepository
	set_repo: ExerciseSetRepository

	def execute(
		self,
		workout_id: str,
		*,
		session_rpe: Optional[float] = None,
		duration_seconds: Optional[int] = None,
	) -> CompleteWorkoutResult:
		workout = self.session_service.complete_workout(
			workout_id, session_rpe=session_rpe, duration_seconds=duration_seconds
		)
		
		# Evaluate PRs for all exercises in this workout
		prs: List[PersonalRecord] = []
		wes = self.we_repo.list_by_workout(workout_id)
		for we in wes:
			sets = self.set_repo.list_for_workout_exercise(we.id)
			# Find top set by estimated 1RM for this exercise
			top_weight, top_reps = None, None
			for s in sets:
				if s.weight_kg is not None and s.reps is not None:
					if top_weight is None or s.weight_kg > top_weight:
						top_weight, top_reps = s.weight_kg, s.reps
			if top_weight and top_reps:
				pr = self.tracking_service.evaluate_prs(
					user_id=workout.user_id,
					exercise_id=we.exercise_id,
					weight_kg=top_weight,
					reps=top_reps,
					achieved_at=workout.completed_at or datetime.now(),
				)
				if pr:
					prs.append(pr)
		
		metrics = self.metrics_service.get_volume_metrics(user_id=workout.user_id, period_days=28)
		achievements = self.insight_service.detect_achievements(user_id=workout.user_id, period_days=365)
		return CompleteWorkoutResult(workout=workout, volume_metrics=metrics, achievements=achievements, prs_detected=prs)

