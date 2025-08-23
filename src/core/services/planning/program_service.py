from typing import List, Optional

from src.core.models import TrainingProgram, ProgramPhase, ProgramEnrollment
from src.core.repositories.protocols import (
    TrainingProgramRepository,
    ProgramPhaseRepository,
    ProgramEnrollmentRepository,
)
from src.core.shared.errors import ValidationError, NotFoundError


class ProgramService:
    def __init__(
        self,
        p_repo: TrainingProgramRepository,
        phase_repo: ProgramPhaseRepository,
        enroll_repo: ProgramEnrollmentRepository,
    ) -> None:
        self._p = p_repo
        self._phase = phase_repo
        self._enroll = enroll_repo

    # Programs
    def create_program(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        duration_weeks: Optional[int] = None,
    ) -> TrainingProgram:
        if not name:
            raise ValidationError("name: required")
        if duration_weeks is not None and duration_weeks <= 0:
            raise ValidationError("duration_weeks: must be > 0")
        prog = TrainingProgram(name=name, description=description, duration_weeks=duration_weeks)
        return self._p.save(prog)

    def get_program(self, program_id: str) -> TrainingProgram:
        prog = self._p.get_by_id(program_id)
        if prog is None:
            raise NotFoundError("program: not found")
        return prog

    def list_programs(self) -> List[TrainingProgram]:
        return self._p.list_all()

    # Phases
    def add_phase(
        self,
        *,
        program_id: str,
        name: str,
        order_index: int,
        start_week: Optional[int] = None,
        end_week: Optional[int] = None,
        is_deload: bool = False,
        deload_percentage: Optional[float] = None,
    ) -> ProgramPhase:
        self.get_program(program_id)
        if order_index < 0:
            raise ValidationError("order_index: must be >= 0")
        phases = self._phase.list_by_program(program_id)
        if any(ph.order_index == order_index for ph in phases):
            raise ValidationError("order_index: duplicate within program")
        if start_week is not None and start_week <= 0:
            raise ValidationError("start_week: must be > 0")
        if end_week is not None and end_week <= 0:
            raise ValidationError("end_week: must be > 0")
        if start_week is not None and end_week is not None and start_week > end_week:
            raise ValidationError("start_week must be <= end_week")
        if is_deload and deload_percentage is not None and (deload_percentage <= 0 or deload_percentage > 1):
            raise ValidationError("deload_percentage: must be (0,1]")

        phase = ProgramPhase(
            program_id=program_id,
            name=name,
            order_index=order_index,
            start_week=start_week,
            end_week=end_week,
            is_deload=is_deload,
            deload_percentage=deload_percentage,
        )
        return self._phase.save(phase)

    def list_phases(self, program_id: str) -> List[ProgramPhase]:
        items = self._phase.list_by_program(program_id)
        return sorted(items, key=lambda x: x.order_index)

    # Enrollment
    def enroll(
        self,
        *,
        user_id: str,
        program_id: str,
        start_date: 'date',
    ) -> ProgramEnrollment:
        self.get_program(program_id)
        e = ProgramEnrollment(user_id=user_id, program_id=program_id, start_date=start_date)
        return self._enroll.save(e)

    def get_enrollment(self, enrollment_id: str) -> ProgramEnrollment:
        e = self._enroll.get_by_id(enrollment_id)
        if e is None:
            raise NotFoundError("enrollment: not found")
        return e

    def list_enrollments(self, user_id: str, *, active_only: bool = True) -> List[ProgramEnrollment]:
        return self._enroll.list_by_user(user_id, active_only=active_only)

    def update_enrollment_progress(
        self,
        *,
        enrollment_id: str,
        current_phase_id: Optional[str] = None,
        progress_week: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> ProgramEnrollment:
        e = self.get_enrollment(enrollment_id)
        if progress_week is not None and progress_week < 0:
            raise ValidationError("progress_week: must be >= 0")
        updated = ProgramEnrollment(
            id=e.id,
            user_id=e.user_id,
            program_id=e.program_id,
            start_date=e.start_date,
            current_phase_id=e.current_phase_id if current_phase_id is None else current_phase_id,
            progress_week=e.progress_week if progress_week is None else progress_week,
            is_active=e.is_active if is_active is None else is_active,
            notes=e.notes,
            ended_at=e.ended_at,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        return self._enroll.update(updated)


