import sqlite3
import json
from typing import Optional, List
from datetime import datetime, date

from src.core.models import User, UserProfile, UserPreferences, FitnessGoal, UserMemory
from src.core.models import ActivityLevel, ExperienceLevel, Gender, UnitSystem, TrainingSplit, GoalCategory, MemoryType, MemorySource
from src.core.repositories.protocols import (
	UserRepository,
	UserProfileRepository,
	UserPreferencesRepository,
	FitnessGoalRepository,
	UserMemoryRepository,
)


class SQLiteUserRepository(UserRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, user: User) -> User:
		self._conn.execute(
			"""INSERT INTO users (id, email, username, created_at, updated_at, last_active_at, is_active, timezone, preferred_language)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				user.id,
				user.email,
				user.username,
				user.created_at.isoformat(),
				user.updated_at.isoformat(),
				user.last_active_at.isoformat(),
				1 if user.is_active else 0,
				user.timezone,
				user.preferred_language,
			),
		)
		self._conn.commit()
		return user

	def find_by_id(self, user_id: str) -> Optional[User]:
		row = self._conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
		return self._row_to_user(row) if row else None

	def find_by_email(self, email: str) -> Optional[User]:
		row = self._conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
		return self._row_to_user(row) if row else None

	def find_by_username(self, username: str) -> Optional[User]:
		row = self._conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
		return self._row_to_user(row) if row else None

	def update(self, user: User) -> User:
		self._conn.execute(
			"""UPDATE users SET email = ?, username = ?, updated_at = ?, last_active_at = ?, is_active = ?, timezone = ?, preferred_language = ?
			   WHERE id = ?""",
			(
				user.email,
				user.username,
				user.updated_at.isoformat(),
				user.last_active_at.isoformat(),
				1 if user.is_active else 0,
				user.timezone,
				user.preferred_language,
				user.id,
			),
		)
		self._conn.commit()
		return user

	def _row_to_user(self, row: sqlite3.Row) -> User:
		return User(
			id=row["id"],
			email=row["email"],
			username=row["username"],
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
			last_active_at=datetime.fromisoformat(row["last_active_at"]),
			is_active=bool(row["is_active"]),
			timezone=row["timezone"],
			preferred_language=row["preferred_language"],
		)


class SQLiteUserProfileRepository(UserProfileRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, profile: UserProfile) -> UserProfile:
		self._conn.execute(
			"""INSERT INTO user_profiles (user_id, first_name, last_name, date_of_birth, gender, height_cm, current_weight_kg, activity_level, experience_level, years_training, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				profile.user_id,
				profile.first_name,
				profile.last_name,
				profile.date_of_birth.isoformat(),
				profile.gender.value,
				profile.height_cm,
				profile.current_weight_kg,
				profile.activity_level.value,
				profile.experience_level.value,
				profile.years_training,
				profile.created_at.isoformat(),
				profile.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return profile

	def find_by_user_id(self, user_id: str) -> Optional[UserProfile]:
		row = self._conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()
		if not row:
			return None
		return UserProfile(
			user_id=row["user_id"],
			first_name=row["first_name"],
			last_name=row["last_name"],
			date_of_birth=date.fromisoformat(row["date_of_birth"]),
			gender=Gender(row["gender"]),
			height_cm=row["height_cm"],
			current_weight_kg=row["current_weight_kg"],
			activity_level=ActivityLevel(row["activity_level"]),
			experience_level=ExperienceLevel(row["experience_level"]),
			years_training=row["years_training"],
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)

	def update(self, profile: UserProfile) -> UserProfile:
		self._conn.execute(
			"""UPDATE user_profiles SET first_name = ?, last_name = ?, date_of_birth = ?, gender = ?, height_cm = ?, current_weight_kg = ?, activity_level = ?, experience_level = ?, years_training = ?, updated_at = ?
			   WHERE user_id = ?""",
			(
				profile.first_name,
				profile.last_name,
				profile.date_of_birth.isoformat(),
				profile.gender.value,
				profile.height_cm,
				profile.current_weight_kg,
				profile.activity_level.value,
				profile.experience_level.value,
				profile.years_training,
				profile.updated_at.isoformat(),
				profile.user_id,
			),
		)
		self._conn.commit()
		return profile


class SQLiteUserPreferencesRepository(UserPreferencesRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, prefs: UserPreferences) -> UserPreferences:
		self._conn.execute(
			"""INSERT INTO user_preferences (user_id, preferred_units, workout_reminders, workout_reminder_time, rest_day_preferences, gym_location, available_equipment, exercise_dislikes, exercise_restrictions, injury_notes, coaching_personality, preferred_split, sessions_per_week, session_duration_preference_minutes, progress_updates, achievement_notifications, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				prefs.user_id,
				prefs.preferred_units.value,
				1 if prefs.workout_reminders else 0,
				prefs.workout_reminder_time,
				json.dumps(prefs.rest_day_preferences),
				prefs.gym_location,
				json.dumps(prefs.available_equipment),
				json.dumps(prefs.exercise_dislikes),
				json.dumps(prefs.exercise_restrictions),
				prefs.injury_notes,
				prefs.coaching_personality.value if prefs.coaching_personality else None,
				prefs.preferred_split.value if prefs.preferred_split else None,
				prefs.sessions_per_week,
				prefs.session_duration_preference_minutes,
				1 if prefs.progress_updates else 0,
				1 if prefs.achievement_notifications else 0,
				prefs.created_at.isoformat(),
				prefs.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return prefs

	def find_by_user_id(self, user_id: str) -> Optional[UserPreferences]:
		row = self._conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
		if not row:
			return None
		return UserPreferences(
			user_id=row["user_id"],
			preferred_units=UnitSystem(row["preferred_units"]),
			workout_reminders=bool(row["workout_reminders"]),
			workout_reminder_time=row["workout_reminder_time"],
			rest_day_preferences=json.loads(row["rest_day_preferences"]) if row["rest_day_preferences"] else [],
			gym_location=row["gym_location"],
			available_equipment=json.loads(row["available_equipment"]) if row["available_equipment"] else [],
			exercise_dislikes=json.loads(row["exercise_dislikes"]) if row["exercise_dislikes"] else [],
			exercise_restrictions=json.loads(row["exercise_restrictions"]) if row["exercise_restrictions"] else [],
			injury_notes=row["injury_notes"],
			coaching_personality=None,  # Enum missing; can add later
			preferred_split=TrainingSplit(row["preferred_split"]) if row["preferred_split"] else None,
			sessions_per_week=row["sessions_per_week"],
			session_duration_preference_minutes=row["session_duration_preference_minutes"],
			progress_updates=bool(row["progress_updates"]),
			achievement_notifications=bool(row["achievement_notifications"]),
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)

	def update(self, prefs: UserPreferences) -> UserPreferences:
		self._conn.execute(
			"""UPDATE user_preferences SET preferred_units = ?, workout_reminders = ?, workout_reminder_time = ?, rest_day_preferences = ?, gym_location = ?, available_equipment = ?, exercise_dislikes = ?, exercise_restrictions = ?, injury_notes = ?, coaching_personality = ?, preferred_split = ?, sessions_per_week = ?, session_duration_preference_minutes = ?, progress_updates = ?, achievement_notifications = ?, updated_at = ?
			   WHERE user_id = ?""",
			(
				prefs.preferred_units.value,
				1 if prefs.workout_reminders else 0,
				prefs.workout_reminder_time,
				json.dumps(prefs.rest_day_preferences),
				prefs.gym_location,
				json.dumps(prefs.available_equipment),
				json.dumps(prefs.exercise_dislikes),
				json.dumps(prefs.exercise_restrictions),
				prefs.injury_notes,
				prefs.coaching_personality.value if prefs.coaching_personality else None,
				prefs.preferred_split.value if prefs.preferred_split else None,
				prefs.sessions_per_week,
				prefs.session_duration_preference_minutes,
				1 if prefs.progress_updates else 0,
				1 if prefs.achievement_notifications else 0,
				prefs.updated_at.isoformat(),
				prefs.user_id,
			),
		)
		self._conn.commit()
		return prefs


class SQLiteFitnessGoalRepository(FitnessGoalRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, goal: FitnessGoal) -> FitnessGoal:
		self._conn.execute(
			"""INSERT INTO fitness_goals (id, user_id, goal_category, goal_type, description, target_value, current_value, target_date, priority_level, is_achieved, achieved_at, progress_percentage, why_important, obstacles, is_active, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				goal.id,
				goal.user_id,
				goal.goal_category.value,
				goal.goal_type,
				goal.description,
				goal.target_value,
				goal.current_value,
				goal.target_date.isoformat() if goal.target_date else None,
				goal.priority_level,
				1 if goal.is_achieved else 0,
				goal.achieved_at.isoformat() if goal.achieved_at else None,
				goal.progress_percentage,
				goal.why_important,
				json.dumps(goal.obstacles),
				1 if goal.is_active else 0,
				goal.created_at.isoformat(),
				goal.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return goal

	def find_by_id(self, goal_id: str) -> Optional[FitnessGoal]:
		row = self._conn.execute("SELECT * FROM fitness_goals WHERE id = ?", (goal_id,)).fetchone()
		return self._row_to_goal(row) if row else None

	def list_by_user(self, user_id: str, active_only: bool = True) -> List[FitnessGoal]:
		if active_only:
			rows = self._conn.execute("SELECT * FROM fitness_goals WHERE user_id = ? AND is_active = 1", (user_id,)).fetchall()
		else:
			rows = self._conn.execute("SELECT * FROM fitness_goals WHERE user_id = ?", (user_id,)).fetchall()
		return [self._row_to_goal(r) for r in rows]

	def update(self, goal: FitnessGoal) -> FitnessGoal:
		self._conn.execute(
			"""UPDATE fitness_goals SET goal_category = ?, goal_type = ?, description = ?, target_value = ?, current_value = ?, target_date = ?, priority_level = ?, is_achieved = ?, achieved_at = ?, progress_percentage = ?, why_important = ?, obstacles = ?, is_active = ?, updated_at = ?
			   WHERE id = ?""",
			(
				goal.goal_category.value,
				goal.goal_type,
				goal.description,
				goal.target_value,
				goal.current_value,
				goal.target_date.isoformat() if goal.target_date else None,
				goal.priority_level,
				1 if goal.is_achieved else 0,
				goal.achieved_at.isoformat() if goal.achieved_at else None,
				goal.progress_percentage,
				goal.why_important,
				json.dumps(goal.obstacles),
				1 if goal.is_active else 0,
				goal.updated_at.isoformat(),
				goal.id,
			),
		)
		self._conn.commit()
		return goal

	def _row_to_goal(self, row: sqlite3.Row) -> FitnessGoal:
		return FitnessGoal(
			id=row["id"],
			user_id=row["user_id"],
			goal_category=GoalCategory(row["goal_category"]),
			goal_type=row["goal_type"],
			description=row["description"],
			target_value=row["target_value"],
			current_value=row["current_value"],
			target_date=date.fromisoformat(row["target_date"]) if row["target_date"] else None,
			priority_level=row["priority_level"],
			is_achieved=bool(row["is_achieved"]),
			achieved_at=datetime.fromisoformat(row["achieved_at"]) if row["achieved_at"] else None,
			progress_percentage=row["progress_percentage"],
			why_important=row["why_important"],
			obstacles=json.loads(row["obstacles"]) if row["obstacles"] else [],
			is_active=bool(row["is_active"]),
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)


class SQLiteUserMemoryRepository(UserMemoryRepository):
	def __init__(self, conn: sqlite3.Connection) -> None:
		self._conn = conn

	def save(self, memory: UserMemory) -> UserMemory:
		self._conn.execute(
			"""INSERT INTO user_memories (id, user_id, memory_type, content, confidence, source, relevance_score, related_exercises, related_muscle_groups, is_active, expires_at, created_at, updated_at)
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
			(
				memory.id,
				memory.user_id,
				memory.memory_type.value,
				memory.content,
				memory.confidence,
				memory.source.value,
				memory.relevance_score,
				json.dumps(memory.related_exercises),
				json.dumps(memory.related_muscle_groups),
				1 if memory.is_active else 0,
				memory.expires_at.isoformat() if memory.expires_at else None,
				memory.created_at.isoformat(),
				memory.updated_at.isoformat(),
			),
		)
		self._conn.commit()
		return memory

	def list_active_by_user(self, user_id: str) -> List[UserMemory]:
		rows = self._conn.execute("SELECT * FROM user_memories WHERE user_id = ? AND is_active = 1", (user_id,)).fetchall()
		return [self._row_to_memory(r) for r in rows]

	def update(self, memory: UserMemory) -> UserMemory:
		self._conn.execute(
			"""UPDATE user_memories SET memory_type = ?, content = ?, confidence = ?, source = ?, relevance_score = ?, related_exercises = ?, related_muscle_groups = ?, is_active = ?, expires_at = ?, updated_at = ?
			   WHERE id = ?""",
			(
				memory.memory_type.value,
				memory.content,
				memory.confidence,
				memory.source.value,
				memory.relevance_score,
				json.dumps(memory.related_exercises),
				json.dumps(memory.related_muscle_groups),
				1 if memory.is_active else 0,
				memory.expires_at.isoformat() if memory.expires_at else None,
				memory.updated_at.isoformat(),
				memory.id,
			),
		)
		self._conn.commit()
		return memory

	def _row_to_memory(self, row: sqlite3.Row) -> UserMemory:
		return UserMemory(
			id=row["id"],
			user_id=row["user_id"],
			memory_type=MemoryType(row["memory_type"]),
			content=row["content"],
			confidence=row["confidence"],
			source=MemorySource(row["source"]),
			relevance_score=row["relevance_score"],
			related_exercises=json.loads(row["related_exercises"]) if row["related_exercises"] else [],
			related_muscle_groups=json.loads(row["related_muscle_groups"]) if row["related_muscle_groups"] else [],
			is_active=bool(row["is_active"]),
			expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
			created_at=datetime.fromisoformat(row["created_at"]),
			updated_at=datetime.fromisoformat(row["updated_at"]),
		)

