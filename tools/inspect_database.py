"""Print a small health report for a SQLite database."""

import argparse
import sqlite3


parser = argparse.ArgumentParser()
parser.add_argument("database")
args = parser.parse_args()

connection = sqlite3.connect(args.database)
tables = [
    row[0]
    for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
]
version = connection.execute(
    "SELECT version_num FROM alembic_version"
).fetchone()
print("integrity:", connection.execute("PRAGMA integrity_check").fetchone()[0])
print("tables:", ",".join(tables))
print("alembic_version:", version[0] if version else "missing")
connection.close()
