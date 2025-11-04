import os

print("Current directory:", os.getcwd())
print("\nChecking for data files...")
print("-" * 60)

files_to_check = [
    'data/health_condition.csv',
    'data/Foods_nutrition.csv'
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    abs_path = os.path.abspath(file_path)
    status = "✅ FOUND" if exists else "❌ MISSING"
    print(f"{status}: {file_path}")
    print(f"         Full path: {abs_path}")
    print()

# List what's in data directory
if os.path.exists('data'):
    print("\nFiles in data/ directory:")
    print("-" * 60)
    for item in os.listdir('data'):
        print(f"  • {item}")
else:
    print("\n❌ data/ directory doesn't exist!")
    print("Create it with: mkdir data")


