from sqlalchemy.exc import OperationalError
from hotel_scraper.database import engine
from hotel_scraper.models import Base

if __name__ == "__main__":
    try:
        print("Initializing database...")
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    except OperationalError as e:
        print(f"Database initialization failed: {e}")
