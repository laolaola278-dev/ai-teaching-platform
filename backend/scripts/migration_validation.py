#!/usr/bin/env python3
"""Migration validation: run Alembic migrate head and downgrade to base against a test DB.

This script uses the DATABASE_URL environment variable. If not set, it will skip gracefully.
Intended for CI to quickly sanity-check migration viability in a disposable environment.
"""
import os
import subprocess
import sys


def run(cmd, env=None):
    res = subprocess.run(cmd, shell=False, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
    return res.returncode


def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set; skipping migration validation.")
        return

    env = os.environ.copy()
    env["DATABASE_URL"] = url
    print(f"Running Alembic migrate head against: {url}")
    rc = run(["alembic", "upgrade", "head"], env=env)
    if rc != 0:
        sys.exit(rc)
    print("Upgrade complete. Running downgrade to base...")
    rc = run(["alembic", "downgrade", "base"], env=env)
    if rc != 0:
        sys.exit(rc)
    print("Migration sanity check completed successfully.")


if __name__ == '__main__':
    main()
