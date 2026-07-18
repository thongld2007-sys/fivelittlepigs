"""Copy a legacy SQLite database into an empty PostgreSQL database safely.

The source is never modified. The target copy runs in one transaction and rolls
back on any error.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from sqlalchemy import JSON, create_engine, func, insert, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.models import Base


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, help="Path to the source tutor.db")
    parser.add_argument("--database-url", required=True, help="postgresql+psycopg://...")
    parser.add_argument("--dry-run", action="store_true", help="Inspect and validate without copying")
    return parser.parse_args()


def source_tables(connection):
    return {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        if not row[0].startswith("sqlite_")
    }


def decode_json_columns(table, row):
    converted = dict(row)
    for column in table.columns:
        if isinstance(column.type, JSON) and isinstance(converted.get(column.name), str):
            converted[column.name] = json.loads(converted[column.name])
    return converted


def main():
    args = parse_args()
    source_path = Path(args.sqlite).resolve()
    if not source_path.is_file():
        raise SystemExit(f"SQLite source not found: {source_path}")
    if not args.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
        raise SystemExit("The target must be a PostgreSQL DATABASE_URL")

    source = sqlite3.connect(f"{source_path.as_uri()}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    available = source_tables(source)
    plan = []
    for table in Base.metadata.sorted_tables:
        if table.name not in available:
            continue
        source_columns = {row[1] for row in source.execute(f'PRAGMA table_info("{table.name}")')}
        common = [column.name for column in table.columns if column.name in source_columns]
        count = source.execute(f'SELECT COUNT(*) FROM "{table.name}"').fetchone()[0]
        plan.append((table, common, count))
    print("Migration plan:")
    for table, columns, count in plan:
        print(f"  {table.name}: {count} rows, {len(columns)} columns")
    if args.dry_run:
        source.close()
        return

    target = create_engine(args.database_url, pool_pre_ping=True)
    Base.metadata.create_all(target)
    copied = {}
    with target.begin() as destination:
        occupied = [
            table.name for table, _, _ in plan
            if destination.scalar(select(func.count()).select_from(table))
        ]
        if occupied:
            raise RuntimeError("Target is not empty for tables: " + ", ".join(occupied))
        for table, columns, expected in plan:
            rows = source.execute(
                f'SELECT {", ".join(chr(34) + name + chr(34) for name in columns)} FROM "{table.name}"'
            ).fetchall()
            payload = [decode_json_columns(table, {name: row[name] for name in columns}) for row in rows]
            if payload:
                destination.execute(insert(table), payload)
            actual = destination.scalar(select(func.count()).select_from(table))
            if actual != expected:
                raise RuntimeError(f"Count mismatch for {table.name}: expected={expected}, actual={actual}")
            copied[table.name] = actual
    source.close()
    print("Migration committed successfully:", copied)


if __name__ == "__main__":
    main()
