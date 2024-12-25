from typing import List

from pydantic import BaseModel


class ProductImage(BaseModel):
    best_quality: str
    low_quality: str


class Product(BaseModel):
    source: str
    currency: str
    is_variation: bool
    product_id: str
    brand: str
    name: str
    similar_with_id: str
    weight: str
    total_savings: float
    mrp_price: float
    store_price: float
    availability: bool
    max_in_cart: int
    inventory: int
    category: str
    deep_link: str
    best_quality: str
    low_quality: str


class ProductsResponse(BaseModel):
    success: bool
    products: List[Product] | None


class Atc(BaseModel):
    product_id: str
    brand: str
    name: str
    images: ProductImage
    items_in_cart: int
    weight: str
    total_savings: float
    mrp_price: float
    store_price: float
    availability: bool
    max_in_cart: int
    inventory: int
