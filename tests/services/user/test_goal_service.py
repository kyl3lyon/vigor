from datetime import datetime

from src.infra.repositories.memory_user import InMemoryFitnessGoalRepository
from src.core.services.user.goal_service import GoalService
from src.core.models import GoalCategory
from src.core.shared.errors import ValidationError


def test_goal_create_and_progress_bounds():
	 repo = InMemoryFitnessGoalRepository()
	 svc = GoalService(repo)
	 g = svc.create_goal(user_id="u1", goal_category=GoalCategory.STRENGTH, goal_type="bench_100kg", priority_level=3)
	 assert g.goal_category == GoalCategory.STRENGTH
	 # invalid priority
	 try:
		 svc.create_goal(user_id="u1", goal_category=GoalCategory.STRENGTH, goal_type="x", priority_level=9)
		 assert False, "expected ValidationError"
	 except ValidationError:
		 pass
	 # update progress within bounds
	 g2 = svc.update_progress(g.id, progress_percentage=50.0)
	 assert g2.progress_percentage == 50.0
	 # out-of-bounds progress
	 try:
		 svc.update_progress(g.id, progress_percentage=120.0)
		 assert False, "expected ValidationError"
	 except ValidationError:
		 pass


