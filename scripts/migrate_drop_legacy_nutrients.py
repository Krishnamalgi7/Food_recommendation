"""
Migration: Drop the 7 legacy nutrient columns from health_conditions.
These columns were always 0.0 — not in Health_Condition.csv and not used
by the recommendation engine.

Run once from the project root:
    python scripts/migrate_drop_legacy_nutrients.py
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text
from backend.utils.database import engine

COLUMNS_TO_DROP = [
    "calcium_grm",
    "iron_grm",
    "magnesium_grm",
    "potassium_grm",
    "vitamin_a_grm",
    "vitamin_b12_grm",
    "vitamin_c_grm",
]


def migrate():
    with engine.connect() as conn:
        # Fetch the columns that actually exist right now
        existing = {
            r[0] for r in conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'health_conditions'"
            )).fetchall()
        }

        print("Columns currently in health_conditions:")
        for col in sorted(existing):
            print(f"  {col}")
        print()

        dropped, skipped = [], []

        for col in COLUMNS_TO_DROP:
            if col in existing:
                conn.execute(text(
                    f"ALTER TABLE health_conditions DROP COLUMN {col}"
                ))
                conn.commit()
                dropped.append(col)
                print(f"[DROP]  {col}")
            else:
                skipped.append(col)
                print(f"[SKIP]  {col} (not present)")

        print()
        print(f"[OK] Dropped {len(dropped)} column(s), skipped {len(skipped)}.")

        # Verify final state
        remaining = {
            r[0] for r in conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'health_conditions'"
            )).fetchall()
        }
        for bad in COLUMNS_TO_DROP:
            if bad in remaining:
                print(f"[FAIL] {bad} still present!")
        print("[VERIFY] Remaining columns:", sorted(remaining))


if __name__ == "__main__":
    migrate()
