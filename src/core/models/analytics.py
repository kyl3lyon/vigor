from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

from .workout import MuscleGroup, MovementPattern


class TrendDirection(Enum):
	 INCREASING = "increasing"
	 STABLE = "stable"
	 DECREASING = "decreasing"


@dataclass
class VolumeMetrics:
	 user_id: str
	 analysis_period_days: int
	 total_volume_kg: float
	 volume_by_muscle_group: Dict[MuscleGroup, float] = field(default_factory=dict)
	 volume_by_movement_pattern: Dict[MovementPattern, float] = field(default_factory=dict)
	 weekly_volume_trend: TrendDirection = TrendDirection.STABLE
	 computed_at: datetime = field(default_factory=datetime.now)
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class StrengthAnalysis:
	 user_id: str
	 exercise_id: str
	 estimated_1rm_kg: float
	 strength_velocity_kg_per_week: float
	 volume_trends: Dict[str, float] = field(default_factory=dict)  # week_iso -> volume
	 plateau_risk: float = 0.0  # 0.0-1.0
	 computed_at: datetime = field(default_factory=datetime.now)
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ProgramAnalysis:
	 program_enrollment_id: str
	 strength_gains_pct: Dict[str, float] = field(default_factory=dict)  # exercise_id -> %
	 adherence_rate: float = 0.0  # 0.0-1.0
	 average_session_rpe: Optional[float] = None
	 recommendation: Optional[str] = None  # "continue" | "modify" | "advance_phase"
	 computed_at: datetime = field(default_factory=datetime.now)
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ReadinessScore:
	 user_id: str
	 date: date
	 session_rpe_trend: float
	 volume_fatigue_index: float
	 readiness_score: float  # 0.0-1.0
	 recommended_action: str  # "full_session" | "reduce_volume" | "rest_day"
	 computed_at: datetime = field(default_factory=datetime.now)
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Achievement:
	 user_id: str
	 achievement_type: str  # e.g., "strength_milestone", "consistency"
	 title: str
	 description: str
	 points: int
	 unlocked_at: datetime
	 related_pr_id: Optional[str] = None
	 related_workout_id: Optional[str] = None
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AIInsight:
	 user_id: str
	 insight_type: str  # e.g., "deload_needed", "weight_increase", "exercise_swap"
	 confidence: float  # 0.0-1.0
	 supporting_data: Dict[str, Any] = field(default_factory=dict)
	 recommendation: str = ""
	 expires_at: Optional[datetime] = None
	 created_at: datetime = field(default_factory=datetime.now)
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))

