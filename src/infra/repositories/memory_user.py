from typing import Optional, List

from src.core.models import User, UserProfile, UserPreferences, FitnessGoal, UserMemory
from src.core.repositories.protocols import (
	 UserRepository,
	 UserProfileRepository,
	 UserPreferencesRepository,
	 FitnessGoalRepository,
	 UserMemoryRepository,
)


class InMemoryUserRepository(UserRepository):
	 def __init__(self) -> None:
		 self._by_id: dict[str, User] = {}
		 self._by_email: dict[str, User] = {}
		 self._by_username: dict[str, User] = {}

	 def save(self, user: User) -> User:
		 self._by_id[user.id] = user
		 self._by_email[user.email] = user
		 self._by_username[user.username] = user
		 return user

	 def find_by_id(self, user_id: str) -> Optional[User]:
		 return self._by_id.get(user_id)

	 def find_by_email(self, email: str) -> Optional[User]:
		 return self._by_email.get(email)

	 def find_by_username(self, username: str) -> Optional[User]:
		 return self._by_username.get(username)

	 def update(self, user: User) -> User:
		 existing = self._by_id.get(user.id)
		 if existing is not None:
			 if existing.email != user.email and existing.email in self._by_email:
				 # remove stale email index
				 self._by_email.pop(existing.email, None)
			 if existing.username != user.username and existing.username in self._by_username:
				 # remove stale username index
				 self._by_username.pop(existing.username, None)
		 return self.save(user)


class InMemoryUserProfileRepository(UserProfileRepository):
	 def __init__(self) -> None:
		 self._by_user: dict[str, UserProfile] = {}

	 def save(self, profile: UserProfile) -> UserProfile:
		 self._by_user[profile.user_id] = profile
		 return profile

	 def find_by_user_id(self, user_id: str) -> Optional[UserProfile]:
		 return self._by_user.get(user_id)

	 def update(self, profile: UserProfile) -> UserProfile:
		 return self.save(profile)


class InMemoryUserPreferencesRepository(UserPreferencesRepository):
	 def __init__(self) -> None:
		 self._by_user: dict[str, UserPreferences] = {}

	 def save(self, prefs: UserPreferences) -> UserPreferences:
		 self._by_user[prefs.user_id] = prefs
		 return prefs

	 def find_by_user_id(self, user_id: str) -> Optional[UserPreferences]:
		 return self._by_user.get(user_id)

	 def update(self, prefs: UserPreferences) -> UserPreferences:
		 return self.save(prefs)


class InMemoryFitnessGoalRepository(FitnessGoalRepository):
	 def __init__(self) -> None:
		 self._by_id: dict[str, FitnessGoal] = {}
		 self._by_user: dict[str, List[FitnessGoal]] = {}

	 def save(self, goal: FitnessGoal) -> FitnessGoal:
		 self._by_id[goal.id] = goal
		 self._by_user.setdefault(goal.user_id, []).append(goal)
		 return goal

	 def find_by_id(self, goal_id: str) -> Optional[FitnessGoal]:
		 return self._by_id.get(goal_id)

	 def list_by_user(self, user_id: str, active_only: bool = True) -> List[FitnessGoal]:
		 goals = self._by_user.get(user_id, [])
		 if not active_only:
			 return list(goals)
		 return [g for g in goals if g.is_active]

	 def update(self, goal: FitnessGoal) -> FitnessGoal:
		 self._by_id[goal.id] = goal
		 arr = self._by_user.get(goal.user_id, [])
		 for i, g in enumerate(arr):
			 if g.id == goal.id:
				 arr[i] = goal
				 break
		 return goal


class InMemoryUserMemoryRepository(UserMemoryRepository):
	 def __init__(self) -> None:
		 self._by_user: dict[str, List[UserMemory]] = {}

	 def save(self, memory: UserMemory) -> UserMemory:
		 self._by_user.setdefault(memory.user_id, []).append(memory)
		 return memory

	 def list_active_by_user(self, user_id: str) -> List[UserMemory]:
		 return [m for m in self._by_user.get(user_id, []) if m.is_active]

	 def update(self, memory: UserMemory) -> UserMemory:
		 arr = self._by_user.get(memory.user_id, [])
		 for i, m in enumerate(arr):
			 if m.id == memory.id:
				 arr[i] = memory
				 break
		 return memory


