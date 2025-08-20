from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

from .user import UnitSystem


class EquipmentType(Enum):
	 BARBELL = "barbell"
	 DUMBBELL = "dumbbell"
	 KETTLEBELL = "kettlebell"
	 MACHINE = "machine"
	 CABLE = "cable"
	 SMITH_MACHINE = "smith_machine"
	 BODYWEIGHT = "bodyweight"
	 BAND = "band"
	 OTHER = "other"


class MuscleGroup(Enum):
	 CHEST = "chest"
	 BACK = "back"
	 LATS = "lats"
	 TRAPS = "traps"
	 SHOULDERS = "shoulders"
	 BICEPS = "biceps"
	 TRICEPS = "triceps"
	 FOREARMS = "forearms"
	 QUADS = "quads"
	 HAMSTRINGS = "hamstrings"
	 GLUTES = "glutes"
	 CALVES = "calves"
	 CORE = "core"
	 FULL_BODY = "full_body"
	 OTHER = "other"


class MovementPattern(Enum):
	 SQUAT = "squat"
	 HINGE = "hinge"
	 HORIZONTAL_PRESS = "horizontal_press"
	 VERTICAL_PRESS = "vertical_press"
	 HORIZONTAL_PULL = "horizontal_pull"
	 VERTICAL_PULL = "vertical_pull"
	 LUNGE = "lunge"
	 CARRY = "carry"
	 ROTATE = "rotate"
	 ANTI_ROTATE = "anti_rotate"
	 GAIT = "gait"
	 OTHER = "other"


class MechanicsType(Enum):
	 COMPOUND = "compound"
	 ISOLATION = "isolation"


class LoadType(Enum):
	 EXTERNAL = "external"           # barbell/dumbbell/cable/etc
	 BODYWEIGHT = "bodyweight"       # pure bodyweight (e.g., push-ups)
	 BODYWEIGHT_PLUS = "bw_plus"     # bodyweight plus external load (e.g., weighted pull-ups)
	 ASSISTED = "assisted"           # assisted (e.g., assisted dips/pull-ups)
	 NONE = "none"                   # no load (e.g., mobility, holds)


class SetIntent(Enum):
	 WARMUP = "warmup"
	 STRAIGHT_SET = "straight_set"
	 TOP_SET = "top_set"
	 BACKOFF = "backoff"
	 AMRAP = "amrap"
	 DROP_SET = "drop_set"
	 CLUSTER = "cluster"
	 EMOM = "emom"
	 TEMPO = "tempo"


class WorkoutStatus(Enum):
	 PLANNED = "planned"
	 IN_PROGRESS = "in_progress"
	 COMPLETED = "completed"
	 SKIPPED = "skipped"


class PRType(Enum):
	 ONE_RM = "one_rm"                 # 1-rep max
	 N_RM = "n_rm"                     # n-rep max (requires reps)
	 WEIGHT_FOR_REPS = "weight_for_reps"
	 REPS_AT_WEIGHT = "reps_at_weight"
	 MAX_VOLUME_SET = "max_volume_set"
	 MAX_VOLUME_WORKOUT = "max_volume_workout"
	 FASTEST_TIME = "fastest_time"
	 LONGEST_DISTANCE = "longest_distance"


class PRSource(Enum):
	 MANUAL = "manual"
	 COMPUTED = "computed"


@dataclass
class ExerciseDefinition:
	 # Required
	 name: str
	 primary_muscles: List[MuscleGroup]
	 equipment: EquipmentType
	 mechanics: MechanicsType
	 movement_pattern: MovementPattern

	 # Optional
	 secondary_muscles: List[MuscleGroup] = field(default_factory=list)
	 aliases: List[str] = field(default_factory=list)
	 is_unilateral: bool = False
	 default_unit: UnitSystem = UnitSystem.METRIC

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Workout:
	 # Required
	 user_id: str

	 # Optional metadata
	 title: Optional[str] = None
	 notes: Optional[str] = None
	 status: WorkoutStatus = WorkoutStatus.PLANNED
	 session_rpe: Optional[float] = None
	 duration_seconds: Optional[int] = None

	 # Timing
	 started_at: Optional[datetime] = None
	 completed_at: Optional[datetime] = None

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkoutExercise:
	 # Required
	 workout_id: str
	 exercise_id: str
	 order_index: int

	 # Optional targeting/notes
	 notes: Optional[str] = None
	 target_reps: Optional[int] = None
	 target_rpe: Optional[float] = None
	 rest_seconds_between_sets: Optional[int] = None
	 tempo: Optional[str] = None
	 superset_group_id: Optional[str] = None  # group identifier for supersets/giant sets

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExerciseSet:
	 # Required
	 workout_exercise_id: str
	 set_number: int
	 load_type: LoadType

	 # Load/reps/time (only relevant fields are populated per set type)
	 weight_kg: Optional[float] = None           # canonical unit for analytics
	 bodyweight_kg: Optional[float] = None       # captured if relevant at time of set
	 assistance_kg: Optional[float] = None       # positive value indicates assistance magnitude
	 reps: Optional[int] = None
	 time_seconds: Optional[int] = None
	 distance_meters: Optional[float] = None

	 # Effort / execution
	 rpe: Optional[float] = None
	 rir: Optional[float] = None
	 tempo: Optional[str] = None
	 is_warmup: bool = False
	 is_failure: bool = False
	 rest_seconds_after: Optional[int] = None

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PersonalRecord:
	 # Required
	 user_id: str
	 exercise_id: str
	 record_type: PRType
	 achieved_at: datetime

	 # Values (populate according to record_type)
	 weight_kg: Optional[float] = None
	 reps: Optional[int] = None
	 time_seconds: Optional[int] = None
	 distance_meters: Optional[float] = None

	 # Meta
	 notes: Optional[str] = None
	 source: PRSource = PRSource.COMPUTED

	 # Generated
	 id: str = field(default_factory=lambda: str(uuid.uuid4()))
	 created_at: datetime = field(default_factory=datetime.now)
	 updated_at: datetime = field(default_factory=datetime.now)