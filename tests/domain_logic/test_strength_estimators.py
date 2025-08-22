from math import isclose

from src.core.domain_logic.strength_estimators import (
	 epley_estimate_1rm,
	 brzycki_estimate_1rm,
	 blended_1rm_estimate,
)


def test_epley_estimate_valid():
	 result = epley_estimate_1rm(100.0, 5)
	 assert result is not None
	 assert isclose(result, 116.6666667, rel_tol=1e-5)


def test_brzycki_estimate_valid():
	 result = brzycki_estimate_1rm(100.0, 5)
	 assert result is not None
	 assert isclose(result, 112.5, rel_tol=1e-5)


def test_blended_estimate_valid():
	 result = blended_1rm_estimate(100.0, 5)
	 assert result is not None
	 # Average of ~116.6667 and 112.5 = ~114.5833
	 assert isclose(result, 114.5833333, rel_tol=1e-5)


def test_estimators_invalid_inputs():
	 assert epley_estimate_1rm(-10.0, 5) is None
	 assert epley_estimate_1rm(100.0, 0) is None
	 assert brzycki_estimate_1rm(100.0, 0) is None
	 assert brzycki_estimate_1rm(100.0, 37) is None
	 # blended returns None if both invalid
	 assert blended_1rm_estimate(-10.0, 0) is None

