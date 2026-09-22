import json
import sqlite3

from schema_compare.cli import main


def db(path, sql):
    with sqlite3.connect(path) as conn:
        conn.executescript(sql)


def test_compare_exit_codes(tmp_path, capsys):
    a, b = tmp_path / "a.db", tmp_path / "b.db"
    db(a, "CREATE TABLE t(id INTEGER);")
    db(b, "CREATE TABLE t(id INTEGER);")
    assert main(["compare", str(a), str(b)]) == 0
    db(b, "ALTER TABLE t ADD COLUMN name TEXT;")
    assert main(["compare", str(a), str(b), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out.split("Schemas are identical.\n")[-1])
    assert payload["different"] is True


def test_inspect_json(tmp_path, capsys):
    path = tmp_path / "x.db"
    db(path, "CREATE TABLE items(id INTEGER PRIMARY KEY, title TEXT);")
    assert main(["inspect", str(path), "--json"]) == 0
    assert "items" in json.loads(capsys.readouterr().out)["tables"]


def test_missing_file_returns_two(tmp_path):
    assert main(["inspect", str(tmp_path / "none.db")]) == 2
