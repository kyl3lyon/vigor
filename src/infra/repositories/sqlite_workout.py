import sqlite3
import json
from typing import Optional, List
from datetime import datetime

from src.core.models import (
	ExerciseDefinition,
	Workout,
	WorkoutExercise,
	ExerciseSet,
	PersonalRecord,
	EquipmentType,
	MuscleGroup,
	MechanicsType,
	MovementPattern,
	LoadType,
	WorkoutStatus,
	PRType,
	PRSource,
)
from src.core.repositories.protocols import (
	ExerciseDefinitionRepository,
	WorkoutRepository,
	WorkoutExerciseRepository,
	ExerciseSetRepository,
	PersonalRecordRepository,
)


class SQLiteExerciseDefinitionRepository(ExerciseDefinitionRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, ex: ExerciseDefinition) -> ExerciseDefinition:
		self._conn.execute(
			"""INSERT INTO exercise_definitions (id, name, primary_muscles, equipment, mechanics, movement_pattern, secondary_muscles, aliases, is_unilateral, default_unit, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				ex.id,
				ex.name,
				json.dumps([m.value for m in ex.primary_muscles]),
				ex.equipment.value,
				ex.mechanics.value,
				ex.movement_pattern.value,
				json.dumps([m.value for m in ex.secondary_muscles]),
				json.dumps(ex.aliases),
				1 if ex.is_unilateral else 0,
				ex.default_unit.value,
				ex.created_at.isoformat(),
				ex.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return ex

	def get_by_id(self, exercise_id: str) -> Optional[ExerciseDefinition]:
		row = self._conn.execute("SELECT * FROM exercise_definitions WHERE id = ?", (exercise_id,)).fetchone()
		return self._row_to_ex(row) if row else None

	def find_by_name(self, name: str) -> Optional[ExerciseDefinition]:
		row = self._conn.execute("SELECT * FROM exercise_definitions WHERE name = ? LIMIT 1", (name,)).fetchone()
		return self._row_to_ex(row) if row else None

	def search(self, *, muscle_groups: Optional[List[str]] = None, equipment: Optional[List[str]] = None) -> List[ExerciseDefinition]:
		rows = self._conn.execute("SELECT * FROM exercise_definitions").fetchall()
		results = []
		for r in rows:
			ex = self._row_to_ex(r)
			if muscle_groups and not any(mg.value in muscle_groups for mg in ex.primary_muscles):
				continue
			if equipment and ex.equipment.value not in equipment:
				continue
			results.append(ex)
		return results

	def _row_to_ex(self, row: sqlite3.Row) -> ExerciseDefinition:
		from src.core.models import UnitSystem
		return ExerciseDefinition(
			id=row["id"],
			name=row["name"],
			primary_muscles=[MuscleGroup(m) for m in json.loads(row["primary_muscles"])],
			equipment=EquipmentType(row["equipment"]),
			mechanics=MechanicsType(row["mechanics"]),
			movement_pattern=MovementPattern(row["movement_pattern"]),
			secondary_muscles=[MuscleGroup(m) for m in json.loads(row["secondary_muscles"])] if row["secondary_muscles"] else [],
			aliases=json.loads(row["aliases"]) if row["aliases"] else [],
			is_unilateral=bool(row["is_unilateral"]),
			default_unit=UnitSystem(row["default_unit"]),
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)


class SQLiteWorkoutRepository(WorkoutRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, workout: Workout) -> Workout:
		self._conn.execute(
			"""INSERT INTO workouts (id, user_id, title, notes, status, session_rpe, duration_seconds, started_at, completed_at, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				workout.id,
				workout.user_id,
				workout.title,
				workout.notes,
				workout.status.value,
				workout.session_rpe,
				workout.duration_seconds,
				workout.started_at.isoformat() if workout.started_at else None,
				workout.completed_at.isoformat() if workout.completed_at else None,
				workout.created_at.isoformat(),
				workout.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return workout

	def get_by_id(self, workout_id: str) -> Optional[Workout]:
		row = self._conn.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,)).fetchone()
		return self._row_to_workout(row) if row else None

	def update(self, workout: Workout) -> Workout:
		self._conn.execute(
			"""UPDATE workouts SET title = ?, notes = ?, status = ?, session_rpe = ?, duration_seconds = ?, started_at = ?, completed_at = ?, updated_at = ?
			   WHERE id = ?""",
			(
				workout.title,
				workout.notes,
				workout.status.value,
				workout.session_rpe,
				workout.duration_seconds,
				workout.started_at.isoformat() if workout.started_at else None,
				workout.completed_at.isoformat() if workout.completed_at else None,
				workout.updated_at.isoformat(),
				workout.id,
			),
		)
		self._conn.commit()
		return workout

	def list_by_user_recent(self, user_id: str, limit: int = 20) -> List[Workout]:
		rows = self._conn.execute(
			"SELECT * FROM workouts WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit)
		).fetchall()
		return [self._row_to_workout(r) for r in rows]

	def _row_to_workout(self, row: sqlite3.Row) -> Workout:
		return Workout(
			id=row["id"],
			user_id=row["user_id"],
			title=row["title"],
			notes=row["notes"],
			status=WorkoutStatus(row["status"]),
			session_rpe=row["session_rpe"],
			duration_seconds=row["duration_seconds"],
			started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
			completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)


