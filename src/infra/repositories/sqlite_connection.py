import sqlite3
from pathlib import Path

from src.infra.repositories.sqlite_schema import SCHEMA_SQL


def get_connection(db_path: str = "vigor.db") -> sqlite3.Connection:
	conn = sqlite3.connect(db_path, check_same_thread=False)
	conn.row_factory = sqlite3.Row
	return conn


def init_db(db_path: str = "vigor.db") -> None:
	conn = get_connection(db_path)
	conn.executescript(SCHEMA_SQL)
	conn.commit()
	conn.close()

