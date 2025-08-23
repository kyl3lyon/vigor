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
    TrainingSplit,
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
from src.infra.repositories.memory_planning import (
    InMemoryWorkoutTemplateRepository,
    InMemoryWorkoutExerciseTemplateRepository,
    InMemoryTrainingProgramRepository,
    InMemoryProgramPhaseRepository,
    InMemoryProgramEnrollmentRepository,
    InMemoryScheduledWorkoutRepository,
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
from src.core.services.planning.template_service import TemplateService
from src.core.services.planning.program_service import ProgramService
from src.core.services.planning.schedule_service import ScheduleService


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

    # Planning repos/services
    wt_repo = InMemoryWorkoutTemplateRepository()
    wet_repo = InMemoryWorkoutExerciseTemplateRepository()
    prog_repo = InMemoryTrainingProgramRepository()
    phase_repo = InMemoryProgramPhaseRepository()
    enroll_repo = InMemoryProgramEnrollmentRepository()
    sched_repo = InMemoryScheduledWorkoutRepository()

    # Services
    user_svc = UserService(user_repo)
    profile_svc = ProfileService(profile_repo, prefs_repo)
    goal_svc = GoalService(goal_repo)
    exercise_svc = ExerciseService(ex_repo)
    session_svc = SessionService(workout_repo, we_repo)
    tracking_svc = TrackingService(set_repo, we_repo, pr_repo)
    template_svc = TemplateService(wt_repo, wet_repo)
    program_svc = ProgramService(prog_repo, phase_repo, enroll_repo)
    schedule_svc = ScheduleService(sched_repo)

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

    print("== Set preferences (comprehensive) ==")
    # Base via service
    prefs = profile_svc.upsert_preferences(
        user.id,
        preferred_split=TrainingSplit.PUSH_PULL,
        sessions_per_week=5,
        session_duration_preference_minutes=75,
        workout_reminders=True,
        progress_updates=True,
        achievement_notifications=True,
    )
    # Enrich via repo to fill out optional list/str fields for demo completeness
    prefs = prefs_repo.update(
        type(prefs)(
            **{
                **prefs.__dict__,
                "workout_reminder_time": "07:00",
                "rest_day_preferences": ["Sat", "Sun"],
                "gym_location": "Downtown Strength",
                "available_equipment": ["barbell", "dumbbells", "cables", "smith_machine"],
                "exercise_dislikes": ["good_mornings"],
                "exercise_restrictions": ["overhead_press_due_to_shoulder_history"],
                "injury_notes": "Old left shoulder impingement; avoid aggressive overhead volume",
            }
        )
    )
    print(
        {
            "preferred_units": prefs.preferred_units.value,
            "preferred_split": getattr(prefs.preferred_split, "value", None),
            "sessions_per_week": prefs.sessions_per_week,
            "session_duration_min": prefs.session_duration_preference_minutes,
            "workout_reminders": prefs.workout_reminders,
            "workout_reminder_time": prefs.workout_reminder_time,
            "rest_days": prefs.rest_day_preferences,
            "gym_location": prefs.gym_location,
            "available_equipment": prefs.available_equipment,
            "exercise_dislikes": prefs.exercise_dislikes,
            "exercise_restrictions": prefs.exercise_restrictions,
            "injury_notes": prefs.injury_notes,
            "progress_updates": prefs.progress_updates,
            "achievement_notifications": prefs.achievement_notifications,
        }
    )

    print("== Create goal ==")
    goal = goal_svc.create_goal(
        user_id=user.id,
        goal_category=GoalCategory.STRENGTH,
        goal_type="bench_100kg",
        priority_level=4,
        description="Bench 100kg",
    )
    print({"goal_id": goal.id, "goal_type": goal.goal_type, "priority": goal.priority_level})

    print("== Define exercises (Push & Pull) ==")
    # Push day
    bench = exercise_svc.create_definition(
        name="Barbell Bench Press",
        primary_muscles=[MuscleGroup.CHEST],
        equipment=EquipmentType.BARBELL,
        mechanics=MechanicsType.COMPOUND,
        movement_pattern=MovementPattern.HORIZONTAL_PRESS,
    )
    ohp = exercise_svc.create_definition(
        name="Overhead Press",
        primary_muscles=[MuscleGroup.SHOULDERS],
        equipment=EquipmentType.BARBELL,
        mechanics=MechanicsType.COMPOUND,
        movement_pattern=MovementPattern.VERTICAL_PRESS,
    )
    incline_db = exercise_svc.create_definition(
        name="Incline Dumbbell Press",
        primary_muscles=[MuscleGroup.CHEST],
        equipment=EquipmentType.DUMBBELL,
        mechanics=MechanicsType.COMPOUND,
        movement_pattern=MovementPattern.HORIZONTAL_PRESS,
    )
    cable_fly = exercise_svc.create_definition(
        name="Cable Fly",
        primary_muscles=[MuscleGroup.CHEST],
        equipment=EquipmentType.CABLE,
        mechanics=MechanicsType.ISOLATION,
        movement_pattern=MovementPattern.HORIZONTAL_PRESS,
    )
    triceps_pd = exercise_svc.create_definition(
        name="Triceps Pushdown",
        primary_muscles=[MuscleGroup.TRICEPS],
        equipment=EquipmentType.CABLE,
        mechanics=MechanicsType.ISOLATION,
        movement_pattern=MovementPattern.OTHER,
    )
    # Pull day
    pullup = exercise_svc.create_definition(
        name="Pull-Up",
        primary_muscles=[MuscleGroup.LATS],
        equipment=EquipmentType.BODYWEIGHT,
        mechanics=MechanicsType.COMPOUND,
        movement_pattern=MovementPattern.VERTICAL_PULL,
    )
    barbell_row = exercise_svc.create_definition(
        name="Barbell Row",
        primary_muscles=[MuscleGroup.BACK],
        equipment=EquipmentType.BARBELL,
        mechanics=MechanicsType.COMPOUND,
        movement_pattern=MovementPattern.HORIZONTAL_PULL,
    )
    lat_pulldown = exercise_svc.create_definition(
        name="Lat Pulldown",
        primary_muscles=[MuscleGroup.LATS],
        equipment=EquipmentType.CABLE,
        mechanics=MechanicsType.COMPOUND,
        movement_pattern=MovementPattern.VERTICAL_PULL,
    )
    face_pull = exercise_svc.create_definition(
        name="Face Pull",
        primary_muscles=[MuscleGroup.TRAPS],
        equipment=EquipmentType.CABLE,
        mechanics=MechanicsType.ISOLATION,
        movement_pattern=MovementPattern.HORIZONTAL_PULL,
    )
    db_curl = exercise_svc.create_definition(
        name="Dumbbell Curl",
        primary_muscles=[MuscleGroup.BICEPS],
        equipment=EquipmentType.DUMBBELL,
        mechanics=MechanicsType.ISOLATION,
        movement_pattern=MovementPattern.OTHER,
    )
    print({
        "push_exercises": [bench.name, ohp.name, incline_db.name, cable_fly.name, triceps_pd.name],
        "pull_exercises": [pullup.name, barbell_row.name, lat_pulldown.name, face_pull.name, db_curl.name],
    })

    print("== Push Day: start, add exercises, log sets ==")
    w_push = session_svc.start_workout(user_id=user.id, title="Push Day")
    wes_push = []
    for idx, ex in enumerate([bench, ohp, incline_db, cable_fly, triceps_pd]):
        wes_push.append(session_svc.add_exercise(workout_id=w_push.id, exercise_id=ex.id, order_index=idx))
    set_plan_push = {
        bench.id: [(60.0, 8, 6.5), (70.0, 5, 8.0), (80.0, 3, 9.0)],
        ohp.id: [(40.0, 8, 7.0), (45.0, 6, 8.0), (50.0, 4, 9.0)],
        incline_db.id: [(24.0, 10, 7.0), (26.0, 8, 8.0), (28.0, 6, 9.0)],
        cable_fly.id: [(20.0, 12, 6.5), (22.5, 10, 7.5), (25.0, 8, 8.5)],
        triceps_pd.id: [(25.0, 12, 7.0), (30.0, 10, 8.0), (35.0, 8, 9.0)],
    }
    for we in wes_push:
        for i, (wt, reps, rpe) in enumerate(set_plan_push.get(we.exercise_id, []), start=1):
            tracking_svc.log_set(we.id, set_number=i, weight_kg=wt, reps=reps, rpe=rpe)
    push_sets_all = []
    we_map_push = {}
    ex_map_push = {ex.id: ex for ex in [bench, ohp, incline_db, cable_fly, triceps_pd]}
    for we in wes_push:
        we_map_push[we.id] = we
        push_sets_all.extend(set_repo.list_for_workout_exercise(we.id))
    v_total_push = total_volume_kg(push_sets_all)
    v_mg_push = volume_by_muscle_group(push_sets_all, we_map_push, ex_map_push)
    v_mp_push = volume_by_movement_pattern(push_sets_all, we_map_push, ex_map_push)
    pr_bench = tracking_svc.evaluate_prs(user_id=user.id, exercise_id=bench.id, weight_kg=80.0, reps=3, achieved_at=datetime.now())
    print({
        "workout": "Push Day",
        "total_volume_kg": v_total_push,
        "volume_by_muscle": {k.value: v for k, v in v_mg_push.items()},
        "volume_by_movement": {k.value: v for k, v in v_mp_push.items()},
        "bench_pr_weight_kg": getattr(pr_bench, "weight_kg", None),
    })
    w_push_done = session_svc.complete_workout(w_push.id, session_rpe=8.0, duration_seconds=4000)
    print({"push_completed_at": w_push_done.completed_at.isoformat() if w_push_done.completed_at else None})

    print("== Pull Day: start, add exercises, log sets ==")
    w_pull = session_svc.start_workout(user_id=user.id, title="Pull Day")
    wes_pull = []
    for idx, ex in enumerate([pullup, barbell_row, lat_pulldown, face_pull, db_curl]):
        wes_pull.append(session_svc.add_exercise(workout_id=w_pull.id, exercise_id=ex.id, order_index=idx))
    set_plan_pull = {
        pullup.id: [(5.0, 6, 8.5), (2.5, 6, 8.0), (0.0, 8, 8.0)],
        barbell_row.id: [(60.0, 8, 7.5), (70.0, 6, 8.5), (75.0, 5, 9.0)],
        lat_pulldown.id: [(45.0, 10, 7.0), (50.0, 8, 8.0), (55.0, 6, 9.0)],
        face_pull.id: [(20.0, 15, 6.5), (22.5, 12, 7.0), (25.0, 10, 8.0)],
        db_curl.id: [(14.0, 12, 7.0), (16.0, 10, 8.0), (18.0, 8, 9.0)],
    }
    for we in wes_pull:
        for i, (wt, reps, rpe) in enumerate(set_plan_pull.get(we.exercise_id, []), start=1):
            tracking_svc.log_set(we.id, set_number=i, weight_kg=wt, reps=reps, rpe=rpe)
    pull_sets_all = []
    we_map_pull = {}
    ex_map_pull = {ex.id: ex for ex in [pullup, barbell_row, lat_pulldown, face_pull, db_curl]}
    for we in wes_pull:
        we_map_pull[we.id] = we
        pull_sets_all.extend(set_repo.list_for_workout_exercise(we.id))
    v_total_pull = total_volume_kg(pull_sets_all)
    v_mg_pull = volume_by_muscle_group(pull_sets_all, we_map_pull, ex_map_pull)
    v_mp_pull = volume_by_movement_pattern(pull_sets_all, we_map_pull, ex_map_pull)
    pr_row = tracking_svc.evaluate_prs(user_id=user.id, exercise_id=barbell_row.id, weight_kg=75.0, reps=5, achieved_at=datetime.now())
    print({
        "workout": "Pull Day",
        "total_volume_kg": v_total_pull,
        "volume_by_muscle": {k.value: v for k, v in v_mg_pull.items()},
        "volume_by_movement": {k.value: v for k, v in v_mp_pull.items()},
        "row_pr_weight_kg": getattr(pr_row, "weight_kg", None),
    })
    w_pull_done = session_svc.complete_workout(w_pull.id, session_rpe=8.0, duration_seconds=4200)
    print({"pull_completed_at": w_pull_done.completed_at.isoformat() if w_pull_done.completed_at else None})

    print("== Scheduling preview: template/program/schedule linkage ==")
    # Create a simple push template and an exercise template target
    t_push = template_svc.create_template(name="Push Template", description="Press emphasis", estimated_duration_minutes=75)
    template_svc.add_exercise_template(
        workout_template_id=t_push.id,
        exercise_id=bench.id,
        order_index=0,
        target_sets=3,
        target_reps_min=5,
        target_reps_max=8,
        target_rpe=8.0,
        rest_seconds_between_sets=180,
    )
    # Create a program with two phases and enroll the user
    prog = program_svc.create_program(name="Push/Pull Intro", description="Base + Deload", duration_weeks=6)
    base = program_svc.add_phase(program_id=prog.id, name="Base", order_index=0, start_week=1, end_week=4)
    deload = program_svc.add_phase(program_id=prog.id, name="Deload", order_index=1, start_week=5, end_week=6, is_deload=True, deload_percentage=0.6)
    enrollment = program_svc.enroll(user_id=user.id, program_id=prog.id, start_date=date.today())
    # Schedule next week's push workout and then link it to the completed workout
    next_week = date.today().replace(day=date.today().day)  # keep same day-of-month
    sched = schedule_svc.schedule_workout(user_id=user.id, scheduled_date=next_week, template_id=t_push.id, program_enrollment_id=enrollment.id, program_phase_id=base.id, priority=3)
    print({"scheduled": {"id": sched.id, "date": sched.scheduled_date.isoformat(), "template": t_push.name}})
    # Mark scheduled workout as completed using the actual push workout id
    sched_done = schedule_svc.mark_completed(sched.id, actual_workout_id=w_push_done.id)
    print({"scheduled_completed_linked_workout": sched_done.actual_workout_id})


if __name__ == "__main__":
    main()
