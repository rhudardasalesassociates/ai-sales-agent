import gspread
from google.oauth2.service_account import Credentials
from loguru import logger
from typing import List, Dict, Optional
import os

from app.config import settings


class ProductService:
    def __init__(self):
        self.products: List[Dict] = []
        self.gc = None
        self.spreadsheet = None

    async def load_products(self) -> List[Dict]:
        try:
            if os.path.exists(settings.google_sheets_credentials_file):
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]

                creds = Credentials.from_service_account_file(
                    settings.google_sheets_credentials_file,
                    scopes=scopes
                )
                self.gc = gspread.authorize(creds)

                if settings.google_sheets_url:
                    self.spreadsheet = self.gc.open_by_url(settings.google_sheets_url)
                    self.products = self._fetch_products_from_sheet()
                    logger.info(f"Loaded {len(self.products)} products from Google Sheets")
            else:
                logger.warning("Google Sheets credentials file not found, using demo products")
                self.products = self._get_demo_products()

            return self.products

        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.products = self._get_demo_products()
            return self.products

    def _fetch_products_from_sheet(self) -> List[Dict]:
        try:
            worksheet = self.spreadsheet.sheet1
            records = worksheet.get_all_records()

            products = []
            for i, record in enumerate(records):
                product = {
                    "id": str(i + 1),
                    "name": record.get("name", record.get("Name", "")),
                    "description": record.get("description", record.get("Description", "")),
                    "price": float(record.get("price", record.get("Price", 0))),
                    "category": record.get("category", record.get("Category", "")),
                    "in_stock": record.get("in_stock", record.get("In Stock", "Yes")).lower() in ["yes", "true", "1"],
                    "image_url": record.get("image_url", record.get("Image URL", "")),
                    "features": record.get("features", record.get("Features", "")).split(",") if record.get("features", record.get("Features", "")) else []
                }
                products.append(product)

            return products

        except Exception as e:
            logger.error(f"Error fetching products from sheet: {e}")
            return self._get_demo_products()

    async def get_products(self) -> List[Dict]:
        if not self.products:
            await self.load_products()
        return self.products

    async def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        for product in self.products:
            if product.get("id") == product_id:
                return product
        return None

    async def search_products(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        results = []
        for product in self.products:
            if (query_lower in product.get("name", "").lower() or
                query_lower in product.get("description", "").lower() or
                query_lower in product.get("category", "").lower()):
                results.append(product)
        return results

    async def get_products_by_category(self, category: str) -> List[Dict]:
        return [p for p in self.products if p.get("category", "").lower() == category.lower()]

    async def get_categories(self) -> List[str]:
        categories = set()
        for product in self.products:
            if product.get("category"):
                categories.add(product["category"])
        return list(categories)

    def _get_demo_products(self) -> List[Dict]:
        return [
            {
                "id": "1",
                "name": "Premium Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
                "price": 199.99,
                "category": "Electronics",
                "in_stock": True,
                "image_url": "https://example.com/headphones.jpg",
                "features": ["Noise Cancellation", "30-hour battery", "Bluetooth 5.0", "Built-in microphone"]
            },
            {
                "id": "2",
                "name": "Smart Fitness Watch",
                "description": "Track your health and fitness with this advanced smartwatch featuring heart rate monitoring.",
                "price": 299.99,
                "category": "Electronics",
                "in_stock": True,
                "image_url": "https://example.com/watch.jpg",
                "features": ["Heart Rate Monitor", "GPS", "Water Resistant", "Sleep Tracking"]
            },
            {
                "id": "3",
                "name": "Organic Cotton T-Shirt",
                "description": "Comfortable and sustainable organic cotton t-shirt available in multiple colors.",
                "price": 34.99,
                "category": "Clothing",
                "in_stock": True,
                "image_url": "https://example.com/tshirt.jpg",
                "features": ["100% Organic Cotton", "Machine Washable", "Multiple Colors", "Eco-Friendly"]
            },
            {
                "id": "4",
                "name": "Professional Blender",
                "description": "Powerful blender for smoothies, soups, and food preparation with 10-speed settings.",
                "price": 149.99,
                "category": "Kitchen",
                "in_stock": True,
                "image_url": "https://example.com/blender.jpg",
                "features": ["10-Speed Settings", "1500W Motor", "BPA-Free", "Easy Clean"]
            },
            {
                "id": "5",
                "name": "Ergonomic Office Chair",
                "description": "Comfortable office chair with lumbar support and adjustable armrests.",
                "price": 449.99,
                "category": "Furniture",
                "in_stock": True,
                "image_url": "https://example.com/chair.jpg",
                "features": ["Lumbar Support", "Adjustable Height", "Breathable Mesh", "10-Year Warranty"]
            }
        ]