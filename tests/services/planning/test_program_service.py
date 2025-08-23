from datetime import date

from src.infra.repositories.memory_planning import (
	 InMemoryTrainingProgramRepository,
	 InMemoryProgramPhaseRepository,
	 InMemoryProgramEnrollmentRepository,
)
from src.core.services.planning.program_service import ProgramService
from src.core.shared.errors import ValidationError


def test_program_create_add_phases_and_enroll():
	 p_repo = InMemoryTrainingProgramRepository()
	 phase_repo = InMemoryProgramPhaseRepository()
	 enroll_repo = InMemoryProgramEnrollmentRepository()
	 svc = ProgramService(p_repo, phase_repo, enroll_repo)
	 prog = svc.create_program(name="Push/Pull", duration_weeks=6)
	 assert p_repo.get_by_id(prog.id) is not None
	 # invalid duration
	 try:
		 svc.create_program(name="X", duration_weeks=0)
		 assert False, "expected ValidationError"
	 except ValidationError:
		 pass
	 # add phases
	 base = svc.add_phase(program_id=prog.id, name="Base", order_index=0, start_week=1, end_week=4)
	 try:
		 svc.add_phase(program_id=prog.id, name="Dup", order_index=0)
		 assert False, "expected ValidationError for duplicate order"
	 except ValidationError:
		 pass
	 deload = svc.add_phase(program_id=prog.id, name="Deload", order_index=1, is_deload=True, deload_percentage=0.6)
	 phases = svc.list_phases(prog.id)
	 assert [p.name for p in phases] == ["Base", "Deload"]
	 # enroll
	 e = svc.enroll(user_id="u1", program_id=prog.id, start_date=date.today())
	 es = svc.list_enrollments("u1")
	 assert len(es) == 1 and es[0].id == e.id
	 # update progress
	 e2 = svc.update_enrollment_progress(enrollment_id=e.id, progress_week=2)
	 assert e2.progress_week == 2


