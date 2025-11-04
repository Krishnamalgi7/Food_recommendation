"""
Script to create all database tables
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.database import engine, Base
from backend.models.custom_tables import (
    User,
    HealthCondition,
    Food,
    UserConditionAssociation,
    UserFood
)
from backend.utils.logger import CustomLogger

LOGGER = CustomLogger()


def create_tables():
    """Create all database tables"""
    try:
        LOGGER.info("Creating database tables...")

        Base.metadata.create_all(bind=engine)

        LOGGER.info("✓ All tables created successfully!")

        table_names = Base.metadata.tables.keys()
        LOGGER.info(f"Created tables: {', '.join(table_names)}")

        return True

    except Exception as ex:
        LOGGER.error(f"Error creating tables: {str(ex)}")
        return False


if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)