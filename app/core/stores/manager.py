import asyncio
from typing import List

from app.core.stores.blinkit import Blinkit
from app.core.stores.instamart import Instamart
from app.core.stores.zepto import Zepto
from app.schemas.schemas import Product


class ScraperManager:
    def __init__(self, lat, lon):
        self.scrapers = {
            'blinkit': Blinkit(lat, lon),
            'instamart': Instamart(lat, lon),
            'zepto': Zepto(lat, lon)
        }

    async def get_products(self, query: str) -> List[Product]:
        scraper_tasks = [
            scraper.get_products(query)
            for scraper in self.scrapers.values()
        ]
        combined_results = await asyncio.gather(*scraper_tasks)
        return [
            product
            for result in combined_results
            for product in result
        ]
