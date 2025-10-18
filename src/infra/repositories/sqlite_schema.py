SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
	id TEXT PRIMARY KEY,
	email TEXT UNIQUE NOT NULL,
	username TEXT UNIQUE NOT NULL,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	last_active_at TEXT NOT NULL,
	is_active INTEGER NOT NULL DEFAULT 1,
	timezone TEXT NOT NULL DEFAULT 'UTC',
	preferred_language TEXT NOT NULL DEFAULT 'en'
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE TABLE IF NOT EXISTS user_profiles (
	user_id TEXT PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT,
	date_of_birth TEXT NOT NULL,
	gender TEXT NOT NULL,
	height_cm REAL NOT NULL,
	current_weight_kg REAL NOT NULL,
	activity_level TEXT NOT NULL,
	experience_level TEXT NOT NULL,
	years_training REAL,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
	user_id TEXT PRIMARY KEY,
	preferred_units TEXT NOT NULL DEFAULT 'metric',
	workout_reminders INTEGER NOT NULL DEFAULT 1,
	workout_reminder_time TEXT,
	rest_day_preferences TEXT,
	gym_location TEXT,
	available_equipment TEXT,
	exercise_dislikes TEXT,
	exercise_restrictions TEXT,
	injury_notes TEXT,
	coaching_personality TEXT,
	preferred_split TEXT,
	sessions_per_week INTEGER,
	session_duration_preference_minutes INTEGER,
	progress_updates INTEGER NOT NULL DEFAULT 1,
	achievement_notifications INTEGER NOT NULL DEFAULT 1,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS fitness_goals (
	id TEXT PRIMARY KEY,
	user_id TEXT NOT NULL,
	goal_category TEXT NOT NULL,
	goal_type TEXT NOT NULL,
	description TEXT,
	target_value REAL,
	current_value REAL,
	target_date TEXT,
	priority_level INTEGER NOT NULL,
	is_achieved INTEGER NOT NULL DEFAULT 0,
	achieved_at TEXT,
	progress_percentage REAL NOT NULL DEFAULT 0.0,
	why_important TEXT,
	obstacles TEXT,
	is_active INTEGER NOT NULL DEFAULT 1,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_goals_user ON fitness_goals(user_id);

CREATE TABLE IF NOT EXISTS user_memories (
	id TEXT PRIMARY KEY,
	user_id TEXT NOT NULL,
	memory_type TEXT NOT NULL,
	content TEXT NOT NULL,
	confidence REAL NOT NULL DEFAULT 0.0,
	source TEXT NOT NULL,
	relevance_score REAL NOT NULL DEFAULT 0.0,
	related_exercises TEXT,
	related_muscle_groups TEXT,
	is_active INTEGER NOT NULL DEFAULT 1,
	expires_at TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_memories_user ON user_memories(user_id);

CREATE TABLE IF NOT EXISTS exercise_definitions (
	id TEXT PRIMARY KEY,
	name TEXT NOT NULL,
	primary_muscles TEXT NOT NULL,
	equipment TEXT NOT NULL,
	mechanics TEXT NOT NULL,
	movement_pattern TEXT NOT NULL,
	secondary_muscles TEXT,
	aliases TEXT,
	is_unilateral INTEGER NOT NULL DEFAULT 0,
	default_unit TEXT NOT NULL DEFAULT 'metric',
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ex_name ON exercise_definitions(name);

CREATE TABLE IF NOT EXISTS workouts (
	id TEXT PRIMARY KEY,
	user_id TEXT NOT NULL,
	title TEXT,
	notes TEXT,
	status TEXT NOT NULL DEFAULT 'planned',
	session_rpe REAL,
	duration_seconds INTEGER,
	started_at TEXT,
	completed_at TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_workouts_user ON workouts(user_id);

CREATE TABLE IF NOT EXISTS workout_exercises (
	id TEXT PRIMARY KEY,
	workout_id TEXT NOT NULL,
	exercise_id TEXT NOT NULL,
	order_index INTEGER NOT NULL,
	notes TEXT,
	target_reps INTEGER,
	target_rpe REAL,
	rest_seconds_between_sets INTEGER,
	tempo TEXT,
	superset_group_id TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (workout_id) REFERENCES workouts(id),
	FOREIGN KEY (exercise_id) REFERENCES exercise_definitions(id)
);

CREATE INDEX IF NOT EXISTS idx_we_workout ON workout_exercises(workout_id);

CREATE TABLE IF NOT EXISTS exercise_sets (
	id TEXT PRIMARY KEY,
	workout_exercise_id TEXT NOT NULL,
	set_number INTEGER NOT NULL,
	load_type TEXT NOT NULL,
	weight_kg REAL,
	bodyweight_kg REAL,
	assistance_kg REAL,
	reps INTEGER,
	time_seconds INTEGER,
	distance_meters REAL,
	rpe REAL,
	rir REAL,
	tempo TEXT,
	is_warmup INTEGER NOT NULL DEFAULT 0,
	is_failure INTEGER NOT NULL DEFAULT 0,
	rest_seconds_after INTEGER,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises(id)
);

CREATE INDEX IF NOT EXISTS idx_sets_we ON exercise_sets(workout_exercise_id);

CREATE TABLE IF NOT EXISTS personal_records (
	id TEXT PRIMARY KEY,
	user_id TEXT NOT NULL,
	exercise_id TEXT NOT NULL,
	record_type TEXT NOT NULL,
	achieved_at TEXT NOT NULL,
	weight_kg REAL,
	reps INTEGER,
	time_seconds INTEGER,
	distance_meters REAL,
	notes TEXT,
	source TEXT NOT NULL DEFAULT 'computed',
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (exercise_id) REFERENCES exercise_definitions(id)
);

CREATE INDEX IF NOT EXISTS idx_prs_user_ex ON personal_records(user_id, exercise_id);

CREATE TABLE IF NOT EXISTS workout_templates (
	id TEXT PRIMARY KEY,
	name TEXT NOT NULL,
	description TEXT,
	estimated_duration_minutes INTEGER,
	difficulty_level TEXT NOT NULL DEFAULT 'beginner',
	goal TEXT NOT NULL DEFAULT 'strength',
	target_muscle_groups TEXT,
	target_movement_patterns TEXT,
	exercise_templates TEXT,
	author_user_id TEXT,
	is_public INTEGER NOT NULL DEFAULT 0,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workout_exercise_templates (
	id TEXT PRIMARY KEY,
	workout_template_id TEXT NOT NULL,
	exercise_id TEXT NOT NULL,
	order_index INTEGER NOT NULL,
	target_sets INTEGER,
	target_reps_min INTEGER,
	target_reps_max INTEGER,
	target_rpe REAL,
	target_intensity_pct_1rm REAL,
	rest_seconds_between_sets INTEGER,
	tempo TEXT,
	notes TEXT,
	superset_group_id TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (workout_template_id) REFERENCES workout_templates(id),
	FOREIGN KEY (exercise_id) REFERENCES exercise_definitions(id)
);

CREATE INDEX IF NOT EXISTS idx_wet_template ON workout_exercise_templates(workout_template_id);

CREATE TABLE IF NOT EXISTS training_programs (
	id TEXT PRIMARY KEY,
	name TEXT NOT NULL,
	description TEXT,
	duration_weeks INTEGER,
	difficulty_level TEXT NOT NULL DEFAULT 'beginner',
	goal TEXT NOT NULL DEFAULT 'strength',
	phase_ids TEXT,
	progression_rules TEXT,
	tags TEXT,
	author_user_id TEXT,
	is_public INTEGER NOT NULL DEFAULT 0,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS program_phases (
	id TEXT PRIMARY KEY,
	program_id TEXT NOT NULL,
	name TEXT NOT NULL,
	order_index INTEGER NOT NULL,
	start_week INTEGER,
	end_week INTEGER,
	workout_template_ids TEXT,
	autoregulation TEXT NOT NULL DEFAULT 'none',
	is_deload INTEGER NOT NULL DEFAULT 0,
	deload_percentage REAL,
	notes TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (program_id) REFERENCES training_programs(id)
);

CREATE INDEX IF NOT EXISTS idx_phase_program ON program_phases(program_id);

CREATE TABLE IF NOT EXISTS program_enrollments (
	id TEXT PRIMARY KEY,
	user_id TEXT NOT NULL,
	program_id TEXT NOT NULL,
	start_date TEXT NOT NULL,
	current_phase_id TEXT,
	progress_week INTEGER,
	is_active INTEGER NOT NULL DEFAULT 1,
	notes TEXT,
	ended_at TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (program_id) REFERENCES training_programs(id)
);

CREATE INDEX IF NOT EXISTS idx_enroll_user ON program_enrollments(user_id);

CREATE TABLE IF NOT EXISTS scheduled_workouts (
	id TEXT PRIMARY KEY,
	user_id TEXT NOT NULL,
	scheduled_date TEXT NOT NULL,
	template_id TEXT,
	program_enrollment_id TEXT,
	program_phase_id TEXT,
	actual_workout_id TEXT,
	status TEXT NOT NULL DEFAULT 'planned',
	priority INTEGER NOT NULL DEFAULT 3,
	notes TEXT,
	auto_generated INTEGER NOT NULL DEFAULT 1,
	reschedule_count INTEGER NOT NULL DEFAULT 0,
	recurrence TEXT NOT NULL DEFAULT 'none',
	recurrence_pattern TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (template_id) REFERENCES workout_templates(id),
	FOREIGN KEY (actual_workout_id) REFERENCES workouts(id)
);

CREATE INDEX IF NOT EXISTS idx_sched_user_date ON scheduled_workouts(user_id, scheduled_date);
"""

