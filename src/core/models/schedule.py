from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

from .workout import MuscleGroup, MovementPattern


class DifficultyLevel(Enum):
	 BEGINNER = "beginner"
	 INTERMEDIATE = "intermediate"
	 ADVANCED = "advanced"
	 EXPERT = "expert"


class TemplateGoal(Enum):
	 STRENGTH = "strength"
	 HYPERTROPHY = "hypertrophy"
	 ENDURANCE = "endurance"
	 POWER = "power"
	 SKILL = "skill"
	 CONDITIONING = "conditioning"


class ScheduleStatus(Enum):
	 PLANNED = "planned"
	 COMPLETED = "completed"
	 SKIPPED = "skipped"
	 CANCELED = "canceled"


class AutoregulationStrategy(Enum):
	 NONE = "none"
	 RPE_BASED = "rpe_based"
	 PERCENT_1RM = "percent_1rm"
	 REP_RANGE = "rep_range"
	 LINEAR_LOAD = "linear_load"
	 WAVE = "wave"


class ScheduleRecurrence(Enum):
	 NONE = "none"
	 WEEKLY = "weekly"
	 BIWEEKLY = "biweekly"
	 CUSTOM = "custom"


@dataclass
class WorkoutExerciseTemplate:
	 # Required
	 workout_template_id: str
	 exercise_id: str
	 order_index: int

	 # Targets
	 target_sets: Optional[int] = None
	 target_reps_min: Optional[int] = None
	 target_reps_max: Optional[int] = None
	 target_rpe: Optional[float] = None
	 target_intensity_pct_1rm: Optional[float] = None
	 rest_seconds_between_sets: Optional[int] = None
	 tempo: Optional[str] = None
	 notes: Optional[str] = None
	 superset_group_id: Optional[str] = None

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkoutTemplate:
	 # Required
	 name: str

	 # Optional
	 description: Optional[str] = None
	 estimated_duration_minutes: Optional[int] = None
	 difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
	 goal: TemplateGoal = TemplateGoal.STRENGTH
	 target_muscle_groups: List[MuscleGroup] = field(default_factory=list)
	 target_movement_patterns: List[MovementPattern] = field(default_factory=list)
	 exercise_templates: List[str] = field(default_factory=list)  # WorkoutExerciseTemplate IDs
	 author_user_id: Optional[str] = None
	 is_public: bool = False

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProgramPhase:
	 # Required
	 program_id: str
	 name: str
	 order_index: int

	 # Optional
	 start_week: Optional[int] = None
	 end_week: Optional[int] = None
	 workout_template_ids: List[str] = field(default_factory=list)
	 autoregulation: AutoregulationStrategy = AutoregulationStrategy.NONE
	 is_deload: bool = False
	 deload_percentage: Optional[float] = None  # e.g., 0.7 for 70% intensity
	 notes: Optional[str] = None

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrainingProgram:
	 # Required
	 name: str

	 # Optional
	 description: Optional[str] = None
	 duration_weeks: Optional[int] = None
	 difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
	 goal: TemplateGoal = TemplateGoal.STRENGTH
	 phase_ids: List[str] = field(default_factory=list)  # ProgramPhase IDs
	 progression_rules: Dict[str, Any] = field(default_factory=dict)
	 tags: List[str] = field(default_factory=list)
	 author_user_id: Optional[str] = None
	 is_public: bool = False

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProgramEnrollment:
	 # Required
	 user_id: str
	 program_id: str
	 start_date: date

	 # Optional
	 current_phase_id: Optional[str] = None
	 progress_week: Optional[int] = None
	 is_active: bool = True
	 notes: Optional[str] = None
	 ended_at: Optional[date] = None

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScheduledWorkout:
	 # Required
	 user_id: str
	 scheduled_date: date

	 # Optional associations
	 template_id: Optional[str] = None  # WorkoutTemplate
	 program_enrollment_id: Optional[str] = None  # ProgramEnrollment
	 program_phase_id: Optional[str] = None  # ProgramPhase
	 actual_workout_id: Optional[str] = None  # Workout (from workout.py)

	 # Scheduling details
	 status: ScheduleStatus = ScheduleStatus.PLANNED
	 priority: int = 3  # 1-5
	 notes: Optional[str] = None
	 auto_generated: bool = True
	 reschedule_count: int = 0
	 recurrence: ScheduleRecurrence = ScheduleRecurrence.NONE
	 recurrence_pattern: Optional[Dict[str, Any]] = None

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)
