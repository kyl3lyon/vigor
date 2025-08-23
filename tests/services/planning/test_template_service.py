from src.infra.repositories.memory_planning import (
	 InMemoryWorkoutTemplateRepository,
	 InMemoryWorkoutExerciseTemplateRepository,
)
from src.core.services.planning.template_service import TemplateService
from src.core.shared.errors import ValidationError


def test_create_template_and_add_exercise_templates():
	 t_repo = InMemoryWorkoutTemplateRepository()
	 wet_repo = InMemoryWorkoutExerciseTemplateRepository()
	 svc = TemplateService(t_repo, wet_repo)
	 t = svc.create_template(name="Push Day", description="Pressing")
	 assert t_repo.get_by_id(t.id) is not None
	 # invalid duration
	 try:
		 svc.create_template(name="X", estimated_duration_minutes=-1)
		 assert False, "expected ValidationError for negative duration"
	 except ValidationError:
		 pass
	 # add exercise templates
	 wet1 = svc.add_exercise_template(
		 workout_template_id=t.id,
		 exercise_id="ex1",
		 order_index=0,
		 target_sets=3,
		 target_reps_min=5,
		 target_reps_max=8,
		 target_rpe=8.0,
		 rest_seconds_between_sets=180,
	 )
	 # duplicate order index rejected
	 try:
		 svc.add_exercise_template(
			 workout_template_id=t.id,
			 exercise_id="ex2",
			 order_index=0,
		 )
		 assert False, "expected ValidationError for duplicate order_index"
	 except ValidationError:
		 pass
	 items = svc.list_exercise_templates(t.id)
	 assert len(items) == 1 and items[0].id == wet1.id


