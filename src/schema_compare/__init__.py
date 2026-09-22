"""Deterministic SQLite schema inspection and comparison."""

from .core import Schema, SchemaError, compare_databases, compare_schemas, inspect_database, schema_to_dict

__version__ = "1.0.0"
__author__ = "Radwan Abdulhadi Ahmed / @rad03i2"

__all__ = ["Schema", "SchemaError", "compare_databases", "compare_schemas", "inspect_database", "schema_to_dict"]
