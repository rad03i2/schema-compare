import sqlite3

import pytest

from schema_compare.core import SchemaError, compare_databases, inspect_database


def make_db(path, sql):
    with sqlite3.connect(path) as conn:
        conn.executescript(sql)


def test_identical_schemas(tmp_path):
    a, b = tmp_path / "a.db", tmp_path / "b.db"
    sql = "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL); CREATE INDEX ix_name ON users(name);"
    make_db(a, sql); make_db(b, sql)
    diff = compare_databases(a, b)
    assert diff["different"] is False


def test_detects_table_column_and_index_drift(tmp_path):
    a, b = tmp_path / "a.db", tmp_path / "b.db"
    make_db(a, "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT); CREATE INDEX ix_name ON users(name);")
    make_db(b, "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT); CREATE TABLE audit(id INTEGER);")
    diff = compare_databases(a, b)
    assert diff["different"] is True
    assert diff["tables_added"] == ["audit"]
    assert diff["tables_changed"]["users"]["columns_added"][0]["name"] == "email"
    assert diff["tables_changed"]["users"]["columns_changed"][0]["name"] == "name"
    assert diff["objects_removed"][0]["name"] == "ix_name"


def test_inspects_views_and_triggers(tmp_path):
    db = tmp_path / "x.db"
    make_db(db, "CREATE TABLE t(id INTEGER); CREATE VIEW v AS SELECT id FROM t; CREATE TRIGGER tr AFTER INSERT ON t BEGIN UPDATE t SET id=id; END;")
    schema = inspect_database(db)
    assert {o.type for o in schema.objects} >= {"table", "view", "trigger"}


def test_missing_database_is_error(tmp_path):
    with pytest.raises(SchemaError):
        inspect_database(tmp_path / "missing.db")
