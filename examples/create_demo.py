"""Create two small SQLite databases with intentional schema drift."""
import sqlite3
from pathlib import Path

root = Path(__file__).parent
for name in ("before.db", "after.db"):
    (root / name).unlink(missing_ok=True)
with sqlite3.connect(root / "before.db") as db:
    db.executescript("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE INDEX ix_users_name ON users(name);")
with sqlite3.connect(root / "after.db") as db:
    db.executescript("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE); CREATE TABLE audit(id INTEGER PRIMARY KEY, event TEXT NOT NULL);")
print("Created examples/before.db and examples/after.db")
