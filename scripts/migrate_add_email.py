"""
Migration: Add email column to users table
Run once from the project root:
    python scripts/migrate_add_email.py
"""
import sys
import os

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text
from backend.utils.database import engine


def migrate():
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'email'
        """))
        already_exists = result.fetchone() is not None

        if already_exists:
            print("✅ Column 'email' already exists in 'users' table. Nothing to do.")
            return

        print("[+] Adding 'email' column to 'users' table ...")
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN email VARCHAR(255) UNIQUE
        """))
        conn.commit()
        print("[OK] Migration complete. Column 'email' added.")
        print("[!]  Existing rows will have email = NULL.")
        print("     Users must re-register or you must backfill email values manually.")


if __name__ == "__main__":
    migrate()
