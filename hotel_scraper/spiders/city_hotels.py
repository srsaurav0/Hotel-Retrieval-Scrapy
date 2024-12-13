import scrapy
import json
import re
import random
import os
import requests
import shutil
from hotel_scraper.database import SessionLocal
from hotel_scraper.models import City, Hotel


class CityAndHotelsSpider(scrapy.Spider):
    name = "city_hotels"
    start_urls = ['https://uk.trip.com/hotels/?locale=en-GB&curr=GBP']

    def clear_previous_data(self):
        """Clear previous data and images."""
        # Clear images folder
        folder_path = "images"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # Recursively delete the folder
            self.log(f"Deleted folder: {folder_path}")

        # Clear database tables
        session = SessionLocal()
        session.query(Hotel).delete()
        session.query(City).delete()
        session.commit()
        session.close()
        self.log("Previous data and images cleared.")

    def parse(self, response):
        # Clear previous data and images
        self.clear_previous_data()

        # Locate the <script> tag containing 'window.IBU_HOTEL'
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()
        
        if script_data:
            # Extract the JSON-like data within the script
            json_match = re.search(r'window.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)
            if json_match:
                raw_json = json_match.group(1)
                data = json.loads(raw_json)
                init_data = data.get("initData", {})
                htls_data = init_data.get("htlsData", {})
                inbound_cities = htls_data.get("inboundCities", [])

                if not inbound_cities:
                    self.log("No cities found in the data.")
                    return

                # Extract city information
                cities = [{"name": city.get("name", "N/A"), "id": city.get("id", "N/A")} for city in inbound_cities]

                # Select 3 random cities
                selected_cities = random.sample(cities, min(3, len(cities)))

                for city in selected_cities:
                    city_id = city["id"]
                    city_name = city["name"]
                    self.log(f"Selected city: {city_name} with ID: {city_id}")

                    # Construct URL for the selected city's hotels page
                    city_url = f"https://uk.trip.com/hotels/list?city={city_id}"

                    # Make a request to fetch hotels for the selected city
                    yield scrapy.Request(
                        url=city_url,
                        callback=self.parse_city_hotels,
                        meta={"city_name": city_name}
                    )
            else:
                self.log("Failed to extract JSON data from script.")

    def parse_city_hotels(self, response):
        """Parse hotels from the selected city's hotel page."""
        city_name = response.meta["city_name"]

        # Locate the <script> tag containing 'window.IBU_HOTEL'
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()

        if script_data:
            json_match = re.search(r'window.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)
            if json_match:
                raw_json = json_match.group(1)
                data = json.loads(raw_json)
                init_data = data.get("initData", {})
                first_page_list = init_data.get("firstPageList", [])
                if not first_page_list:
                    self.log(f"No hotel data found for city: {city_name}")
                    return

                hotel_list = first_page_list.get("hotelList", [])
                if not hotel_list:
                    self.log(f"No hotels found for city: {city_name}")
                    return

                # Connect to the database
                session = SessionLocal()

                # Ensure the city exists in the database
                city = session.query(City).filter_by(name=city_name).first()
                if not city:
                    city = City(name=city_name)
                    session.add(city)
                    session.commit()

                for hotel in hotel_list[:10]:  # Limit to 10 hotels per city
                    hotel_data = self.extract_hotel_data(hotel)

                    # Download and save the image
                    image_path = None
                    if hotel_data["image_url"] != "N/A":
                        image_path = self.download_image(hotel_data["image_url"], city_name, hotel_data["property_title"])

                    # Add hotel data to the database
                    hotel_obj = Hotel(
                        name=hotel_data["property_title"],
                        rating=float(hotel_data["rating"]) if hotel_data["rating"] not in ["N/A", "", None] else None,
                        location=hotel_data["location"],
                        latitude=float(hotel_data["latitude"]) if hotel_data["latitude"] != "N/A" else None,
                        longitude=float(hotel_data["longitude"]) if hotel_data["longitude"] != "N/A" else None,
                        room_type=hotel_data["room_type"],
                        price=float(hotel_data["price"]) if hotel_data["price"] not in ["N/A", "", None] else None,
                        image_path=image_path,
                        city_id=city.id,
                    )
                    session.add(hotel_obj)

                # Commit the transaction
                session.commit()

                # Query the database to display data
                self.display_database_content(session)

                session.close()

                self.log(f"Data for city '{city_name}' and its hotels has been saved to the database.")
            else:
                self.log("Failed to extract JSON data from script.")

    def extract_hotel_data(self, hotel):
        """Extract and structure hotel data."""
        hotel_basic_info = hotel.get("hotelBasicInfo", {})
        commentInfo = hotel.get("commentInfo", {})
        positionInfo = hotel.get("positionInfo", {})
        roomInfo = hotel.get("roomInfo", {})
        return {
            "property_title": hotel_basic_info.get("hotelName", "N/A"),
            "rating": commentInfo.get("commentScore", "N/A"),
            "location": positionInfo.get("positionName", "N/A"),
            "latitude": positionInfo.get("coordinate", {}).get("lat", "N/A"),
            "longitude": positionInfo.get("coordinate", {}).get("lng", "N/A"),
            "room_type": roomInfo.get("physicalRoomName", "N/A"),
            "price": hotel_basic_info.get("price", "N/A"),
            "image_url": hotel_basic_info.get("hotelImg", "N/A"),
        }

    def download_image(self, image_url, city_name, hotel_name):
        """Download image and save it to the images folder."""
        folder_path = os.path.join("images", city_name)
        os.makedirs(folder_path, exist_ok=True)

        image_name = f"{hotel_name.replace(' ', '_')}.jpg"
        image_path = os.path.join(folder_path, image_name)

        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                self.log(f"Image saved: {image_path}")
                return image_path
            else:
                self.log(f"Failed to download image: {image_url}")
                return None
        except Exception as e:
            self.log(f"Error downloading image {image_url}: {e}")
            return None
        
    def display_database_content(self, session):
        """Display the content of the database."""
        self.log("Fetching data from the database...")

        # Query all cities
        cities = session.query(City).all()
        for city in cities:
            self.log(f"City: {city.name}")
            
            # Query hotels for each city
            hotels = session.query(Hotel).filter_by(city_id=city.id).all()
            for hotel in hotels:
                self.log(f"    Hotel: {hotel.name}")
                self.log(f"    Rating: {hotel.rating}")
                self.log(f"    Location: {hotel.location}")
                self.log(f"    Latitude: {hotel.latitude}")
                self.log(f"    Longitude: {hotel.longitude}")
                self.log(f"    Room Type: {hotel.room_type}")
                self.log(f"    Price: {hotel.price}")
                self.log(f"    Image Path: {hotel.image_path}")

