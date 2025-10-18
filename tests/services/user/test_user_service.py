from datetime import datetime

from src.infra.repositories.memory_user import InMemoryUserRepository
from src.core.services.user.user_service import UserService
from src.core.shared.errors import ValidationError, ConflictError


def test_create_user_success_and_uniqueness():
	"""
	Validates user creation logic for uniqueness constraints.

	Verifies:
	- Creation of a user with a unique email and username is successful.
	- Attempting to create a user with a duplicate email raises ConflictError.
	- Attempting to create a user with a duplicate username raises ConflictError.

	Repository state and user identity are checked after each operation.
	"""
	repo = InMemoryUserRepository()
	svc = UserService(repo)
	u = svc.create_user(email="a@b.com", username="alpha")
	assert repo.find_by_email("a@b.com").id == u.id  # type: ignore[union-attr]
	assert repo.find_by_username("alpha").id == u.id  # type: ignore[union-attr]
	# duplicate email
	try:
		svc.create_user(email="a@b.com", username="beta")
		assert False, "expected ConflictError for duplicate email"
	except ConflictError:
		pass
	# duplicate username
	try:
		svc.create_user(email="b@b.com", username="alpha")
		assert False, "expected ConflictError for duplicate username"
	except ConflictError:
		pass


def test_create_user_invalid_email():
	"""
	Ensures email format validation during user creation.

	Verifies:
	- Creating a user with an invalid email format raises ValidationError.
	"""
	repo = InMemoryUserRepository()
	svc = UserService(repo)
	try:
		svc.create_user(email="bad-email", username="x")
		assert False, "expected ValidationError for invalid email"
	except ValidationError:
		pass


def test_activate_deactivate_and_last_active():
	"""
	Verifies user activation, deactivation, idempotency of deactivation, re-activation, and last active timestamp update.

	- Ensures a newly created user is active.
	- Deactivation sets is_active to False.
	- Repeated deactivation remains idempotent (is_active stays False).
	- Activation sets is_active to True.
	- Updating last active timestamp results in a non-decreasing value.
	"""
	repo = InMemoryUserRepository()
	svc = UserService(repo)
	u = svc.create_user(email="a@b.com", username="alpha")
	assert u.is_active is True
	# deactivate
	u = svc.deactivate_user(u.id)
	assert u.is_active is False
	# idempotent deactivate
	u2 = svc.deactivate_user(u.id)
	assert u2.is_active is False
	# activate
	u3 = svc.activate_user(u.id)
	assert u3.is_active is True
	# last active update
	before = u3.last_active_at
	u4 = svc.update_last_active(u3.id)
	assert u4.last_active_at >= before


def test_update_identity_validates_and_checks_uniqueness():
	"""
	Validates user identity update logic for email and username.

	- Ensures invalid email format raises ValidationError.
	- Ensures updating to an email already in use by another user raises ConflictError.
	- Ensures successful update changes both email and username, and repository reflects the changes.
	"""
	repo = InMemoryUserRepository()
	svc = UserService(repo)
	a = svc.create_user(email="a@b.com", username="alpha")
	b = svc.create_user(email="b@b.com", username="beta")
	# invalid email format
	try:
		svc.update_identity(a.id, email="bad-email")
		assert False, "expected ValidationError"
	except ValidationError:
		pass
	# conflict with another user's email
	try:
		svc.update_identity(a.id, email=b.email)
		assert False, "expected ConflictError"
	except ConflictError:
		pass
	# success change
	a2 = svc.update_identity(a.id, email="c@d.com", username="charlie")
	assert repo.find_by_email("c@d.com").id == a.id  # type: ignore[union-attr]
	assert repo.find_by_username("charlie").id == a.id  # type: ignore[union-attr]


