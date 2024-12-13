import scrapy
import json
import re


class CitiesHotelsSpider(scrapy.Spider):
    name = "hotels_list"
    start_urls = ['https://uk.trip.com/hotels/?locale=en-GB&curr=GBP']

    def parse(self, response):
        # Locate the <script> tag containing 'window.IBU_HOTEL'
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()

        if script_data:
            # Extract the JSON-like data within the script
            json_match = re.search(r'window.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)
            if json_match:
                raw_json = json_match.group(1)

                # Parse the JSON data
                data = json.loads(raw_json)
                init_data = data.get("initData", {})
                htls_data = init_data.get("htlsData", {})
                inbound_cities = htls_data.get("inboundCities", [])

                if not inbound_cities:
                    self.log("No cities found in the data.")
                    return

                # Extract city and hotel information
                results = []
                for city in inbound_cities:
                    city_name = city.get("name", "N/A")
                    city_id = city.get("id", "N/A")
                    city_hotels = []

                    # Get recommended hotels under the city
                    recommended_hotels = city.get("recommendHotels", [])
                    for hotel in recommended_hotels:
                        city_hotels.append({
                            "hotelName": hotel.get("hotelName", "N/A"),
                            "rating": hotel.get("rating", "N/A"),
                            "location": hotel.get("districtName", "N/A"),
                            "latitude": hotel.get("lat", "N/A"),
                            "longitude": hotel.get("lon", "N/A"),
                            "price": hotel.get("displayPrice", {}).get("price", "N/A"),
                        })

                    results.append({
                        "cityName": city_name,
                        "cityId": city_id,
                        "hotels": city_hotels,
                    })

                # Save the results to a JSON file
                with open("city_data.json", "w") as f:
                    json.dump(results, f, indent=4)

                self.log("Extracted data saved to city_data.json")
            else:
                self.log("Failed to find JSON data within the script tag.")
        else:
            self.log("No script tag containing 'window.IBU_HOTEL' found.")
