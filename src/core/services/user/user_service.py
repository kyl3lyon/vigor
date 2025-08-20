from dataclasses import replace
from datetime import datetime
from typing import Optional

from src.core.models import User
from src.core.repositories.protocols import UserRepository
from src.core.shared.errors import ValidationError, NotFoundError, ConflictError


class UserService:
	 def __init__(self, user_repo: UserRepository) -> None:
		 self._users = user_repo

	 def create_user(self, email: str, username: str, timezone: str = "UTC", preferred_language: str = "en") -> User:
		 if not email or "@" not in email:
			 raise ValidationError("email: invalid format")
		 existing_email = self._users.find_by_email(email)
		 if existing_email is not None:
			 raise ConflictError("email: already exists")
		 if not username:
			 raise ValidationError("username: required")
		 existing_username = self._users.find_by_username(username)
		 if existing_username is not None:
			 raise ConflictError("username: already exists")

		 user = User(email=email, username=username, timezone=timezone, preferred_language=preferred_language)
		 return self._users.save(user)

	 def activate_user(self, user_id: str) -> User:
		 user = self._require_user(user_id)
		 if user.is_active:
			 return user
		 updated = replace(user, is_active=True, updated_at=datetime.now())
		 return self._users.update(updated)

	 def deactivate_user(self, user_id: str) -> User:
		 user = self._require_user(user_id)
		 if not user.is_active:
			 return user
		 updated = replace(user, is_active=False, updated_at=datetime.now())
		 return self._users.update(updated)

	 def update_last_active(self, user_id: str) -> User:
		 user = self._require_user(user_id)
		 updated = replace(user, last_active_at=datetime.now(), updated_at=datetime.now())
		 return self._users.update(updated)

	 def update_identity(self, user_id: str, *, email: Optional[str] = None, username: Optional[str] = None) -> User:
		 user = self._require_user(user_id)
		 new_email = email if email is not None else user.email
		 new_username = username if username is not None else user.username
		 if new_email != user.email:
			 if not new_email or "@" not in new_email:
				 raise ValidationError("email: invalid format")
			 existing_email = self._users.find_by_email(new_email)
			 if existing_email is not None and existing_email.id != user.id:
				 raise ConflictError("email: already exists")
		 if new_username != user.username:
			 if not new_username:
				 raise ValidationError("username: required")
			 existing_username = self._users.find_by_username(new_username)
			 if existing_username is not None and existing_username.id != user.id:
				 raise ConflictError("username: already exists")

		 updated = replace(user, email=new_email, username=new_username, updated_at=datetime.now())
		 return self._users.update(updated)

	 def _require_user(self, user_id: str) -> User:
		 user = self._users.find_by_id(user_id)
		 if user is None:
			 raise NotFoundError("user: not found")
		 return user


