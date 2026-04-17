"""
Database initialization and schema setup.
"""
import os
import sys
from sqlalchemy import create_engine, text
from agent.state_manager import Base, BuildJob, Deployment

# Import models to ensure they're registered
from agent.state_manager import StateManager


def init_database(db_url: str = None):
    """
    Initialize database schema.

    Args:
        db_url: Database URL (default from environment)
    """
    db_url = db_url or os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/automotive"
    )

    print(f"Initializing database: {db_url}")

    try:
        # Create engine
        engine = create_engine(db_url)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")

        # Create tables
        Base.metadata.create_all(engine)
        print("✓ Database schema created successfully")

        # Initialize state manager
        state_manager = StateManager(db_url)
        state_manager.init_db()
        print("✓ State manager initialized")

        return True

    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
