from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
import uuid


class TrainingSplit(Enum):
	 BRO_SPLIT = "bro_split"
	 PUSH_PULL_LEGS = "push_pull_legs"
	 UPPER_LOWER = "upper_lower"
	 FULL_BODY = "full_body"
	 PUSH_PULL = "push_pull"
	 UPPER_LOWER_PUSH_PULL = "upper_lower_push_pull"
	 CUSTOM = "custom"


class ExperienceLevel(Enum):
	 BEGINNER = "beginner"
	 INTERMEDIATE = "intermediate"
	 ADVANCED = "advanced"
	 EXPERT = "expert"


class ActivityLevel(Enum):
	 SEDENTARY = "sedentary"
	 LIGHTLY_ACTIVE = "lightly_active"
	 MODERATELY_ACTIVE = "moderately_active"
	 VERY_ACTIVE = "very_active"
	 EXTREMELY_ACTIVE = "extremely_active"


class Gender(Enum):
	 MALE = "male"
	 FEMALE = "female"


class UnitSystem(Enum):
	 METRIC = "metric"
	 IMPERIAL = "imperial"


class CoachingPersonality(Enum):
	 SUPPORTIVE = "supportive"
	 DATA_DRIVEN = "data_driven"
	 TOUGH_LOVE = "tough_love"
	 MINIMAL = "minimal"


class MemoryType(Enum):
	 INJURY = "injury"
	 PREFERENCE = "preference"
	 GOAL = "goal"
	 CONSTRAINT = "constraint"
	 PERSONAL = "personal"


class MemorySource(Enum):
	 USER_STATED = "user_stated"
	 INFERRED = "inferred"
	 OBSERVATION = "observation"


class GoalCategory(Enum):
	 STRENGTH = "strength"
	 PHYSIQUE = "physique"
	 PERFORMANCE = "performance"
	 HEALTH = "health"


@dataclass
class User:
	 # Required
	 email: str
	 username: str

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)
	 last_active_at: datetime = field(default_factory=datetime.now)

	 # Optional with sensible defaults
	 is_active: bool = True
	 timezone: str = "UTC"
	 preferred_language: str = "en"


@dataclass
class UserProfile:
	 # Required
	 user_id: str
	 first_name: str
	 date_of_birth: date
	 gender: Gender
	 height_cm: float
	 current_weight_kg: float
	 activity_level: ActivityLevel
	 experience_level: ExperienceLevel

	 # Optional
	 last_name: Optional[str] = None
	 years_training: Optional[float] = None

	 # Generated
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserPreferences:
	 # Required
	 user_id: str

	 # Configuration
	 preferred_units: UnitSystem = UnitSystem.METRIC
	 preferred_split: Optional[TrainingSplit] = None

	 # Lists with safe defaults
	 rest_day_preferences: List[str] = field(default_factory=list)
	 available_equipment: List[str] = field(default_factory=list)
	 exercise_dislikes: List[str] = field(default_factory=list)
	 exercise_restrictions: List[str] = field(default_factory=list)

	 # Optional
	 workout_reminder_time: Optional[str] = None
	 gym_location: Optional[str] = None
	 injury_notes: Optional[str] = None
	 sessions_per_week: Optional[int] = None
	 session_duration_preference_minutes: Optional[int] = None
	 coaching_personality: Optional[CoachingPersonality] = None

	 # Flags
	 workout_reminders: bool = True
	 progress_updates: bool = True
	 achievement_notifications: bool = True

	 # Generated
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserMemory:
	 # Required
	 user_id: str
	 memory_type: MemoryType
	 content: str
	 source: MemorySource

	 # Measures
	 confidence: float = 0.0
	 relevance_score: float = 0.0

	 # Associations
	 related_exercises: List[str] = field(default_factory=list)
	 related_muscle_groups: List[str] = field(default_factory=list)

	 # Lifecycle
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 is_active: bool = True
	 expires_at: Optional[datetime] = None
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class FitnessGoal:
	 # Required
	 user_id: str
	 goal_category: GoalCategory
	 goal_type: str
	 priority_level: int  # 1-5 (5 = most important)

	 # Optional targets/progress
	 description: Optional[str] = None
	 target_value: Optional[float] = None
	 current_value: Optional[float] = None
	 target_date: Optional[date] = None

	 # Progress tracking
	 is_achieved: bool = False
	 achieved_at: Optional[datetime] = None
	 progress_percentage: float = 0.0

	 # Context
	 why_important: Optional[str] = None
	 obstacles: List[str] = field(default_factory=list)

	 # Lifecycle
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 is_active: bool = True
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)