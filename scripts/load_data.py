"""
Script to load data from CSV files into the database
ROBUST VERSION: Handles missing/invalid data gracefully
"""
import sys
import os
import json
import pandas as pd
import numpy as np

# AUTO-DETECT PROJECT ROOT
if os.path.basename(os.getcwd()) == 'scripts':
    PROJECT_ROOT = os.path.dirname(os.getcwd())
    os.chdir(PROJECT_ROOT)
else:
    PROJECT_ROOT = os.getcwd()

sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session
from backend.utils.database import SessionLocal
from backend.models.custom_tables import HealthCondition, Food
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()


def parse_nutrients(nutrients_value):
    """
    Safely parse nutrients from various formats
    Returns a dict or empty dict if parsing fails
    """
    # Handle None/NaN
    if nutrients_value is None or (isinstance(nutrients_value, float) and np.isnan(nutrients_value)):
        return {}

    # Already a dict
    if isinstance(nutrients_value, dict):
        return nutrients_value

    # Try to parse as JSON string
    if isinstance(nutrients_value, str):
        # Remove whitespace
        nutrients_value = nutrients_value.strip()

        # Empty string
        if not nutrients_value:
            return {}
        nutrients_dict = dict(item.strip().split(': ') for item in nutrients_value.split(','))
        print(nutrients_dict)

        # Try parsing JSON
        try:
            #parsed = json.loads(nutrients_dict)
            if isinstance(nutrients_dict, dict):
                return nutrients_dict
            else:
                return {}
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parsing fails, try to handle common issues
            try:
                # Sometimes quotes are escaped incorrectly
                nutrients_value = nutrients_value.replace("'", '"')
                parsed = json.loads(nutrients_value)
                if isinstance(parsed, dict):
                    return parsed
            except:
                pass

            return {}

    return {}


def get_default_nutrients():
    """Return default nutrients structure"""
    return {
        "Calcium": 0.0,
        "Carbohydrates": 0.0,
        "Fats": 0.0,
        "Fiber": 0.0,
        "Iron": 0.0,
        "Magnesium": 0.0,
        "Potassium": 0.0,
        "Protein": 0.0,
        "Sodium": 0.0,
        "Vitamin_A": 0.0,
        "Vitamin_B12": 0.0,
        "Vitamin_C": 0.0
    }


