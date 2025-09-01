from datetime import datetime, timedelta
from typing import Dict, List

from src.core.models import Workout, WorkoutExercise, ExerciseSet, ExerciseDefinition
from src.core.models.analytics import Achievement
from src.core.repositories.protocols import (
    WorkoutRepository,
    WorkoutExerciseRepository,
    ExerciseSetRepository,
    ExerciseDefinitionRepository,
    PersonalRecordRepository,
)
from src.core.domain_logic.strength_estimators import blended_1rm_estimate


class InsightService:
    def __init__(
        self,
        workout_repo: WorkoutRepository,
        we_repo: WorkoutExerciseRepository,
        set_repo: ExerciseSetRepository,
        ex_repo: ExerciseDefinitionRepository,
        pr_repo: PersonalRecordRepository,
    ) -> None:
        self._workouts = workout_repo
        self._wes = we_repo
        self._sets = set_repo
        self._ex = ex_repo
        self._prs = pr_repo

    def detect_achievements(self, user_id: str, period_days: int = 365) -> List[Achievement]:
        end = datetime.now()
        start = end - timedelta(days=period_days)
        achievements: List[Achievement] = []
        workouts = [w for w in self._workouts.list_by_user_recent(user_id, limit=1000) if w.started_at and start <= w.started_at <= end]
        seen_exercises: Dict[str, float] = {}
        for w in workouts:
            wes = self._wes.list_by_workout(w.id)
            for we in wes:
                sets = self._sets.list_for_workout_exercise(we.id)
                top = None
                for s in sets:
                    if s.weight_kg is None or s.reps is None:
                        continue
                    est = blended_1rm_estimate(s.weight_kg, s.reps)
                    if est is None:
                        continue
                    if top is None or est > top:
                        top = est
                if top is None:
                    continue
                best = self._prs.get_best_one_rm(user_id, we.exercise_id)
                prior = best.weight_kg if best and best.weight_kg is not None else 0.0
                if top > prior and top > seen_exercises.get(we.exercise_id, 0.0):
                    achievements.append(
                        Achievement(
                            user_id=user_id,
                            achievement_type="strength_pr",
                            title="New PR",
                            description=f"Estimated 1RM improved to {top:.1f} kg",
                            points=50,
                            unlocked_at=w.started_at or end,
                            related_pr_id=None,
                            related_workout_id=w.id,
                        )
                    )
                    seen_exercises[we.exercise_id] = top
        return achievements

    def find_balance_warnings(self, user_id: str, period_days: int = 28) -> List[Dict[str, str]]:
        end = datetime.now()
        start = end - timedelta(days=period_days)
        workouts = [w for w in self._workouts.list_by_user_recent(user_id, limit=1000) if w.started_at and start <= w.started_at <= end]
        by_mp: Dict[str, float] = {}
        for w in workouts:
            wes = self._wes.list_by_workout(w.id)
            for we in wes:
                ex = self._ex.get_by_id(we.exercise_id)
                if ex is None:
                    continue
                sets = self._sets.list_for_workout_exercise(we.id)
                for s in sets:
                    if s.weight_kg is None or s.reps is None:
                        continue
                    vol = s.weight_kg * float(s.reps)
                    key = ex.movement_pattern.value
                    by_mp[key] = by_mp.get(key, 0.0) + vol
        warnings: List[Dict[str, str]] = []
        # Example: push vs pull
        push = by_mp.get("horizontal_press", 0.0) + by_mp.get("vertical_press", 0.0)
        pull = by_mp.get("horizontal_pull", 0.0) + by_mp.get("vertical_pull", 0.0)
        if push > 0 and pull > 0:
            ratio = push / max(1e-6, pull)
            if ratio > 1.5 or ratio < 0.67:
                warnings.append({
                    "type": "balance_warning",
                    "dimension": "push_pull",
                    "detail": f"push:pull ratio={ratio:.2f}",
                })
        return warnings


