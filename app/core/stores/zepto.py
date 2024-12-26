import logging
from typing import List

import httpx
from httpx import AsyncClient

from app.schemas.interface import ScraperBase
from app.schemas.schemas import Product


class Zepto(ScraperBase):
    def __init__(self, lat, lon, scraper: AsyncClient = httpx.AsyncClient()):
        self.scraper = scraper
        self.base_url = "https://api.zeptonow.com/api/v3/search"
        self.store_id_url = f"https://api.zeptonow.com/api/v1/config/layout/?latitude={lat}&longitude={lon}&page_type=HOME&version=v2"
        self.body = {"query": "", "pageNumber": 0, "mode": "AUTOSUGGEST"}
        self.headers = {
            "Accept": "*/*",
            "User-Agent": self.scraper.headers['User-Agent'],
            "appVersion": "12.24.0",
            "platform": "WEB",
            "Content-Type": "application/json",
        }

    async def get_store_id(self) -> str:
        try:
            response = await self.scraper.get(
                self.store_id_url,
                headers=self.headers
            )
            if response.status_code == 200:
                store_data = response.json()["storeServiceableResponse"]
                self.headers["storeId"] = store_data["storeId"]
                return store_data["storeId"]
        except Exception as e:
            logging.log(logging.WARN, f"Failed to get store id : {e}")
            return ""

    async def get_products(self, query) -> List[Product]:
        headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "storeId": await self.get_store_id(),
            "appVersion": "12.24.0",
            "platform": "WEB",
            "Content-Type": "application/json",
        }
        try:
            response = await self.scraper.post(
                "https://api.zeptonow.com/api/v3/search",
                json={"query": query, "pageNumber": 0, "mode": "AUTOSUGGEST"},
                headers=headers
            )
            return self.parse_data(response.json())
        except Exception as e:
            logging.log(logging.WARN, f"Request failed for {query} : {e}")
            return []

    def parse_data(self, data) -> List[Product]:
        all_products = []
        for widget in data["layout"]:
            if widget["widgetId"] == "PRODUCT_GRID":
                products = widget["data"]["resolver"]["data"]["items"]
                all_products.extend(products)

        transformed_products = []
        for item in all_products:
            product_data = item["productResponse"]

            images = product_data["productVariant"]["images"]
            best_quality_img = images[0]["path"] if images else ""
            low_quality_img = images[-1]["path"] if images else ""

            mrp = float(product_data["mrp"]) / 100
            selling_price = float(product_data["sellingPrice"]) / 100
            savings = mrp - selling_price

            product = Product(
                source="zepto",
                product_id=product_data["id"],
                brand=product_data["product"]["brand"],
                name=product_data["product"]["name"],
                weight=f"{product_data['productVariant']['packsize']} {product_data['productVariant']['unitOfMeasure'].lower()}",
                total_savings=savings,
                mrp_price=mrp,
                store_price=selling_price,
                availability=not product_data["outOfStock"],
                max_in_cart=product_data["productVariant"]["maxAllowedQuantity"],
                inventory=product_data["availableQuantity"],
                category=product_data["primaryCategoryName"],
                best_quality=best_quality_img,
                low_quality=low_quality_img,
                currency="INR",
                deep_link="",
                is_variation=False,
                similar_with_id=""
            )
            transformed_products.append(product)
        return transformed_products
