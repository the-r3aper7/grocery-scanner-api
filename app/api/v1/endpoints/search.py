import logging

from fastapi import APIRouter

from app.core.stores.blinkit import Blinkit
from app.core.stores.instamart import Instamart
from app.core.stores.manager import ScraperManager
from app.core.stores.zepto import Zepto
from app.schemas.enums import StoresEnum
from app.schemas.schemas import ProductsResponse

router = APIRouter()


@router.get("/products/{query}")
async def get_products_route(query: str, lat: str, lon: str) -> ProductsResponse:
    try:
        manager = ScraperManager(lat, lon)
        products = await manager.get_products(query)
        return ProductsResponse(
            success=True,
            products=products
        )
    except Exception as e:
        logging.log(logging.WARN, e)
        return ProductsResponse(
            success=False,
            products=None
        )


@router.get("/products/{store}/{query}")
async def get_products_route(store: StoresEnum, query: str, lat: str, lon: str) -> ProductsResponse:
    try:
        if store == StoresEnum.BLINKIT:
            blinkit = Blinkit(lat, lon)
            products = await blinkit.get_products(query)
            return ProductsResponse(
                success=True,
                products=products
            )
        if store == StoresEnum.INSTAMART:
            instamart = Instamart(lat, lon)
            products = await instamart.get_products(query)
            return ProductsResponse(
                success=True,
                products=products
            )
        if store == StoresEnum.ZEPTO:
            zepto = Zepto(lat, lon)
            products = await zepto.get_products(query)
            return ProductsResponse(
                success=True,
                products=products
            )
    except Exception as e:
        logging.log(logging.WARN, e)
        return ProductsResponse(
            success=False,
            products=None
        )
