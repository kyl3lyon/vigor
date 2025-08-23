from dataclasses import replace
from typing import List, Optional

from src.core.models import WorkoutTemplate, WorkoutExerciseTemplate
from src.core.repositories.protocols import WorkoutTemplateRepository, WorkoutExerciseTemplateRepository
from src.core.shared.errors import ValidationError, NotFoundError


class TemplateService:
    def __init__(self, t_repo: WorkoutTemplateRepository, wet_repo: WorkoutExerciseTemplateRepository) -> None:
        self._t = t_repo
        self._wet = wet_repo

    # Templates
    def create_template(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        estimated_duration_minutes: Optional[int] = None,
    ) -> WorkoutTemplate:
        if not name:
            raise ValidationError("name: required")
        if estimated_duration_minutes is not None and estimated_duration_minutes < 0:
            raise ValidationError("estimated_duration_minutes: must be >= 0")
        t = WorkoutTemplate(name=name, description=description, estimated_duration_minutes=estimated_duration_minutes)
        return self._t.save(t)

    def get_template(self, template_id: str) -> WorkoutTemplate:
        t = self._t.get_by_id(template_id)
        if t is None:
            raise NotFoundError("template: not found")
        return t

    def list_templates(self) -> List[WorkoutTemplate]:
        return self._t.list_all()

    # Exercise templates
    def add_exercise_template(
        self,
        *,
        workout_template_id: str,
        exercise_id: str,
        order_index: int,
        target_sets: Optional[int] = None,
        target_reps_min: Optional[int] = None,
        target_reps_max: Optional[int] = None,
        target_rpe: Optional[float] = None,
        target_intensity_pct_1rm: Optional[float] = None,
        rest_seconds_between_sets: Optional[int] = None,
        tempo: Optional[str] = None,
        notes: Optional[str] = None,
        superset_group_id: Optional[str] = None,
    ) -> WorkoutExerciseTemplate:
        t = self.get_template(workout_template_id)
        if order_index < 0:
            raise ValidationError("order_index: must be >= 0")
        existing = self._wet.list_by_template(workout_template_id)
        if any(it.order_index == order_index for it in existing):
            raise ValidationError("order_index: duplicate within template")
        if target_sets is not None and target_sets <= 0:
            raise ValidationError("target_sets: must be > 0 when provided")
        if (target_reps_min is not None and target_reps_min <= 0) or (
            target_reps_max is not None and target_reps_max <= 0
        ):
            raise ValidationError("target_reps: must be > 0 when provided")
        if target_reps_min is not None and target_reps_max is not None and target_reps_min > target_reps_max:
            raise ValidationError("target_reps_min must be <= target_reps_max")
        if target_rpe is not None and (target_rpe < 1.0 or target_rpe > 10.0):
            raise ValidationError("target_rpe: must be 1.0..10.0")
        if target_intensity_pct_1rm is not None and (target_intensity_pct_1rm <= 0 or target_intensity_pct_1rm > 1):
            raise ValidationError("target_intensity_pct_1rm: must be (0,1]")
        if rest_seconds_between_sets is not None and rest_seconds_between_sets < 0:
            raise ValidationError("rest_seconds_between_sets: must be >= 0")

        wet = WorkoutExerciseTemplate(
            workout_template_id=workout_template_id,
            exercise_id=exercise_id,
            order_index=order_index,
            target_sets=target_sets,
            target_reps_min=target_reps_min,
            target_reps_max=target_reps_max,
            target_rpe=target_rpe,
            target_intensity_pct_1rm=target_intensity_pct_1rm,
            rest_seconds_between_sets=rest_seconds_between_sets,
            tempo=tempo,
            notes=notes,
            superset_group_id=superset_group_id,
        )
        return self._wet.save(wet)

    def list_exercise_templates(self, template_id: str) -> List[WorkoutExerciseTemplate]:
        # also ensure stable order by order_index
        items = self._wet.list_by_template(template_id)
        return sorted(items, key=lambda x: x.order_index)


