import logging
import uuid
from typing import List, Any

import cloudscraper
from cloudscraper import CloudScraper

from app.schemas.interface import ScraperBase
from app.schemas.schemas import Product


class Instamart(ScraperBase):
    def __init__(self, lat: str, lon: str, scraper: CloudScraper = cloudscraper.create_scraper()):
        self.base_url = 'https://www.swiggy.com/api/instamart/search'
        self.scraper = scraper
        self.scraper.get('https://blinkit.com/')
        self.cookies = self.scraper.cookies.get_dict()

        self.headers = {
            'User-Agent': self.scraper.headers['User-Agent'],
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://www.swiggy.com',
        }
        self.user_location = {"address": "", "lat": lat, "lng": lon, "id": "", "annotation": "", "name": ""}
        self.results = []

    async def get_products(self, query: str, start: int = 0, size: int = 20) -> List[Product]:
        params = {
            "pageNumber": "0",
            "searchResultsOffset": "0",
            "limit": "10",
            "query": query,
            "ageConsent": "false",
            "layoutId": "3990",
            "pageType": "INSTAMART_AUTO_SUGGEST_PAGE",
            "isPreSearchTag": "false",
            "highConfidencePageNo": "0",
            "lowConfidencePageNo": "0",
        }

        try:
            self.scraper.cookies.set("_deviceId", str(uuid.uuid4()))
            self.scraper.cookies.set("userLocation", str(self.user_location))
            response = self.scraper.post(
                self.base_url,
                json={"facets": {}, "sortAttribute": ""},
                params=params,
                headers=self.headers
            )

            if response.status_code == 200:
                return self.parse_data(response.json())
            return []

        except Exception as e:
            logging.log(logging.WARN, f"Request failed for {query} : {e}")
            return []

    def parse_data(self, data: Any) -> List[Product]:
        try:
            products = []
            widgets = data.get('data', {}).get('widgets', [])

            for widget in widgets:
                if widget.get('type') == 'PRODUCT_LIST':
                    for item in widget.get('data', []):
                        for variation in item.get('variations', []):
                            try:
                                image_urls = variation.get('images', [])
                                image_id = image_urls[0]
                                best_quality = f"https://instamart-media-assets.swiggy.com/swiggy/image/upload/{image_id}"
                                low_quality = f"https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_126,w_126/{image_id}"

                                price_info = variation['price']
                                mrp = float(price_info['mrp'])
                                store_price = float(price_info['offer_price'])
                                savings = mrp - store_price

                                product = Product(
                                    source="instamart",
                                    currency=price_info['currency'],
                                    is_variation=True,
                                    product_id=variation['id'],
                                    brand=item['brand'],
                                    name=variation['display_name'],
                                    similar_with_id="",
                                    weight=variation['quantity'],
                                    total_savings=savings,
                                    mrp_price=mrp,
                                    store_price=store_price,
                                    availability=variation['inventory']['in_stock'],
                                    max_in_cart=variation['cart_allowed_quantity']['total'],
                                    inventory=variation['inventory']['remaining'],
                                    category=item['category'],
                                    deep_link="",
                                    best_quality=best_quality,
                                    low_quality=low_quality
                                )
                                products.append(product)

                            except Exception as e:
                                logging.log(logging.WARN, f"Error processing product variation: {e}")
                                continue

            return products

        except Exception as e:
            logging.log(logging.WARN, f"Parsing Failed in Instamart Scraper : {e}")
            return []
