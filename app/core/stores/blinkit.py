import logging
from typing import List

import cloudscraper
from cloudscraper import CloudScraper

from app.schemas.interface import ScraperBase
from app.schemas.schemas import Product


class Blinkit(ScraperBase):
    def __init__(self, lat: str, lon: str, scraper: CloudScraper = cloudscraper.create_scraper()):
        self.base_url = 'https://blinkit.com/v6/search/products'
        self.scraper = scraper
        self.scraper.get('https://blinkit.com/')
        self.cookies = self.scraper.cookies.get_dict()

        self.headers = {
            'User-Agent': self.scraper.headers['User-Agent'],
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'app_client': 'consumer_web',
            'lat': lat,
            'lon': lon,
            'Content-Type': 'application/json',
            'Origin': 'https://blinkit.com'
        }

    async def get_products(self, query: str, start: int = 0, size: int = 10) -> List[Product]:
        params = {
            'start': start,
            'size': size,
            'search_type': 7,
            'q': query
        }

        try:
            response = self.scraper.get(
                self.base_url,
                params=params,
                headers=self.headers
            )

            if response.status_code == 200:
                return self.parse_data(response.json())
            return []

        except Exception as e:
            logging.log(logging.WARN, f"Request failed for {query} : {e}")
            return []

    def parse_data(self, json_data) -> List[Product]:
        products = []
        for product in json_data.get('products', []):
            variant = (product.get('variant_info') or [{}])[0]

            product_dict = {
                "source": "blinkit",
                "currency": "INR",
                "is_variation": len(product.get('variant_info', [])) > 1,
                "product_id": str(product.get('product_id', '')),
                "brand": product.get('brand', ''),
                "name": product.get('name', ''),
                "similar_with_id": str(product.get('group_id', '')),
                "weight": variant.get('unit', ''),
                "total_savings": float(product.get('mrp', 0) - product.get('price', 0)),
                "mrp_price": float(product.get('mrp', 0)),
                "store_price": float(product.get('price', 0)),
                "availability": product.get('inventory', 0) > 0,
                "max_in_cart": 10,
                "inventory": product.get('inventory', 0),
                "category": product.get('type', ''),
                "deep_link": "",
                "best_quality": variant.get('image_url', ''),
                "low_quality": variant.get('image_url', '')
            }

            products.append(Product(**product_dict))

        return products
