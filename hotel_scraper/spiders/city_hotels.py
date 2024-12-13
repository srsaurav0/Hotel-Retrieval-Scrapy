import scrapy
import json
import re
import random
import os
import requests


class CityAndHotelsSpider(scrapy.Spider):
    name = "city_hotels"
    start_urls = ['https://uk.trip.com/hotels/?locale=en-GB&curr=GBP']

    def parse(self, response):
        # Locate the <script> tag containing 'window.IBU_HOTEL'
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()
        # self.log(f"Script Data Extracted: {script_data[:1000]}") if script_data else self.log("No script data found.")
        
        if script_data:
            # Extract the JSON-like data within the script
            json_match = re.search(r'window.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)
            if json_match:
                # self.log(f"Raw JSON Extracted: {raw_json[:1000]}...")
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

                # Select a random city
                random_city = random.choice(cities)
                city_id = random_city["id"]
                city_name = random_city["name"]

                self.log(f"Selected city: {city_name} with ID: {city_id}")

                # Construct URL for the selected city's hotels page
                city_url = f"https://uk.trip.com/hotels/list?city={city_id}"

                # Make a request to fetch hotels for the selected city
                yield scrapy.Request(url=city_url, callback=self.parse_city_hotels, meta={"city_name": city_name})
            else:
                self.log("Failed to extract JSON data from script.")


    def parse_city_hotels(self, response):
        """Parse hotels from the selected city's hotel page."""
        city_name = response.meta["city_name"]

        # Locate the <script> tag containing 'window.IBU_HOTEL'
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()
        self.log(f"Script Data Extracted: {script_data[:1000]}") if script_data else self.log("No script data found.")

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

                # Extract hotel data
                city_data = {
                    "city_name": city_name,
                    "hotels": []
                }

                for hotel in hotel_list[:10]:  # Limit to 10 hotels
                    hotel_data = self.extract_hotel_data(hotel)
                    city_data["hotels"].append(hotel_data)

                    # Download and save the image
                    if hotel_data["image_url"] != "N/A":
                        self.download_image(hotel_data["image_url"], city_name, hotel_data["property_title"])

                # Save city and hotel data to a JSON file
                filename = "hotels_data.json"
                with open(filename, "w") as f:
                    json.dump(city_data, f, indent=4)

                self.log(f"Extracted city and hotel data saved to {filename}")
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
            else:
                self.log(f"Failed to download image: {image_url}")
        except Exception as e:
            self.log(f"Error downloading image {image_url}: {e}")
