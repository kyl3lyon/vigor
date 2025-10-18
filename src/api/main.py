from fastapi import FastAPI

from src.api.routers import users, goals, exercises, workouts, planning, analytics

app = FastAPI(title="Vigor API", version="0.1.0")

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(goals.router, prefix="/api", tags=["goals"])
app.include_router(exercises.router, prefix="/api", tags=["exercises"])
app.include_router(workouts.router, prefix="/api", tags=["workouts"])
app.include_router(planning.router, prefix="/api", tags=["planning"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])


@app.get("/health")
def health():
	return {"status": "ok"}

