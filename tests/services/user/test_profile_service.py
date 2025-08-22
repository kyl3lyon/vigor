from datetime import date

from src.infra.repositories.memory_user import (
	 InMemoryUserProfileRepository,
	 InMemoryUserPreferencesRepository,
)
from src.core.services.user.profile_service import ProfileService
from src.core.shared.errors import ValidationError
from src.core.models import Gender, ActivityLevel, ExperienceLevel, UnitSystem, TrainingSplit


def test_profile_create_requires_all_fields_and_validates_numbers():
	 p_repo = InMemoryUserProfileRepository()
	 pref_repo = InMemoryUserPreferencesRepository()
	 svc = ProfileService(p_repo, pref_repo)
	 user_id = "u1"
	 # missing required -> error
	 try:
		 svc.upsert_profile(user_id=user_id, first_name="A", height_cm=180.0, current_weight_kg=80.0)
		 assert False, "expected ValidationError for missing fields"
	 except ValidationError:
		 pass
	 # valid create
	 profile = svc.upsert_profile(
		 user_id=user_id,
		 first_name="A",
		 last_name="B",
		 height_cm=180.0,
		 current_weight_kg=80.0,
		 date_of_birth=date(1990, 1, 1),
		 gender=Gender.MALE,
		 activity_level=ActivityLevel.MODERATELY_ACTIVE,
		 experience_level=ExperienceLevel.INTERMEDIATE,
	 )
	 assert p_repo.find_by_user_id(user_id) is not None
	 # invalid numbers
	 try:
		 svc.upsert_profile(user_id=user_id, height_cm=-1.0)
		 assert False, "expected ValidationError for negative height"
	 except ValidationError:
		 pass


def test_preferences_bounds_and_updates():
	 p_repo = InMemoryUserProfileRepository()
	 pref_repo = InMemoryUserPreferencesRepository()
	 svc = ProfileService(p_repo, pref_repo)
	 user_id = "u1"
	 prefs = svc.upsert_preferences(
		 user_id,
		 preferred_units=UnitSystem.METRIC,
		 preferred_split=TrainingSplit.PUSH_PULL,
		 sessions_per_week=5,
		 session_duration_preference_minutes=60,
	 )
	 assert prefs.sessions_per_week == 5
	 # bounds
	 try:
		 svc.upsert_preferences(user_id, sessions_per_week=20)
		 assert False, "expected ValidationError for sessions_per_week bound"
	 except ValidationError:
		 pass
	 try:
		 svc.upsert_preferences(user_id, session_duration_preference_minutes=5)
		 assert False, "expected ValidationError for duration bound"
	 except ValidationError:
		 pass


