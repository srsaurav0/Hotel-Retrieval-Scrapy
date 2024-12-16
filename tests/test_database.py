import pytest
from hotel_scraper.database import SessionLocal, engine
from hotel_scraper.models import City, Hotel, Base


@pytest.fixture
def session():
    """Provide a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Start a new session
    db_session = SessionLocal()

    yield db_session  # Provide the session to the test

    # Close session and drop tables after the test
    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create the database schema before running tests."""
    Base.metadata.create_all(bind=engine)  # Create tables
    yield
    Base.metadata.drop_all(bind=engine)  # Drop tables after tests


def test_city_model(session):
    """Test City model insertion."""
    city = City(name="Test City")
    session.add(city)
    session.commit()
    assert city.id is not None
    assert city.name == "Test City"


def test_hotel_model(session):
    """Test Hotel model insertion."""
    city = City(name="Test City")
    session.add(city)
    session.commit()

    hotel = Hotel(
        name="Test Hotel",
        rating=4.5,
        location="Test Location",
        latitude=1.23,
        longitude=4.56,
        room_type="Deluxe",
        price=100.0,
        image_path="/path/to/image.jpg",
        city_id=city.id,
    )
    session.add(hotel)
    session.commit()

    assert hotel.id is not None
    assert hotel.name == "Test Hotel"