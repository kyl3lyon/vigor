import tempfile
import os

from src.infra.repositories.sqlite_connection import init_db, get_connection
from src.infra.repositories.sqlite_user import SQLiteUserRepository
from src.core.models import User


def test_sqlite_user_save_and_find():
	with tempfile.TemporaryDirectory() as tmpdir:
		db_path = os.path.join(tmpdir, "test.db")
		init_db(db_path)
		conn = get_connection(db_path)
		repo = SQLiteUserRepository(conn)

		u = User(email="a@b.com", username="alpha")
		repo.save(u)
		found = repo.find_by_email("a@b.com")
		assert found is not None and found.id == u.id
		found_un = repo.find_by_username("alpha")
		assert found_un is not None and found_un.id == u.id

		conn.close()

