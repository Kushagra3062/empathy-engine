from app.database import engine, Base
from app.db_models import SynthesisLog, SystemMetrics
from sqlalchemy import text

def reset_db():
    print("Attempting to reset database tables...")
    try:
        # Drop tables with raw SQL to bypass SQLAlchemy's metadata checks if needed
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS synthesis_logs"))
            conn.execute(text("DROP TABLE IF EXISTS system_metrics"))
            conn.commit()
            print("Tables dropped successfully.")
        
        # Recreate tables
        Base.metadata.create_all(bind=engine)
        print("Database schemas recreated successfully.")
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_db()
