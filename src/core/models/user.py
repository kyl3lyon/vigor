from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum

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

@dataclass
class User:
    id: str
    email: str
    username: str
    created_at: datetime
    updated_at: datetime
    last_active_at: datetime
    is_active: bool = True
    timezone: str = "UTC"
    preferred_language: str = "en"

@dataclass
class UserProfile:
    user_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    height_cm: float
    current_weight_kg: float
    activity_level: ActivityLevel
    created_at: datetime
    updated_at: datetime
    experience_level: ExperienceLevel
    years_training: Optional[float]

@dataclass
class UserPreferences:
    user_id: str
    preferred_units: str
    workout_reminders: bool=True
    workout_reminder_time: Optional[str]
    rest_day_preferences: List[str]
    gym_location: Optional[str]
    available_equipment: List[str]
    exercise_dislikes: List[str]
    exercise_restrictions: List[str]
    injury_notes: Optional[str]
    coaching_personality: str
    preferred_units: str = "metric"  # "metric" or "imperial"
    preferred_split: Optional[TrainingSplit]
    sessions_per_week: Optional[int]
    session_duration_preference_minutes: Optional[int]
    progress_updates: bool=True
    achievement_notifications: bool=True
    created_at: datetime
    updated_at: datetime

@dataclass
class UserMemory:
    """
    AI agent's memory of user context, preferences, and important details
    revealed through conversations. This allows personalized coaching.
    """
    id: str
    user_id: str
    memory_type: str          # "injury", "preference", "goal", "constraint", "personal"
    content: str              # Natural language description
    confidence: float         # 0.0-1.0 - How confident is the AI in this memory?
    source: str               # "user_stated", "inferred", "observation"
    relevance_score: float    # How important is this for workout planning?

    # Context
    related_exercises: List[str]     # Exercise IDs this memory relates to
    related_muscle_groups: List[str] # Muscle groups this affects

    # Lifecycle
    is_active: bool = True
    expires_at: Optional[datetime]   # Some memories may be temporary
    created_at: datetime
    updated_at: datetime

    # Examples:
    # "User mentioned bad left shoulder from old injury - avoid overhead pressing"
    # "User prefers morning workouts around 7 AM before work"
    # "User's gym doesn't have a proper squat rack, only Smith machine"
    # "User is training for powerlifting meet in 6 months"
    # "User gets anxious in crowded gyms, prefers off-peak hours"


@dataclass
class FitnessGoal:
    id: str
    user_id: str
    goal_category: str       # "strength", "physique", "performance", "health"
    goal_type: str           # "bench_200lbs", "lose_20lbs", "run_5k", "deadlift_bodyweight"
    description: str         # User's own words
    target_value: Optional[float]
    current_value: Optional[float]
    target_date: Optional[date]
    priority_level: int      # 1-5 (5 = most important)

    # Progress tracking
    is_achieved: bool = False
    achieved_at: Optional[datetime]
    progress_percentage: float = 0.0

    # Context
    why_important: Optional[str]  # User's motivation
    obstacles: List[str]          # What might prevent achievement

    is_active: bool = True
    created_at: datetime
    updated_at: datetime