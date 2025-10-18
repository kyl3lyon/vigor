from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_api_user_profile_workout_flow():
	resp = client.post("/api/users", json={"email": "api@test.com", "username": "apitest"})
	assert resp.status_code == 200
	user_id = resp.json()["user_id"]

	resp = client.post(
		f"/api/users/{user_id}/profile",
		json={
			"first_name": "A",
			"height_cm": 180.0,
			"current_weight_kg": 80.0,
			"date_of_birth": "1990-01-01",
			"gender": "male",
			"activity_level": "moderately_active",
			"experience_level": "intermediate",
		},
	)
	assert resp.status_code == 200

	resp = client.post("/api/exercises", json={
		"name": "Bench",
		"primary_muscles": ["chest"],
		"equipment": "barbell",
		"mechanics": "compound",
		"movement_pattern": "horizontal_press",
	})
	assert resp.status_code == 200
	ex_id = resp.json()["exercise_id"]

	resp = client.post("/api/workouts", json={"user_id": user_id, "title": "Test"})
	assert resp.status_code == 200
	workout_id = resp.json()["workout_id"]

	resp = client.post(f"/api/workouts/{workout_id}/exercises", json={"exercise_id": ex_id, "order_index": 0})
	assert resp.status_code == 200
	we_id = resp.json()["workout_exercise_id"]

	resp = client.post(f"/api/workouts/{workout_id}/exercises/{we_id}/sets", json={"set_number": 1, "weight_kg": 80.0, "reps": 5})
	if resp.status_code != 200:
		print(f"Error response: {resp.json()}")
	assert resp.status_code == 200

	resp = client.post(f"/api/workouts/{workout_id}/complete", json={"session_rpe": 8.0})
	assert resp.status_code == 200
	assert resp.json()["total_volume_kg"] > 0

	resp = client.get(f"/api/users/{user_id}/analytics/volume?period_days=7")
	assert resp.status_code == 200
	assert resp.json()["total_volume_kg"] > 0

