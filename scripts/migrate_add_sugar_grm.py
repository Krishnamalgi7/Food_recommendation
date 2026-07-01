"""
Migration: Add sugar_grm column to health_conditions table
AND backfill Sugar values from Health_Condition.csv into existing rows.

Run once from the project root:
    python scripts/migrate_add_sugar_grm.py
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text
from backend.utils.database import engine

# Sugar values per disease, sourced directly from Health_Condition.csv
CSV_SUGAR = {
    "Skin":       50.0,
    "BP":         30.0,
    "Diabetes":   20.0,
    "Heart":      25.0,
    "Kidney":     20.0,
    "Liver":      35.0,
    "Lung":       25.0,
    "PCOD":       25.0,
    "Gastroloty": 20.0,   # matches the CSV disease name exactly
}


def migrate():
    with engine.connect() as conn:
        # -- Step 1: Check if column already exists --
        rows = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'health_conditions' AND column_name = 'sugar_grm'"
        )).fetchall()

        if rows:
            print("[OK] Column 'sugar_grm' already exists.")
        else:
            print("[+] Adding 'sugar_grm' column to 'health_conditions' ...")
            conn.execute(text(
                "ALTER TABLE health_conditions ADD COLUMN sugar_grm FLOAT"
            ))
            conn.commit()
            print("[OK] Column added.")

        # -- Step 2: Backfill sugar values for every existing row --
        print("[+] Backfilling Sugar values from Health_Condition.csv data ...")
        updated = 0
        for disease, sugar_val in CSV_SUGAR.items():
            result = conn.execute(text(
                "UPDATE health_conditions SET sugar_grm = :sugar WHERE name = :name"
            ), {"sugar": sugar_val, "name": disease})
            conn.commit()
            if result.rowcount:
                print(f"    {disease}: sugar_grm = {sugar_val}")
                updated += result.rowcount

        print(f"[OK] Backfilled {updated} rows.")

        # -- Step 3: Verify --
        rows = conn.execute(text(
            "SELECT name, sugar_grm FROM health_conditions ORDER BY id"
        )).fetchall()
        print("\n[VERIFY] health_conditions.sugar_grm:")
        for r in rows:
            print(f"    {r[0]}: {r[1]}")


if __name__ == "__main__":
    migrate()
