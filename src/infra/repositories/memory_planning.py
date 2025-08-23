from datetime import date
from typing import Dict, List, Optional

from src.core.models import (
    WorkoutTemplate,
    WorkoutExerciseTemplate,
    TrainingProgram,
    ProgramPhase,
    ProgramEnrollment,
    ScheduledWorkout,
)
from src.core.repositories.protocols import (
    WorkoutTemplateRepository,
    WorkoutExerciseTemplateRepository,
    TrainingProgramRepository,
    ProgramPhaseRepository,
    ProgramEnrollmentRepository,
    ScheduledWorkoutRepository,
)


class InMemoryWorkoutTemplateRepository(WorkoutTemplateRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, WorkoutTemplate] = {}

    def save(self, t: WorkoutTemplate) -> WorkoutTemplate:
        self._by_id[t.id] = t
        return t

    def get_by_id(self, template_id: str) -> Optional[WorkoutTemplate]:
        return self._by_id.get(template_id)

    def list_all(self) -> List[WorkoutTemplate]:
        return list(self._by_id.values())

    def update(self, t: WorkoutTemplate) -> WorkoutTemplate:
        self._by_id[t.id] = t
        return t


class InMemoryWorkoutExerciseTemplateRepository(WorkoutExerciseTemplateRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, WorkoutExerciseTemplate] = {}
        self._by_template: Dict[str, List[WorkoutExerciseTemplate]] = {}

    def save(self, wet: WorkoutExerciseTemplate) -> WorkoutExerciseTemplate:
        self._by_id[wet.id] = wet
        self._by_template.setdefault(wet.workout_template_id, []).append(wet)
        return wet

    def list_by_template(self, template_id: str) -> List[WorkoutExerciseTemplate]:
        return list(self._by_template.get(template_id, []))

    def get_by_id(self, wet_id: str) -> Optional[WorkoutExerciseTemplate]:
        return self._by_id.get(wet_id)

    def update(self, wet: WorkoutExerciseTemplate) -> WorkoutExerciseTemplate:
        self._by_id[wet.id] = wet
        items = self._by_template.get(wet.workout_template_id, [])
        for i, it in enumerate(items):
            if it.id == wet.id:
                items[i] = wet
                break
        return wet


class InMemoryTrainingProgramRepository(TrainingProgramRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, TrainingProgram] = {}

    def save(self, p: TrainingProgram) -> TrainingProgram:
        self._by_id[p.id] = p
        return p

    def get_by_id(self, program_id: str) -> Optional[TrainingProgram]:
        return self._by_id.get(program_id)

    def list_all(self) -> List[TrainingProgram]:
        return list(self._by_id.values())

    def update(self, p: TrainingProgram) -> TrainingProgram:
        self._by_id[p.id] = p
        return p


class InMemoryProgramPhaseRepository(ProgramPhaseRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, ProgramPhase] = {}
        self._by_program: Dict[str, List[ProgramPhase]] = {}

    def save(self, phase: ProgramPhase) -> ProgramPhase:
        self._by_id[phase.id] = phase
        self._by_program.setdefault(phase.program_id, []).append(phase)
        return phase

    def list_by_program(self, program_id: str) -> List[ProgramPhase]:
        return list(self._by_program.get(program_id, []))

    def get_by_id(self, phase_id: str) -> Optional[ProgramPhase]:
        return self._by_id.get(phase_id)

    def update(self, phase: ProgramPhase) -> ProgramPhase:
        self._by_id[phase.id] = phase
        items = self._by_program.get(phase.program_id, [])
        for i, it in enumerate(items):
            if it.id == phase.id:
                items[i] = phase
                break
        return phase


class InMemoryProgramEnrollmentRepository(ProgramEnrollmentRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, ProgramEnrollment] = {}
        self._by_user: Dict[str, List[ProgramEnrollment]] = {}

    def save(self, e: ProgramEnrollment) -> ProgramEnrollment:
        self._by_id[e.id] = e
        self._by_user.setdefault(e.user_id, []).append(e)
        return e

    def get_by_id(self, enrollment_id: str) -> Optional[ProgramEnrollment]:
        return self._by_id.get(enrollment_id)

    def list_by_user(self, user_id: str, active_only: bool = True) -> List[ProgramEnrollment]:
        items = self._by_user.get(user_id, [])
        if not active_only:
            return list(items)
        return [i for i in items if i.is_active]

    def update(self, e: ProgramEnrollment) -> ProgramEnrollment:
        self._by_id[e.id] = e
        items = self._by_user.get(e.user_id, [])
        for i, it in enumerate(items):
            if it.id == e.id:
                items[i] = e
                break
        return e


class InMemoryScheduledWorkoutRepository(ScheduledWorkoutRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, ScheduledWorkout] = {}
        self._by_user: Dict[str, List[ScheduledWorkout]] = {}

    def save(self, s: ScheduledWorkout) -> ScheduledWorkout:
        self._by_id[s.id] = s
        self._by_user.setdefault(s.user_id, []).append(s)
        return s

    def get_by_id(self, scheduled_id: str) -> Optional[ScheduledWorkout]:
        return self._by_id.get(scheduled_id)

    def list_by_user_and_date_range(self, user_id: str, start_date: date, end_date: date) -> List[ScheduledWorkout]:
        items = self._by_user.get(user_id, [])
        return [i for i in items if start_date <= i.scheduled_date <= end_date]

    def update(self, s: ScheduledWorkout) -> ScheduledWorkout:
        self._by_id[s.id] = s
        items = self._by_user.get(s.user_id, [])
        for i, it in enumerate(items):
            if it.id == s.id:
                items[i] = s
                break
        return s


