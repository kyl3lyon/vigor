from datetime import date

from src.infra.repositories.memory_user import (
	 InMemoryUserRepository,
	 InMemoryUserProfileRepository,
	 InMemoryUserPreferencesRepository,
	 InMemoryFitnessGoalRepository,
	 InMemoryUserMemoryRepository,
)
from src.core.models import (
	 User,
	 UserProfile,
	 UserPreferences,
	 FitnessGoal,
	 UserMemory,
	 ActivityLevel,
	 ExperienceLevel,
	 Gender,
	 GoalCategory,
	 MemoryType,
	 MemorySource,
)


def test_user_repo_save_and_indexes_update():
	"""
	Test that the user repository can save and retrieve users, and that the secondary indexes are updated correctly.
	"""
	repo = InMemoryUserRepository()
	u = User(email="a@b.com", username="ab")
	repo.save(u)
	assert repo.find_by_id(u.id) is not None
	assert repo.find_by_email("a@b.com") is not None
	assert repo.find_by_username("ab") is not None

	 # update email and username, ensure secondary indexes move
	u2 = User(
		id=u.id,
		email="c@d.com",
		username="cd",
		created_at=u.created_at,
		updated_at=u.updated_at,
		last_active_at=u.last_active_at,
	)
	repo.update(u2)
	assert repo.find_by_email("a@b.com") is None
	assert repo.find_by_username("ab") is None
	assert repo.find_by_email("c@d.com").id == u.id  # type: ignore[union-attr]
	assert repo.find_by_username("cd").id == u.id  # type: ignore[union-attr]


def test_profile_prefs_save_and_get():
	"""
	Test that the user profile and preferences repositories can save and retrieve profiles and preferences.
	"""
	p_repo = InMemoryUserProfileRepository()
	pr_repo = InMemoryUserPreferencesRepository()
	user_id = "u1"
	profile = UserProfile(
		user_id=user_id,
		first_name="A",
		last_name="B",
		date_of_birth=date.today(),
		gender=Gender.MALE,
		height_cm=180.0,
		current_weight_kg=80.0,
		activity_level=ActivityLevel.MODERATELY_ACTIVE,
		experience_level=ExperienceLevel.INTERMEDIATE,
	)
	p_repo.save(profile)
	assert p_repo.find_by_user_id(user_id) is not None

	prefs = UserPreferences(user_id=user_id)
	pr_repo.save(prefs)
	got = pr_repo.find_by_user_id(user_id)
	assert got is not None and got.user_id == user_id


def test_goal_memory_repos():
	"""
	Test that the fitness goal and user memory repositories can save and retrieve goals and memories.
	"""
	g_repo = InMemoryFitnessGoalRepository()
	m_repo = InMemoryUserMemoryRepository()
	user_id = "u1"
	goal = FitnessGoal(user_id=user_id, goal_category=GoalCategory.STRENGTH, goal_type="bench", priority_level=3)
	g_repo.save(goal)
	assert len(g_repo.list_by_user(user_id)) == 1

	# add memory and filter active
	mem = UserMemory(user_id=user_id, memory_type=MemoryType.PREFERENCE, content="note", source=MemorySource.USER_STATED)
	m_repo.save(mem)
	active = m_repo.list_active_by_user(user_id)
	assert len(active) == 1

