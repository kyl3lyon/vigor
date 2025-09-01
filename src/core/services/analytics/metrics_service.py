from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from src.core.models import Workout, WorkoutExercise, ExerciseSet, ExerciseDefinition
from src.core.models.analytics import VolumeMetrics, StrengthAnalysis, TrendDirection
from src.core.repositories.protocols import (
    WorkoutRepository,
    WorkoutExerciseRepository,
    ExerciseSetRepository,
    ExerciseDefinitionRepository,
)
from src.core.domain_logic.strength_estimators import blended_1rm_estimate


class MetricsService:
    def __init__(
        self,
        workout_repo: WorkoutRepository,
        we_repo: WorkoutExerciseRepository,
        set_repo: ExerciseSetRepository,
        ex_repo: ExerciseDefinitionRepository,
    ) -> None:
        self._workouts = workout_repo
        self._wes = we_repo
        self._sets = set_repo
        self._ex = ex_repo

    def get_volume_metrics(self, user_id: str, period_days: int = 28) -> VolumeMetrics:
        end = datetime.now()
        start = end - timedelta(days=period_days)
        workouts = [w for w in self._workouts.list_by_user_recent(user_id, limit=1000) if w.started_at and start <= w.started_at <= end]
        we_map: Dict[str, WorkoutExercise] = {}
        ex_map: Dict[str, ExerciseDefinition] = {}
        total = 0.0
        by_mg: Dict = {}
        by_mp: Dict = {}
        # weekly buckets by ISO week
        weekly: Dict[Tuple[int, int], float] = {}

        for w in workouts:
            wes = self._wes.list_by_workout(w.id)
            for we in wes:
                we_map[we.id] = we
                if we.exercise_id not in ex_map:
                    ex = self._ex.get_by_id(we.exercise_id)
                    if ex is None:
                        continue
                    ex_map[we.exercise_id] = ex
                sets = self._sets.list_for_workout_exercise(we.id)
                for s in sets:
                    if s.weight_kg is None or s.reps is None:
                        continue
                    vol = s.weight_kg * float(s.reps)
                    total += vol
                    # muscle groups
                    for mg in ex_map[we.exercise_id].primary_muscles:
                        by_mg[mg] = by_mg.get(mg, 0.0) + vol
                    # movement pattern
                    mp = ex_map[we.exercise_id].movement_pattern
                    by_mp[mp] = by_mp.get(mp, 0.0) + vol
                    # weekly bucket
                    if w.started_at:
                        key = w.started_at.isocalendar()[:2]  # (year, week)
                        weekly[key] = weekly.get(key, 0.0) + vol

        # trend: compare last two buckets if present
        trend = TrendDirection.STABLE
        if len(weekly) >= 2:
            keys = sorted(weekly.keys())
            if weekly[keys[-1]] > weekly[keys[-2]]:
                trend = TrendDirection.INCREASING
            elif weekly[keys[-1]] < weekly[keys[-2]]:
                trend = TrendDirection.DECREASING

        return VolumeMetrics(
            user_id=user_id,
            analysis_period_days=period_days,
            total_volume_kg=total,
            volume_by_muscle_group=by_mg,
            volume_by_movement_pattern=by_mp,
            weekly_volume_trend=trend,
        )

    def get_exercise_strength_progress(self, user_id: str, exercise_id: str, period_days: int = 84) -> StrengthAnalysis:
        end = datetime.now()
        start = end - timedelta(days=period_days)
        workouts = [w for w in self._workouts.list_by_user_recent(user_id, limit=1000) if w.started_at and start <= w.started_at <= end]
        # For each workout, pick the top set (highest estimated 1RM) for the exercise
        series: List[Tuple[datetime, float]] = []
        for w in workouts:
            top_est = None
            wes = self._wes.list_by_workout(w.id)
            for we in wes:
                if we.exercise_id != exercise_id:
                    continue
                sets = self._sets.list_for_workout_exercise(we.id)
                for s in sets:
                    if s.weight_kg is None or s.reps is None:
                        continue
                    est = blended_1rm_estimate(s.weight_kg, s.reps)
                    if est is None:
                        continue
                    if top_est is None or est > top_est:
                        top_est = est
            if top_est is not None and w.started_at is not None:
                series.append((w.started_at, top_est))

        series.sort(key=lambda x: x[0])
        # simple velocity estimate: (last - first) / weeks
        velocity = 0.0
        estimated = series[-1][1] if series else 0.0
        if len(series) >= 2:
            delta = series[-1][1] - series[0][1]
            days = max(1, (series[-1][0] - series[0][0]).days)
            velocity = delta / (days / 7.0)

        return StrengthAnalysis(
            user_id=user_id,
            exercise_id=exercise_id,
            estimated_1rm_kg=estimated,
            strength_velocity_kg_per_week=velocity,
        )



