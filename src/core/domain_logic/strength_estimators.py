from typing import Optional


def epley_estimate_1rm(weight_kg: float, reps: int) -> Optional[float]:
	 if weight_kg <= 0 or reps <= 0:
		 return None
	 return weight_kg * (1.0 + reps / 30.0)


def brzycki_estimate_1rm(weight_kg: float, reps: int) -> Optional[float]:
	 if weight_kg <= 0 or reps <= 0 or reps >= 37:
		 return None
	 return weight_kg * (36.0 / (37.0 - reps))


def blended_1rm_estimate(weight_kg: float, reps: int) -> Optional[float]:
	 e = epley_estimate_1rm(weight_kg, reps)
	 b = brzycki_estimate_1rm(weight_kg, reps)
	 if e is None and b is None:
		 return None
	 if e is None:
		 return b
	 if b is None:
		 return e
	 return (e + b) / 2.0