class SQLiteWorkoutExerciseRepository(WorkoutExerciseRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, we: WorkoutExercise) -> WorkoutExercise:
		self._conn.execute(
			"""INSERT INTO workout_exercises (id, workout_id, exercise_id, order_index, notes, target_reps, target_rpe, rest_seconds_between_sets, tempo, superset_group_id, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				we.id,
				we.workout_id,
				we.exercise_id,
				we.order_index,
				we.notes,
				we.target_reps,
				we.target_rpe,
				we.rest_seconds_between_sets,
				we.tempo,
				we.superset_group_id,
				we.created_at.isoformat(),
				we.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return we

	def list_by_workout(self, workout_id: str) -> List[WorkoutExercise]:
		rows = self._conn.execute("SELECT * FROM workout_exercises WHERE workout_id = ?", (workout_id,)).fetchall()
		return [self._row_to_we(r) for r in rows]

	def get_by_id(self, workout_exercise_id: str) -> Optional[WorkoutExercise]:
		row = self._conn.execute("SELECT * FROM workout_exercises WHERE id = ?", (workout_exercise_id,)).fetchone()
		return self._row_to_we(row) if row else None

	def _row_to_we(self, row: sqlite3.Row) -> WorkoutExercise:
		return WorkoutExercise(
			id=row["id"],
			workout_id=row["workout_id"],
			exercise_id=row["exercise_id"],
			order_index=row["order_index"],
			notes=row["notes"],
			target_reps=row["target_reps"],
			target_rpe=row["target_rpe"],
			rest_seconds_between_sets=row["rest_seconds_between_sets"],
			tempo=row["tempo"],
			superset_group_id=row["superset_group_id"],
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)


class SQLiteExerciseSetRepository(ExerciseSetRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, s: ExerciseSet) -> ExerciseSet:
		self._conn.execute(
			"""INSERT INTO exercise_sets (id, workout_exercise_id, set_number, load_type, weight_kg, bodyweight_kg, assistance_kg, reps, time_seconds, distance_meters, rpe, rir, tempo, is_warmup, is_failure, rest_seconds_after, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				s.id,
				s.workout_exercise_id,
				s.set_number,
				s.load_type.value,
				s.weight_kg,
				s.bodyweight_kg,
				s.assistance_kg,
				s.reps,
				s.time_seconds,
				s.distance_meters,
				s.rpe,
				s.rir,
				s.tempo,
				1 if s.is_warmup else 0,
				1 if s.is_failure else 0,
				s.rest_seconds_after,
				s.created_at.isoformat(),
				s.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return s

	def list_for_workout_exercise(self, workout_exercise_id: str) -> List[ExerciseSet]:
		rows = self._conn.execute("SELECT * FROM exercise_sets WHERE workout_exercise_id = ?", (workout_exercise_id,)).fetchall()
		return [self._row_to_set(r) for r in rows]

	def _row_to_set(self, row: sqlite3.Row) -> ExerciseSet:
		return ExerciseSet(
			id=row["id"],
			workout_exercise_id=row["workout_exercise_id"],
			set_number=row["set_number"],
			load_type=LoadType(row["load_type"]),
			weight_kg=row["weight_kg"],
			bodyweight_kg=row["bodyweight_kg"],
			assistance_kg=row["assistance_kg"],
			reps=row["reps"],
			time_seconds=row["time_seconds"],
			distance_meters=row["distance_meters"],
			rpe=row["rpe"],
			rir=row["rir"],
			tempo=row["tempo"],
			is_warmup=bool(row["is_warmup"]),
			is_failure=bool(row["is_failure"]),
			rest_seconds_after=row["rest_seconds_after"],
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)


class SQLitePersonalRecordRepository(PersonalRecordRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, pr: PersonalRecord) -> PersonalRecord:
		self._conn.execute(
			"""INSERT INTO personal_records (id, user_id, exercise_id, record_type, achieved_at, weight_kg, reps, time_seconds, distance_meters, notes, source, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				pr.id,
				pr.user_id,
				pr.exercise_id,
				pr.record_type.value,
				pr.achieved_at.isoformat(),
				pr.weight_kg,
				pr.reps,
				pr.time_seconds,
				pr.distance_meters,
				pr.notes,
				pr.source.value,
				pr.created_at.isoformat(),
				pr.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return pr

	def list_by_user_and_exercise(self, user_id: str, exercise_id: str) -> List[PersonalRecord]:
		rows = self._conn.execute(
			"SELECT * FROM personal_records WHERE user_id = ? AND exercise_id = ?", (user_id, exercise_id)
		).fetchall()
		return [self._row_to_pr(r) for r in rows]

	def get_best_one_rm(self, user_id: str, exercise_id: str) -> Optional[PersonalRecord]:
		row = self._conn.execute(
			"SELECT * FROM personal_records WHERE user_id = ? AND exercise_id = ? ORDER BY weight_kg DESC LIMIT 1",
			(user_id, exercise_id),
		).fetchone()
		return self._row_to_pr(row) if row else None

	def _row_to_pr(self, row: sqlite3.Row) -> PersonalRecord:
		return PersonalRecord(
			id=row["id"],
			user_id=row["user_id"],
			exercise_id=row["exercise_id"],
			record_type=PRType(row["record_type"]),
			achieved_at=datetime.fromisoformat(row["achieved_at"]),
			weight_kg=row["weight_kg"],
			reps=row["reps"],
			time_seconds=row["time_seconds"],
			distance_meters=row["distance_meters"],
			notes=row["notes"],
			source=PRSource(row["source"]),
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)

