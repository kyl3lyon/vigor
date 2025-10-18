from dataclasses import replace
from datetime import datetime, date
from typing import Optional, List

from src.core.models import UserProfile, UserPreferences, UnitSystem, TrainingSplit, ActivityLevel, ExperienceLevel, Gender
from src.core.repositories.protocols import UserProfileRepository, UserPreferencesRepository
from src.core.shared.errors import ValidationError, NotFoundError


class ProfileService:
	 def __init__(self, profile_repo: UserProfileRepository, prefs_repo: UserPreferencesRepository) -> None:
		 self._profiles = profile_repo
		 self._prefs = prefs_repo

	 # Profile
	 def upsert_profile(
		 self,
		 user_id: str,
		 *,
		 first_name: Optional[str] = None,
		 last_name: Optional[str] = None,
		 height_cm: Optional[float] = None,
		 current_weight_kg: Optional[float] = None,
		 date_of_birth: Optional[date] = None,
		 gender: Optional[Gender] = None,
		 activity_level: Optional[ActivityLevel] = None,
		 experience_level: Optional[ExperienceLevel] = None,
	 ) -> UserProfile:
		 profile = self._profiles.find_by_user_id(user_id)
		 if profile is None:
			 if (
				 first_name is None
				 or height_cm is None
				 or current_weight_kg is None
				 or date_of_birth is None
				 or gender is None
				 or activity_level is None
				 or experience_level is None
			 ):
				 raise ValidationError("missing required fields to create profile")
			 base = UserProfile(
				 user_id=user_id,
				 first_name=first_name,
				 last_name=last_name,
				 date_of_birth=date_of_birth,
				 gender=gender,
				 height_cm=height_cm,
				 current_weight_kg=current_weight_kg,
				 activity_level=activity_level,
				 experience_level=experience_level,
				 years_training=None,
				 created_at=datetime.now(),
				 updated_at=datetime.now(),
			 )
			 return self._profiles.save(base)

		 # update
		 updated = replace(
			 profile,
			 first_name=profile.first_name if first_name is None else first_name,
			 last_name=profile.last_name if last_name is None else last_name,
			 height_cm=profile.height_cm if height_cm is None else height_cm,
			 current_weight_kg=profile.current_weight_kg if current_weight_kg is None else current_weight_kg,
			 date_of_birth=profile.date_of_birth if date_of_birth is None else date_of_birth,
			 gender=profile.gender if gender is None else gender,
			 activity_level=profile.activity_level if activity_level is None else activity_level,
			 experience_level=profile.experience_level if experience_level is None else experience_level,
			 updated_at=datetime.now(),
		 )
		 self._validate_profile(updated)
		 return self._profiles.update(updated)

	 def _validate_profile(self, p: UserProfile) -> None:
		 if p.height_cm <= 0:
			 raise ValidationError("height_cm: must be positive")
		 if p.current_weight_kg <= 0:
			 raise ValidationError("current_weight_kg: must be positive")

	 # Preferences
	 def upsert_preferences(
		 self,
		 user_id: str,
		 *,
		 preferred_units: Optional[UnitSystem] = None,
		 preferred_split: Optional[TrainingSplit] = None,
		 sessions_per_week: Optional[int] = None,
		 session_duration_preference_minutes: Optional[int] = None,
		 workout_reminders: Optional[bool] = None,
		 workout_reminder_time: Optional[str] = None,
		 rest_day_preferences: Optional[List[str]] = None,
		 gym_location: Optional[str] = None,
		 available_equipment: Optional[List[str]] = None,
		 exercise_dislikes: Optional[List[str]] = None,
		 exercise_restrictions: Optional[List[str]] = None,
		 injury_notes: Optional[str] = None,
		 progress_updates: Optional[bool] = None,
		 achievement_notifications: Optional[bool] = None,
	 ) -> UserPreferences:
		 prefs = self._prefs.find_by_user_id(user_id)
		 if prefs is None:
			 new_prefs = UserPreferences(
				 user_id=user_id,
				 preferred_units=preferred_units or UnitSystem.METRIC,
				 preferred_split=preferred_split,
				 sessions_per_week=sessions_per_week,
				 session_duration_preference_minutes=session_duration_preference_minutes,
				 workout_reminders=workout_reminders if workout_reminders is not None else True,
				 workout_reminder_time=workout_reminder_time,
				 rest_day_preferences=rest_day_preferences or [],
				 gym_location=gym_location,
				 available_equipment=available_equipment or [],
				 exercise_dislikes=exercise_dislikes or [],
				 exercise_restrictions=exercise_restrictions or [],
				 injury_notes=injury_notes,
				 progress_updates=progress_updates if progress_updates is not None else True,
				 achievement_notifications=achievement_notifications if achievement_notifications is not None else True,
				 created_at=datetime.now(),
				 updated_at=datetime.now(),
			 )
			 return self._prefs.save(new_prefs)

		 updated = replace(
			 prefs,
			 preferred_units=prefs.preferred_units if preferred_units is None else preferred_units,
			 preferred_split=prefs.preferred_split if preferred_split is None else preferred_split,
			 sessions_per_week=prefs.sessions_per_week if sessions_per_week is None else sessions_per_week,
			 session_duration_preference_minutes=(
				 prefs.session_duration_preference_minutes if session_duration_preference_minutes is None else session_duration_preference_minutes
			 ),
			 workout_reminders=prefs.workout_reminders if workout_reminders is None else workout_reminders,
			 workout_reminder_time=prefs.workout_reminder_time if workout_reminder_time is None else workout_reminder_time,
			 rest_day_preferences=prefs.rest_day_preferences if rest_day_preferences is None else rest_day_preferences,
			 gym_location=prefs.gym_location if gym_location is None else gym_location,
			 available_equipment=prefs.available_equipment if available_equipment is None else available_equipment,
			 exercise_dislikes=prefs.exercise_dislikes if exercise_dislikes is None else exercise_dislikes,
			 exercise_restrictions=prefs.exercise_restrictions if exercise_restrictions is None else exercise_restrictions,
			 injury_notes=prefs.injury_notes if injury_notes is None else injury_notes,
			 progress_updates=prefs.progress_updates if progress_updates is None else progress_updates,
			 achievement_notifications=prefs.achievement_notifications if achievement_notifications is None else achievement_notifications,
			 updated_at=datetime.now(),
		 )
		 self._validate_preferences(updated)
		 return self._prefs.update(updated)

	 def _validate_preferences(self, p: UserPreferences) -> None:
		 if p.sessions_per_week is not None and (p.sessions_per_week < 0 or p.sessions_per_week > 14):
			 raise ValidationError("sessions_per_week: must be between 0 and 14")
		 if (
			 p.session_duration_preference_minutes is not None
			 and (p.session_duration_preference_minutes < 10 or p.session_duration_preference_minutes > 240)
		 ):
			 raise ValidationError("session_duration_preference_minutes: must be between 10 and 240")


