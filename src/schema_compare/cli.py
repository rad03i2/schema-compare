from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import SchemaError, compare_databases, inspect_database, schema_to_dict


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="schema-compare", description="Compare SQLite database schemas without modifying them.")
    p.add_argument("--version", action="version", version=f"schema-compare {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Inspect one SQLite schema")
    inspect.add_argument("database", type=Path)
    inspect.add_argument("--json", action="store_true", dest="as_json")
    compare = sub.add_parser("compare", help="Compare two SQLite schemas")
    compare.add_argument("left", type=Path)
    compare.add_argument("right", type=Path)
    compare.add_argument("--json", action="store_true", dest="as_json")
    return p


def _render_diff(diff: dict) -> str:
    if not diff["different"]:
        return "Schemas are identical."
    lines = ["Schema differences:"]
    if diff["tables_added"]:
        lines.append("  Tables added: " + ", ".join(diff["tables_added"]))
    if diff["tables_removed"]:
        lines.append("  Tables removed: " + ", ".join(diff["tables_removed"]))
    for table, change in diff["tables_changed"].items():
        lines.append(f"  Table changed: {table}")
        for col in change["columns_added"]:
            lines.append(f"    + column {col['name']} ({col['type']})")
        for col in change["columns_removed"]:
            lines.append(f"    - column {col['name']} ({col['type']})")
        for col in change["columns_changed"]:
            lines.append(f"    ~ column {col['name']}")
    for obj in diff["objects_added"]:
        lines.append(f"  + {obj['type']} {obj['name']}")
    for obj in diff["objects_removed"]:
        lines.append(f"  - {obj['type']} {obj['name']}")
    for obj in diff["objects_changed"]:
        lines.append(f"  ~ {obj['type']} {obj['name']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect":
            data = schema_to_dict(inspect_database(args.database))
            if args.as_json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"Tables: {len(data['tables'])}")
                for name, columns in data["tables"].items():
                    print(f"  {name}: {len(columns)} column(s)")
            return 0
        diff = compare_databases(args.left, args.right)
        print(json.dumps(diff, indent=2, ensure_ascii=False) if args.as_json else _render_diff(diff))
        return 1 if diff["different"] else 0
    except SchemaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
