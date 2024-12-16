import os
import shutil
import pytest
from scrapy.http import Request, HtmlResponse
from hotel_scraper.spiders.city_hotels import CityAndHotelsSpider
from hotel_scraper.models import Base, City, Hotel
from hotel_scraper.database import engine, SessionLocal


# Fixtures
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create the database schema before running tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session():
    """Provide a fresh database session for each test."""
    db_session = SessionLocal()
    yield db_session
    db_session.rollback()
    db_session.close()


@pytest.fixture
def spider():
    """Provide an instance of the spider."""
    return CityAndHotelsSpider()


# Tests
def test_clear_previous_data(session, spider):
    """Test clearing previous data and images."""
    # Setup: Create mock images folder and database entries
    os.makedirs("images/mock_city", exist_ok=True)
    with open("images/mock_city/mock_image.jpg", "w") as f:
        f.write("mock image content")

    session.add(City(name="Mock City"))
    session.add(Hotel(name="Mock Hotel", city_id=1))
    session.commit()

    # Clear data
    spider.clear_previous_data()

    # Assert images folder is deleted
    assert not os.path.exists("images")

    # Assert database is cleared
    assert session.query(City).count() == 0
    assert session.query(Hotel).count() == 0


def test_parse_with_valid_data(spider):
    """Test parsing main city data."""
    response = HtmlResponse(
        url="https://uk.trip.com/hotels/?locale=en-GB&curr=GBP",
        body=(
            b'<script>window.IBU_HOTEL = {"initData": {"htlsData": {"inboundCities": ['
            b'{"name": "City1", "id": "1"}, {"name": "City2", "id": "2"}]}}};</script>'
        ),
        encoding="utf-8",
    )

    requests = list(spider.parse(response))

    assert len(requests) == 2  # Two cities parsed
    assert "City1" in requests[0].meta["city_name"] or "City2" in requests[0].meta["city_name"]



def test_parse_city_hotels_with_valid_data(session, spider):
    """Test parsing city hotels."""
    # Create a mock request with meta data
    mock_request = Request(
        url="https://uk.trip.com/hotels/list?city=1",
        meta={"city_name": "Test City"}
    )

    # Create a response with the mock request
    response = HtmlResponse(
        url=mock_request.url,
        body=(
            b'<script>window.IBU_HOTEL = {"initData": {"firstPageList": {"hotelList": ['
            b'{"hotelBasicInfo": {"hotelName": "Hotel1", "hotelImg": "http://example.com/image.jpg", "price": 100},'
            b'"commentInfo": {"commentScore": 4.5},'
            b'"positionInfo": {"positionName": "Near Airport", "coordinate": {"lat": 1.23, "lng": 4.56}},'
            b'"roomInfo": {"physicalRoomName": "Deluxe"}}]}}};</script>'
        ),
        encoding="utf-8",
        request=mock_request  # Attach the mock request to the response
    )

    spider.parse_city_hotels(response)

    # Assert city and hotel are saved
    assert session.query(City).count() == 1
    assert session.query(Hotel).count() == 1

    hotel = session.query(Hotel).first()
    assert hotel.name == "Hotel1"
    assert hotel.price == 100.0
    assert hotel.latitude == 1.23
    assert hotel.longitude == 4.56


def test_extract_hotel_data(spider):
    """Test extracting hotel data."""
    hotel_data = {
        "hotelBasicInfo": {"hotelName": "Hotel1", "hotelImg": "http://example.com/image.jpg", "price": 100},
        "commentInfo": {"commentScore": 4.5},
        "positionInfo": {"positionName": "Near Airport", "coordinate": {"lat": 1.23, "lng": 4.56}},
        "roomInfo": {"physicalRoomName": "Deluxe"},
    }

    extracted = spider.extract_hotel_data(hotel_data)

    assert extracted["property_title"] == "Hotel1"
    assert extracted["price"] == 100
    assert extracted["latitude"] == 1.23
    assert extracted["longitude"] == 4.56


def test_download_image(spider):
    """Test image download functionality."""
    image_url = "https://via.placeholder.com/150"
    city_name = "Test City"
    hotel_name = "Test Hotel"

    # Download image
    image_path = spider.download_image(image_url, city_name, hotel_name)

    # Assert image exists
    assert os.path.exists(image_path)

    # Cleanup
    shutil.rmtree("images")
