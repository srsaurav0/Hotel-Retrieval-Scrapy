import scrapy
import json
import re

class HotelsSpider(scrapy.Spider):
    name = "hotels"
    start_urls = ['https://uk.trip.com/hotels/?locale=en-GB&curr=GBP']

    def parse(self, response):
        # Locate the <script> tag that contains 'window.IBU_HOTEL'
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()

        if script_data:
            # Extract the JSON-like data within the script
            json_match = re.search(r'window.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)
            if json_match:
                raw_json = json_match.group(1)
                self.log(f"Extracted raw JSON: {raw_json[:1000]}...")
                self.log(f"Last 100 characters of JSON: {raw_json[-100:]}")
                
                # Parse the JSON data
                data = json.loads(raw_json)
                
                # Example: Access specific fields
                init_data = data.get("initData", {})
                seo_headers = init_data.get("seoHeader", [])
                
                # Save or process the extracted data
                with open("hotel_data.json", "w") as f:
                    json.dump(init_data, f, indent=4)

                self.log(f"Extracted data saved to hotel_data.json")
            else:
                self.log("Failed to find JSON data within the script tag.")
        else:
            self.log("No script tag containing 'window.IBU_HOTEL' found.")
