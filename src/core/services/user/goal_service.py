from dataclasses import replace
from datetime import datetime
from typing import Optional, List

from src.core.models import FitnessGoal
from src.core.repositories.protocols import FitnessGoalRepository
from src.core.shared.errors import ValidationError, NotFoundError


class GoalService:
	 def __init__(self, goal_repo: FitnessGoalRepository) -> None:
		 self._goals = goal_repo

	 def create_goal(
		 self,
		 user_id: str,
		 *,
		 goal_category: str,
		 goal_type: str,
		 priority_level: int,
		 description: Optional[str] = None,
		 target_value: Optional[float] = None,
		 target_date: Optional[datetime] = None,
	 ) -> FitnessGoal:
		 self._validate_priority(priority_level)
		 goal = FitnessGoal(
			 id=str(FitnessGoal.__name__),  # will be overwritten by dataclass default_factory
			 user_id=user_id,
			 goal_category=goal_category,  # type: ignore[arg-type]
			 goal_type=goal_type,
			 description=description or "",
			 target_value=target_value,
			 current_value=None,
			 target_date=target_date.date() if isinstance(target_date, datetime) else target_date,  # type: ignore[assignment]
			 priority_level=priority_level,
			 created_at=datetime.now(),
			 updated_at=datetime.now(),
		 )
		 return self._goals.save(goal)

	 def update_progress(
		 self,
		 goal_id: str,
		 *,
		 current_value: Optional[float] = None,
		 progress_percentage: Optional[float] = None,
		 is_achieved: Optional[bool] = None,
		 achieved_at: Optional[datetime] = None,
	 ) -> FitnessGoal:
		 goal = self._require_goal(goal_id)
		 new_progress = goal.progress_percentage if progress_percentage is None else progress_percentage
		 if new_progress is not None and (new_progress < 0.0 or new_progress > 100.0):
			 raise ValidationError("progress_percentage: must be 0..100")
		 updated = replace(
			 goal,
			 current_value=goal.current_value if current_value is None else current_value,
			 progress_percentage=new_progress if new_progress is not None else goal.progress_percentage,
			 is_achieved=goal.is_achieved if is_achieved is None else is_achieved,
			 achieved_at=goal.achieved_at if achieved_at is None else achieved_at,
			 updated_at=datetime.now(),
		 )
		 return self._goals.update(updated)

	 def list_goals(self, user_id: str, *, active_only: bool = True) -> List[FitnessGoal]:
		 return self._goals.list_by_user(user_id, active_only=active_only)

	 def _require_goal(self, goal_id: str) -> FitnessGoal:
		 goal = self._goals.find_by_id(goal_id)
		 if goal is None:
			 raise NotFoundError("goal: not found")
		 return goal

	 def _validate_priority(self, p: int) -> None:
		 if p < 1 or p > 5:
			 raise ValidationError("priority_level: must be between 1 and 5")


