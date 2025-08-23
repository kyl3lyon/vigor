from datetime import date, timedelta

from src.infra.repositories.memory_planning import InMemoryScheduledWorkoutRepository
from src.core.services.planning.schedule_service import ScheduleService


def test_schedule_reschedule_complete_and_range():
	 repo = InMemoryScheduledWorkoutRepository()
	 svc = ScheduleService(repo)
	 today = date.today()
	 s = svc.schedule_workout(user_id="u1", scheduled_date=today, priority=3)
	 assert repo.get_by_id(s.id) is not None
	 # reschedule
	 s2 = svc.reschedule(s.id, new_date=today + timedelta(days=2))
	 assert s2.scheduled_date == today + timedelta(days=2) and s2.reschedule_count == 1
	 # complete (link actual workout)
	 s3 = svc.mark_completed(s.id, actual_workout_id="w1")
	 assert s3.actual_workout_id == "w1"
	 # range
	 items = svc.list_for_user("u1", start_date=today, end_date=today + timedelta(days=7))
	 assert len(items) == 1


