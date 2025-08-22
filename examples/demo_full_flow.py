from datetime import datetime, date

from src.core.models import (
    EquipmentType,
    MuscleGroup,
    MechanicsType,
    MovementPattern,
    GoalCategory,
    ActivityLevel,
    ExperienceLevel,
    Gender,
)
from src.infra.repositories.memory_user import (
    InMemoryUserRepository,
    InMemoryUserProfileRepository,
    InMemoryUserPreferencesRepository,
    InMemoryFitnessGoalRepository,
)
from src.infra.repositories.memory_workout import (
    InMemoryExerciseDefinitionRepository,
    InMemoryWorkoutRepository,
    InMemoryWorkoutExerciseRepository,
    InMemoryExerciseSetRepository,
    InMemoryPersonalRecordRepository,
)
from src.core.services.user.user_service import UserService
from src.core.services.user.profile_service import ProfileService
from src.core.services.user.goal_service import GoalService
from src.core.services.workout.exercise_service import ExerciseService
from src.core.services.workout.session_service import SessionService
from src.core.services.workout.tracking_service import TrackingService
from src.core.domain_logic.volume_aggregators import (
    total_volume_kg,
    volume_by_muscle_group,
    volume_by_movement_pattern,
)


def main() -> None:
    # Repositories
    user_repo = InMemoryUserRepository()
    profile_repo = InMemoryUserProfileRepository()
    prefs_repo = InMemoryUserPreferencesRepository()
    goal_repo = InMemoryFitnessGoalRepository()

    ex_repo = InMemoryExerciseDefinitionRepository()
    workout_repo = InMemoryWorkoutRepository()
    we_repo = InMemoryWorkoutExerciseRepository()
    set_repo = InMemoryExerciseSetRepository()
    pr_repo = InMemoryPersonalRecordRepository()

    # Services
    user_svc = UserService(user_repo)
    profile_svc = ProfileService(profile_repo, prefs_repo)
    goal_svc = GoalService(goal_repo)
    exercise_svc = ExerciseService(ex_repo)
    session_svc = SessionService(workout_repo, we_repo)
    tracking_svc = TrackingService(set_repo, we_repo, pr_repo)

    print("== Create user ==")
    user = user_svc.create_user(email="demo@example.com", username="demo")
    print({"user_id": user.id, "email": user.email, "username": user.username})

    print("== Create profile ==")
    profile = profile_svc.upsert_profile(
        user_id=user.id,
        first_name="Casey",
        last_name="L.",
        height_cm=178.0,
        current_weight_kg=80.0,
        date_of_birth=date(1995, 5, 17),
        gender=Gender.MALE,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        experience_level=ExperienceLevel.INTERMEDIATE,
    )
    print({"height_cm": profile.height_cm, "weight_kg": profile.current_weight_kg})

    print("== Set preferences ==")
    prefs = profile_svc.upsert_preferences(user.id, sessions_per_week=4)
    print({"sessions_per_week": prefs.sessions_per_week})

    print("== Create goal ==")
    goal = goal_svc.create_goal(
        user_id=user.id,
        goal_category=GoalCategory.STRENGTH,
        goal_type="bench_100kg",
        priority_level=4,
        description="Bench 100kg",
    )
    print({"goal_id": goal.id, "goal_type": goal.goal_type, "priority": goal.priority_level})

    print("== Define exercise ==")
    bench = exercise_svc.create_definition(
        name="Barbell Bench Press",
        primary_muscles=[MuscleGroup.CHEST],
        equipment=EquipmentType.BARBELL,
        mechanics=MechanicsType.COMPOUND,
        movement_pattern=MovementPattern.HORIZONTAL_PRESS,
    )
    print({"exercise_id": bench.id, "name": bench.name})

    print("== Start workout ==")
    w = session_svc.start_workout(user_id=user.id, title="Upper Body")
    print({"workout_id": w.id, "started_at": w.started_at.isoformat() if w.started_at else None})

    print("== Add exercise to workout ==")
    we = session_svc.add_exercise(workout_id=w.id, exercise_id=bench.id, order_index=0)
    print({"workout_exercise_id": we.id, "exercise_id": we.exercise_id})

    print("== Log sets ==")
    tracking_svc.log_set(we.id, set_number=1, weight_kg=60.0, reps=8, rpe=6.5)
    tracking_svc.log_set(we.id, set_number=2, weight_kg=70.0, reps=5, rpe=8.0)
    tracking_svc.log_set(we.id, set_number=3, weight_kg=80.0, reps=3, rpe=9.0)

    sets = set_repo.list_for_workout_exercise(we.id)
    print({"sets_logged": len(sets)})

    print("== Volume and PR ==")
    v_total = total_volume_kg(sets)
    v_mg = volume_by_muscle_group(sets, {we.id: we}, {bench.id: bench})
    v_mp = volume_by_movement_pattern(sets, {we.id: we}, {bench.id: bench})
    pr = tracking_svc.evaluate_prs(user_id=user.id, exercise_id=bench.id, weight_kg=80.0, reps=3, achieved_at=datetime.now())
    print({"total_volume_kg": v_total, "volume_by_muscle": {k.value: v for k, v in v_mg.items()}, "volume_by_movement": {k.value: v for k, v in v_mp.items()}, "pr_weight_kg": getattr(pr, "weight_kg", None)})

    print("== Complete workout ==")
    w2 = session_svc.complete_workout(w.id, session_rpe=8.5, duration_seconds=3600)
    print({"completed_at": w2.completed_at.isoformat() if w2.completed_at else None, "session_rpe": w2.session_rpe, "duration_seconds": w2.duration_seconds})


if __name__ == "__main__":
    main()


