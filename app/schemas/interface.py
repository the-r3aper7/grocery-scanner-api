from typing import List, Any

from app.schemas.schemas import Product


class ScraperBase:
    def get_products(self, query: str) -> List[Product]:
        pass

    def parse_data(self, data: Any):
        pass
