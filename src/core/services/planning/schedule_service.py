from datetime import date
from typing import List, Optional

from src.core.models import ScheduledWorkout
from src.core.repositories.protocols import ScheduledWorkoutRepository
from src.core.shared.errors import ValidationError, NotFoundError


class ScheduleService:
    def __init__(self, repo: ScheduledWorkoutRepository) -> None:
        self._s = repo

    def schedule_workout(
        self,
        *,
        user_id: str,
        scheduled_date: date,
        template_id: Optional[str] = None,
        program_enrollment_id: Optional[str] = None,
        program_phase_id: Optional[str] = None,
        priority: int = 3,
    ) -> ScheduledWorkout:
        if not user_id:
            raise ValidationError("user_id: required")
        if priority < 1 or priority > 5:
            raise ValidationError("priority: must be 1..5")
        s = ScheduledWorkout(
            user_id=user_id,
            scheduled_date=scheduled_date,
            template_id=template_id,
            program_enrollment_id=program_enrollment_id,
            program_phase_id=program_phase_id,
            priority=priority,
        )
        return self._s.save(s)

    def get(self, scheduled_id: str) -> ScheduledWorkout:
        s = self._s.get_by_id(scheduled_id)
        if s is None:
            raise NotFoundError("scheduled_workout: not found")
        return s

    def list_for_user(self, user_id: str, start_date: date, end_date: date) -> List[ScheduledWorkout]:
        return self._s.list_by_user_and_date_range(user_id, start_date, end_date)

    def reschedule(self, scheduled_id: str, new_date: date) -> ScheduledWorkout:
        s = self.get(scheduled_id)
        updated = ScheduledWorkout(
            id=s.id,
            user_id=s.user_id,
            scheduled_date=new_date,
            template_id=s.template_id,
            program_enrollment_id=s.program_enrollment_id,
            program_phase_id=s.program_phase_id,
            actual_workout_id=s.actual_workout_id,
            status=s.status,
            priority=s.priority,
            notes=s.notes,
            auto_generated=s.auto_generated,
            reschedule_count=s.reschedule_count + 1,
            recurrence=s.recurrence,
            recurrence_pattern=s.recurrence_pattern,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        return self._s.update(updated)

    def mark_completed(self, scheduled_id: str, actual_workout_id: str) -> ScheduledWorkout:
        s = self.get(scheduled_id)
        updated = ScheduledWorkout(
            id=s.id,
            user_id=s.user_id,
            scheduled_date=s.scheduled_date,
            template_id=s.template_id,
            program_enrollment_id=s.program_enrollment_id,
            program_phase_id=s.program_phase_id,
            actual_workout_id=actual_workout_id,
            status=s.status,
            priority=s.priority,
            notes=s.notes,
            auto_generated=s.auto_generated,
            reschedule_count=s.reschedule_count,
            recurrence=s.recurrence,
            recurrence_pattern=s.recurrence_pattern,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        return self._s.update(updated)


