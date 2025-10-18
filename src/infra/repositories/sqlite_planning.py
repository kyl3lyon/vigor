import sqlite3
import json
from datetime import datetime, date
from typing import Optional, List

from src.core.models import (
	WorkoutTemplate,
	WorkoutExerciseTemplate,
	TrainingProgram,
	ProgramPhase,
	ProgramEnrollment,
	ScheduledWorkout,
	DifficultyLevel,
	TemplateGoal,
	AutoregulationStrategy,
	ScheduleStatus,
	ScheduleRecurrence,
)
from src.core.repositories.protocols import (
	WorkoutTemplateRepository,
	WorkoutExerciseTemplateRepository,
	TrainingProgramRepository,
	ProgramPhaseRepository,
	ProgramEnrollmentRepository,
	ScheduledWorkoutRepository,
)


class SQLiteWorkoutTemplateRepository(WorkoutTemplateRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, t: WorkoutTemplate) -> WorkoutTemplate:
		self._conn.execute(
			"""INSERT INTO workout_templates (id, name, description, estimated_duration_minutes, difficulty_level, goal, target_muscle_groups, target_movement_patterns, exercise_templates, author_user_id, is_public, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				t.id,
				t.name,
				t.description,
				t.estimated_duration_minutes,
				t.difficulty_level.value,
				t.goal.value,
				json.dumps([m.value for m in t.target_muscle_groups]),
				json.dumps([m.value for m in t.target_movement_patterns]),
				json.dumps(t.exercise_templates),
				t.author_user_id,
				1 if t.is_public else 0,
				t.created_at.isoformat(),
				t.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return t

	def get_by_id(self, template_id: str) -> Optional[WorkoutTemplate]:
		row = self._conn.execute("SELECT * FROM workout_templates WHERE id = ?", (template_id,)).fetchone()
		return self._row_to_template(row) if row else None

	def list_all(self) -> List[WorkoutTemplate]:
		rows = self._conn.execute("SELECT * FROM workout_templates").fetchall()
		return [self._row_to_template(r) for r in rows]

	def update(self, t: WorkoutTemplate) -> WorkoutTemplate:
		self._conn.execute(
			"""UPDATE workout_templates SET name = ?, description = ?, estimated_duration_minutes = ?, difficulty_level = ?, goal = ?, updated_at = ?
			   WHERE id = ?""",
			(
				t.name,
				t.description,
				t.estimated_duration_minutes,
				t.difficulty_level.value,
				t.goal.value,
				t.updated_at.isoformat(),
				t.id,
			),
		)
		self._conn.commit()
		return t

	def _row_to_template(self, row: sqlite3.Row) -> WorkoutTemplate:
		from src.core.models import MuscleGroup, MovementPattern
		return WorkoutTemplate(
			id=row["id"],
			name=row["name"],
			description=row["description"],
			estimated_duration_minutes=row["estimated_duration_minutes"],
			difficulty_level=DifficultyLevel(row["difficulty_level"]),
			goal=TemplateGoal(row["goal"]),
			target_muscle_groups=[MuscleGroup(m) for m in json.loads(row["target_muscle_groups"])] if row["target_muscle_groups"] else [],
			target_movement_patterns=[MovementPattern(m) for m in json.loads(row["target_movement_patterns"])] if row["target_movement_patterns"] else [],
			exercise_templates=json.loads(row["exercise_templates"]) if row["exercise_templates"] else [],
			author_user_id=row["author_user_id"],
			is_public=bool(row["is_public"]),
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)


class SQLiteWorkoutExerciseTemplateRepository(WorkoutExerciseTemplateRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, wet: WorkoutExerciseTemplate) -> WorkoutExerciseTemplate:
		self._conn.execute(
			"""INSERT INTO workout_exercise_templates (id, workout_template_id, exercise_id, order_index, target_sets, target_reps_min, target_reps_max, target_rpe, target_intensity_pct_1rm, rest_seconds_between_sets, tempo, notes, superset_group_id, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				wet.id,
				wet.workout_template_id,
				wet.exercise_id,
				wet.order_index,
				wet.target_sets,
				wet.target_reps_min,
				wet.target_reps_max,
				wet.target_rpe,
				wet.target_intensity_pct_1rm,
				wet.rest_seconds_between_sets,
				wet.tempo,
				wet.notes,
				wet.superset_group_id,
				wet.created_at.isoformat(),
				wet.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return wet

	def list_by_template(self, template_id: str) -> List[WorkoutExerciseTemplate]:
		rows = self._conn.execute("SELECT * FROM workout_exercise_templates WHERE workout_template_id = ?", (template_id,)).fetchall()
		return [self._row_to_wet(r) for r in rows]

	def get_by_id(self, wet_id: str) -> Optional[WorkoutExerciseTemplate]:
		row = self._conn.execute("SELECT * FROM workout_exercise_templates WHERE id = ?", (wet_id,)).fetchone()
		return self._row_to_wet(row) if row else None

	def update(self, wet: WorkoutExerciseTemplate) -> WorkoutExerciseTemplate:
		self._conn.execute(
			"""UPDATE workout_exercise_templates SET exercise_id = ?, order_index = ?, target_sets = ?, target_reps_min = ?, target_reps_max = ?, target_rpe = ?, updated_at = ?
			   WHERE id = ?""",
			(
				wet.exercise_id,
				wet.order_index,
				wet.target_sets,
				wet.target_reps_min,
				wet.target_reps_max,
				wet.target_rpe,
				wet.updated_at.isoformat(),
				wet.id,
			),
		)
		self._conn.commit()
		return wet

	def _row_to_wet(self, row: sqlite3.Row) -> WorkoutExerciseTemplate:
		return WorkoutExerciseTemplate(
			id=row["id"],
			workout_template_id=row["workout_template_id"],
			exercise_id=row["exercise_id"],
			order_index=row["order_index"],
			target_sets=row["target_sets"],
			target_reps_min=row["target_reps_min"],
			target_reps_max=row["target_reps_max"],
			target_rpe=row["target_rpe"],
			target_intensity_pct_1rm=row["target_intensity_pct_1rm"],
			rest_seconds_between_sets=row["rest_seconds_between_sets"],
			tempo=row["tempo"],
			notes=row["notes"],
			superset_group_id=row["superset_group_id"],
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)


class SQLiteScheduledWorkoutRepository(ScheduledWorkoutRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, s: ScheduledWorkout) -> ScheduledWorkout:
		self._conn.execute(
			"""INSERT INTO scheduled_workouts (id, user_id, scheduled_date, template_id, program_enrollment_id, program_phase_id, actual_workout_id, status, priority, notes, auto_generated, reschedule_count, recurrence, recurrence_pattern, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				s.id,
				s.user_id,
				s.scheduled_date.isoformat(),
				s.template_id,
				s.program_enrollment_id,
				s.program_phase_id,
				s.actual_workout_id,
				s.status.value,
				s.priority,
				s.notes,
				1 if s.auto_generated else 0,
				s.reschedule_count,
				s.recurrence.value,
				json.dumps(s.recurrence_pattern) if s.recurrence_pattern else None,
				s.created_at.isoformat(),
				s.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return s

	def get_by_id(self, scheduled_id: str) -> Optional[ScheduledWorkout]:
		row = self._conn.execute("SELECT * FROM scheduled_workouts WHERE id = ?", (scheduled_id,)).fetchone()
		return self._row_to_sched(row) if row else None

	def list_by_user_and_date_range(self, user_id: str, start_date: date, end_date: date) -> List[ScheduledWorkout]:
		rows = self._conn.execute(
			"SELECT * FROM scheduled_workouts WHERE user_id = ? AND scheduled_date >= ? AND scheduled_date <= ?",
			(user_id, start_date.isoformat(), end_date.isoformat()),
		).fetchall()
		return [self._row_to_sched(r) for r in rows]

	def update(self, s: ScheduledWorkout) -> ScheduledWorkout:
		self._conn.execute(
			"""UPDATE scheduled_workouts SET scheduled_date = ?, template_id = ?, actual_workout_id = ?, status = ?, priority = ?, reschedule_count = ?, updated_at = ?
			   WHERE id = ?""",
			(
				s.scheduled_date.isoformat(),
				s.template_id,
				s.actual_workout_id,
				s.status.value,
				s.priority,
				s.reschedule_count,
				s.updated_at.isoformat(),
				s.id,
			),
		)
		self._conn.commit()
		return s

	def _row_to_sched(self, row: sqlite3.Row) -> ScheduledWorkout:
		return ScheduledWorkout(
			id=row["id"],
			user_id=row["user_id"],
			scheduled_date=date.fromisoformat(row["scheduled_date"]),
			template_id=row["template_id"],
			program_enrollment_id=row["program_enrollment_id"],
			program_phase_id=row["program_phase_id"],
			actual_workout_id=row["actual_workout_id"],
			status=ScheduleStatus(row["status"]),
			priority=row["priority"],
			notes=row["notes"],
			auto_generated=bool(row["auto_generated"]),
			reschedule_count=row["reschedule_count"],
			recurrence=ScheduleRecurrence(row["recurrence"]),
			recurrence_pattern=json.loads(row["recurrence_pattern"]) if row["recurrence_pattern"] else None,
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)

