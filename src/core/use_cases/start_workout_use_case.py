from dataclasses import dataclass
from typing import Optional

from src.core.services.workout.session_service import SessionService


@dataclass
class StartWorkoutUseCase:
	 session_service: SessionService

	 def execute(self, user_id: str, *, title: Optional[str] = None, notes: Optional[str] = None):
		 return self.session_service.start_workout(user_id, title=title, notes=notes)