def load_health_conditions(db: Session):
    """Load health conditions from CSV"""
    try:
        csv_path = os.path.join(PROJECT_ROOT, 'data', 'normalized_health_conditions.csv')

        print(f"📁 Looking for: {csv_path}")

        if not os.path.exists(csv_path):
            print(f"\n❌ FILE NOT FOUND: {csv_path}")
            return False

        print(f"✅ Found file!")

        # Read CSV with error handling
        df = pd.read_csv(csv_path, na_values=['', 'NA', 'null', 'None'])
        print(f"✅ Loaded CSV: {len(df)} rows, {len(df.columns)} columns")

        # Check if already loaded
        existing_count = db.query(HealthCondition).count()
        if existing_count > 0:
            print(f"ℹ️  Health conditions already loaded ({existing_count} records). Skipping...")
            return True

        print(f"\n📊 Inserting {len(df)} health conditions...")

        success_count = 0
        error_count = 0

        for idx, row in df.iterrows():
            try:
                # condition = HealthCondition(
                #     name=str(row['Disease']),
                #     description=f"Dietary requirements for {row['Disease']}",
                #     calcium_grm=float(row['Calcium']) if pd.notna(row['Calcium']) else 0.0,
                #     carbohydrates_grm=float(row['Carbohydrates']) if pd.notna(row['Carbohydrates']) else 0.0,
                #     fats_grm=float(row['Fats']) if pd.notna(row['Fats']) else 0.0,
                #     fiber_grm=float(row['Fiber']) if pd.notna(row['Fiber']) else 0.0,
                #     iron_grm=float(row['Iron']) if pd.notna(row['Iron']) else 0.0,
                #     magnesium_grm=float(row['Magnesium']) if pd.notna(row['Magnesium']) else 0.0,
                #     potassium_grm=float(row['Potassium']) if pd.notna(row['Potassium']) else 0.0,
                #     protein_grm=float(row['Protein']) if pd.notna(row['Protein']) else 0.0,
                #     sodium_grm=float(row['Sodium']) if pd.notna(row['Sodium']) else 0.0,
                #     vitamin_a_grm=float(row['Vitamin_A']) if pd.notna(row['Vitamin_A']) else 0.0,
                #     vitamin_b12_grm=float(row['Vitamin_B12']) if pd.notna(row['Vitamin_B12']) else 0.0,
                #     vitamin_c_grm=float(row['Vitamin_C']) if pd.notna(row['Vitamin_C']) else 0.0
                # )
                condition = HealthCondition(
                    name=str(row['Disease']),
                    description=f"Dietary requirements for {row['Disease']}",
                    calcium_grm=0.0,
                    carbohydrates_grm=0.0,
                    fats_grm=float(row['Fats']) if pd.notna(row['Fats']) else 0.0,
                    fiber_grm=float(row['Fiber']) if pd.notna(row['Fiber']) else 0.0,
                    iron_grm=0.0,
                    magnesium_grm=0.0,
                    potassium_grm=0.0,
                    protein_grm=float(row['Protein']) if pd.notna(row['Protein']) else 0.0,
                    sodium_grm=0.0,
                    vitamin_a_grm= 0.0,
                    vitamin_b12_grm= 0.0,
                    vitamin_c_grm=0.0
                )
                db.add(condition)
                success_count += 1
                print(f"  ✓ {success_count}/{len(df)}: {row['Disease']}")

            except Exception as e:
                error_count += 1
                print(f"  ✗ Error on row {idx}: {str(e)}")
                continue

        db.commit()

        final_count = db.query(HealthCondition).count()
        print(f"\n✅ Successfully loaded {final_count} health conditions!")
        if error_count > 0:
            print(f"⚠️  Skipped {error_count} rows due to errors")

        return True

    except Exception as ex:
        print(f"\n❌ ERROR: {str(ex)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False


def load_foods(db: Session, batch_size: int = 500):
    """Load foods from CSV with robust error handling"""
    try:
        csv_path = os.path.join(PROJECT_ROOT, 'data', 'Foods_nutrition.csv')

        print(f"📁 Looking for: {csv_path}")

        if not os.path.exists(csv_path):
            print(f"\n❌ FILE NOT FOUND: {csv_path}")
            return False

        print(f"✅ Found file!")

        # Check if already loaded
        existing_count = db.query(Food).count()
        if existing_count > 0:
            print(f"ℹ️  Foods already loaded ({existing_count} records). Skipping...")
            return True

        print(f"\n🍎 Loading foods in batches of {batch_size}...")
        print("⏳ This may take a few minutes for large files...")

        chunk_count = 0
        total_loaded = 0
        total_errors = 0

        # Read CSV in chunks with error handling
        for chunk in pd.read_csv(csv_path, chunksize=batch_size, na_values=['', 'NA', 'null', 'None'], keep_default_na=True):
            chunk_count += 1
            print(f"\n  📦 Batch {chunk_count}: Processing {len(chunk)} rows...")

            foods = []
            batch_errors = 0

            for idx, row in chunk.iterrows():
                try:
                    # Parse nutrients with robust error handling
                    nutrients = parse_nutrients(row.get('nutrients'))

                    # If nutrients is empty, use defaults
                    if not nutrients:
                        nutrients = get_default_nutrients()

                    # Ensure all required fields are present
                    name = str(row['name']) if pd.notna(row.get('name')) else f"Unknown_{idx}"
                    category = str(row['category']) if pd.notna(row.get('category')) else "Uncategorized"
                    food_type = str(row['type']) if pd.notna(row.get('type')) else "Unknown"
                    ingredients = str(row['ingredients']) if pd.notna(row.get('ingredients')) else ""

                    # Handle price
                    try:
                        price = float(row['price']) if pd.notna(row.get('price')) else 0.0
                    except (ValueError, TypeError):
                        price = 0.0

                    food = Food(
                        name=name,
                        category=category,
                        type=food_type,
                        ingredients=ingredients,
                        nutrients=nutrients,
                        price=price
                    )
                    foods.append(food)

                except Exception as row_ex:
                    batch_errors += 1
                    total_errors += 1

                    # Only show first 5 errors per batch to avoid spam
                    if batch_errors <= 5:
                        print(f"    ⚠️  Row {idx}: {str(row_ex)}")
                    elif batch_errors == 6:
                        print(f"    ⚠️  ... (hiding additional errors)")

            # Save batch
            if foods:
                try:
                    db.bulk_save_objects(foods)
                    db.commit()
                    total_loaded += len(foods)
                    print(f"    ✓ Inserted {len(foods)} foods (Total: {total_loaded})")

                    if batch_errors > 0:
                        print(f"    ⚠️  Skipped {batch_errors} rows in this batch")

                except Exception as batch_ex:
                    print(f"    ✗ Failed to save batch: {str(batch_ex)}")
                    db.rollback()
                    continue

            # Progress update every 10 batches
            if chunk_count % 10 == 0:
                print(f"\n  📊 Progress: {total_loaded} foods loaded so far...")

        final_count = db.query(Food).count()
        print(f"\n✅ Successfully loaded {final_count} foods!")

        if total_errors > 0:
            print(f"⚠️  Total rows skipped due to errors: {total_errors}")
            print(f"📊 Success rate: {(total_loaded/(total_loaded+total_errors)*100):.1f}%")

        return True

    except Exception as ex:
        print(f"\n❌ ERROR: {str(ex)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False


def main():
    """Main function to load all data"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("🚀 FOOD RECOMMENDATION SYSTEM - DATA LOADER (ROBUST VERSION)")
        print("=" * 70)
        print(f"\n📂 Project Root: {PROJECT_ROOT}")
        print(f"📂 Current Directory: {os.getcwd()}")
        print()

        # Verify data directory exists
        data_dir = os.path.join(PROJECT_ROOT, 'data')
        if not os.path.exists(data_dir):
            print(f"❌ ERROR: Data directory not found at {data_dir}")
            print(f"\n💡 Create it with: mkdir {data_dir}")
            return False

        print(f"✅ Data directory found: {data_dir}")
        print(f"📂 Files in data/: {os.listdir(data_dir)}")
        print()

        # Load health conditions
        print("=" * 70)
        print("1️⃣  LOADING HEALTH CONDITIONS")
        print("=" * 70)
        if not load_health_conditions(db):
            print("\n⚠️  Failed to load health conditions (continuing anyway...)")

        print()

        # Load foods
        print("=" * 70)
        print("2️⃣  LOADING FOODS")
        print("=" * 70)
        if not load_foods(db):
            print("\n❌ Failed to load foods!")
            return False

        print()
        print("=" * 70)
        print("🎉 DATA LOADING COMPLETE!")
        print("=" * 70)

        # Summary
        health_count = db.query(HealthCondition).count()
        food_count = db.query(Food).count()

        print(f"\n📊 SUMMARY:")
        print(f"  • Health Conditions: {health_count}")
        print(f"  • Foods: {food_count}")
        print()

        return True

    except Exception as ex:
        print(f"\n❌ FATAL ERROR: {str(ex)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = main()

    if success:
        print("\n✅ SUCCESS! You can now start the application!")
        print("   Backend:  uvicorn backend.main:app --reload")
        print("   Frontend: cd frontend && streamlit run app.py")
    else:
        print("\n⚠️  Some errors occurred. Check the output above.")
        print("   The application may still work with partial data.")

    sys.exit(0 if success else 1)