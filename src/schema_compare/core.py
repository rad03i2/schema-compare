from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class SchemaError(ValueError):
    """Raised when a database cannot be inspected safely."""


@dataclass(frozen=True)
class Column:
    name: str
    type: str
    not_null: bool
    default: str | None
    primary_key: int


@dataclass(frozen=True)
class DbObject:
    type: str
    name: str
    table: str
    sql: str | None


@dataclass(frozen=True)
class Schema:
    tables: dict[str, tuple[Column, ...]]
    objects: tuple[DbObject, ...]


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def inspect_database(path: str | Path) -> Schema:
    db = Path(path).expanduser().resolve()
    if not db.is_file():
        raise SchemaError(f"Database does not exist: {db}")
    try:
        conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        raise SchemaError(f"Cannot open SQLite database: {exc}") from exc
    try:
        rows = conn.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
        ).fetchall()
        objects = tuple(DbObject(*row) for row in rows)
        tables: dict[str, tuple[Column, ...]] = {}
        for obj in objects:
            if obj.type != "table":
                continue
            info = conn.execute(f"PRAGMA table_info({_quote_identifier(obj.name)})").fetchall()
            tables[obj.name] = tuple(
                Column(name=r[1], type=r[2], not_null=bool(r[3]), default=r[4], primary_key=r[5])
                for r in info
            )
        return Schema(tables=tables, objects=objects)
    except sqlite3.Error as exc:
        raise SchemaError(f"Cannot inspect schema: {exc}") from exc
    finally:
        conn.close()


def schema_to_dict(schema: Schema) -> dict[str, Any]:
    return {
        "tables": {name: [asdict(c) for c in cols] for name, cols in schema.tables.items()},
        "objects": [asdict(o) for o in schema.objects],
    }


def compare_schemas(left: Schema, right: Schema) -> dict[str, Any]:
    left_names, right_names = set(left.tables), set(right.tables)
    added = sorted(right_names - left_names)
    removed = sorted(left_names - right_names)
    changed: dict[str, Any] = {}
    for table in sorted(left_names & right_names):
        lcols = {c.name: c for c in left.tables[table]}
        rcols = {c.name: c for c in right.tables[table]}
        c_added = sorted(set(rcols) - set(lcols))
        c_removed = sorted(set(lcols) - set(rcols))
        c_changed = []
        for name in sorted(set(lcols) & set(rcols)):
            if lcols[name] != rcols[name]:
                c_changed.append({"name": name, "left": asdict(lcols[name]), "right": asdict(rcols[name])})
        if c_added or c_removed or c_changed:
            changed[table] = {
                "columns_added": [asdict(rcols[n]) for n in c_added],
                "columns_removed": [asdict(lcols[n]) for n in c_removed],
                "columns_changed": c_changed,
            }
    def obj_map(schema: Schema) -> dict[tuple[str, str], DbObject]:
        return {(o.type, o.name): o for o in schema.objects if o.type != "table"}
    lo, ro = obj_map(left), obj_map(right)
    object_added = [asdict(ro[k]) for k in sorted(set(ro) - set(lo))]
    object_removed = [asdict(lo[k]) for k in sorted(set(lo) - set(ro))]
    object_changed = [
        {"type": k[0], "name": k[1], "left_sql": lo[k].sql, "right_sql": ro[k].sql}
        for k in sorted(set(lo) & set(ro)) if lo[k].sql != ro[k].sql
    ]
    different = bool(added or removed or changed or object_added or object_removed or object_changed)
    return {
        "different": different,
        "tables_added": added,
        "tables_removed": removed,
        "tables_changed": changed,
        "objects_added": object_added,
        "objects_removed": object_removed,
        "objects_changed": object_changed,
    }


def compare_databases(left: str | Path, right: str | Path) -> dict[str, Any]:
    return compare_schemas(inspect_database(left), inspect_database(right))
