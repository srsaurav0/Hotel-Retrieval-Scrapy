window.IBU_HOTEL.initData.htlsData

scrapy
psycopg2-binary
sqlalchemy
scrapy-user-agents


docker-compose run scraper sh

pytest --cov=hotel_scraper


# Test database
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



# test spider
import os
import shutil
import pytest
from hotel_scraper.models import Base, City, Hotel
from hotel_scraper.database import engine, SessionLocal
from hotel_scraper.spiders.city_hotels import CityAndHotelsSpider

@pytest.fixture
def session():
    """Provide a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    yield db_session
    db_session.rollback()
    db_session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_response():
    """Mock response for testing."""
    class MockResponse:
        def __init__(self, text):
            self.text = text

        def xpath(self, path):
            return []
    
    return MockResponse


def test_clear_previous_data(session):
    """Test clearing previous data and images."""
    import os
    import shutil

    # Setup: Create mock images folder and database entries
    os.makedirs("images/mock_city", exist_ok=True)
    with open("images/mock_city/mock_image.jpg", "w") as f:
        f.write("mock image content")

    session.add(City(name="Mock City"))
    session.add(Hotel(name="Mock Hotel", city_id=1))
    session.commit()

    # Clear data
    spider = CityAndHotelsSpider()
    spider.clear_previous_data()

    # Assert images folder is deleted
    assert not os.path.exists("images")

    # Assert database is cleared
    assert session.query(City).count() == 0
    assert session.query(Hotel).count() == 0


def test_parse_with_valid_data(mock_response):
    """Test parsing main city data."""
    from scrapy.http import HtmlResponse

    response = HtmlResponse(
        url="https://uk.trip.com/hotels/?locale=en-GB&curr=GBP",
        body=b'<script>window.IBU_HOTEL = {"initData": {"htlsData": {"inboundCities": [{"name": "City1", "id": "1"}, {"name": "City2", "id": "2"}]}}};</script>',
        encoding="utf-8",
    )

    spider = CityAndHotelsSpider()
    requests = list(spider.parse(response))

    assert len(requests) == 3  # Three random cities selected
    assert "City" in requests[0].meta["city_name"]


def test_parse_city_hotels_with_valid_data(session):
    """Test parsing city hotels."""
    from scrapy.http import HtmlResponse

    response = HtmlResponse(
        url="https://uk.trip.com/hotels/list?city=1",
        body=b'<script>window.IBU_HOTEL = {"initData": {"firstPageList": {"hotelList": [{"hotelBasicInfo": {"hotelName": "Hotel1", "hotelImg": "http://example.com/image.jpg", "price": 100}, "commentInfo": {"commentScore": 4.5}, "positionInfo": {"positionName": "Near Airport", "coordinate": {"lat": 1.23, "lng": 4.56}}, "roomInfo": {"physicalRoomName": "Deluxe"}}]}}};</script>',
        encoding="utf-8",
    )

    spider = CityAndHotelsSpider()
    spider.parse_city_hotels(response)

    # Assert city and hotel are saved
    assert session.query(City).count() == 1
    assert session.query(Hotel).count() == 1

    hotel = session.query(Hotel).first()
    assert hotel.name == "Hotel1"
    assert hotel.price == 100.0


def test_download_image():
    """Test image download functionality."""
    spider = CityAndHotelsSpider()
    image_url = "https://via.placeholder.com/150"
    city_name = "Test City"
    hotel_name = "Test Hotel"

    # Download image
    image_path = spider.download_image(image_url, city_name, hotel_name)

    # Assert image exists
    assert os.path.exists(image_path)

    # Cleanup
    shutil.rmtree("images")


def test_extract_hotel_data():
    """Test the extract_hotel_data method."""
    spider = CityAndHotelsSpider()
    mock_hotel = {
        "hotelBasicInfo": {"hotelName": "Test Hotel", "hotelImg": "/image.jpg", "price": 120.5},
        "commentInfo": {"commentScore": "4.6"},
        "positionInfo": {"positionName": "Downtown", "coordinate": {"lat": 23.81, "lng": 90.41}},
        "roomInfo": {"physicalRoomName": "Suite"},
    }

    hotel_data = spider.extract_hotel_data(mock_hotel)

    assert hotel_data["property_title"] == "Test Hotel"
    assert hotel_data["rating"] == "4.6"
    assert hotel_data["location"] == "Downtown"
    assert hotel_data["latitude"] == 23.81
    assert hotel_data["longitude"] == 90.41
    assert hotel_data["room_type"] == "Suite"
    assert hotel_data["price"] == 120.5
    assert hotel_data["image_url"] == "/image.jpg"

