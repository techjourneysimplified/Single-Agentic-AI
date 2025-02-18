import datetime
import random
import uuid
from typing import List, Dict
from .connection import DatabaseConnection

class DataPopulator:
    @staticmethod
    def generate_sample_products() -> List[Dict]:
        """Generate sample product data"""
        return [
            {
                "product_id": "P001",
                "name": "Gaming Mouse",
                "current_stock": 25,
                "reorder_threshold": 30,
                "supplier_email": "techjourneysimplified@gmail.com",
                "unit_price": 45.99,
                "supplier_name": "Tech Peripherals Inc"
            },
            {
                "product_id": "P002",
                "name": "Mechanical Keyboard",
                "current_stock": 15,
                "reorder_threshold": 20,
                "supplier_email": "techjourneysimplified@gmail.com",
                "unit_price": 89.99,
                "supplier_name": "Tech Peripherals Inc"
            },
            {
                "product_id": "P003",
                "name": "Gaming Headset",
                "current_stock": 35,
                "reorder_threshold": 25,
                "supplier_email": "techjourneysimplified@gmail.com",
                "unit_price": 79.99,
                "supplier_name": "Audio Tech Ltd"
            },
            # Add more products here...
        ]

    @staticmethod
    def generate_sample_sales() -> List[Dict]:
        """Generate 30 days of sample sales data"""
        sales = []
        products = ["P001", "P002", "P003"]
        
        # Generate sales for last 30 days
        for day in range(30):
            date = (datetime.datetime.now() - datetime.timedelta(days=day)).date()
            
            # Generate 1-5 transactions per day for each product
            for product_id in products:
                for _ in range(1, 6):
                    sales.append({
                        "transaction_id": f"T{uuid.uuid4().hex[:8]}",
                        "product_id": product_id,
                        "quantity": random.randint(1, 5),
                        "sale_date": date,
                        "sale_price": 0.0  # Will be updated based on product
                    })
        return sales

    @staticmethod
    def populate_database():
        """Populate the database with sample data"""
        with DatabaseConnection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Populate products
            products = DataPopulator.generate_sample_products()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO products 
                (product_id, name, current_stock, reorder_threshold, 
                supplier_email, unit_price, supplier_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [(p["product_id"], p["name"], p["current_stock"], 
                  p["reorder_threshold"], p["supplier_email"], 
                  p["unit_price"], p["supplier_name"]) for p in products]
            )

            # Populate sales transactions
            sales = DataPopulator.generate_sample_sales()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO sales_transactions 
                (transaction_id, product_id, quantity, sale_date, sale_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                [(s["transaction_id"], s["product_id"], s["quantity"], 
                  s["sale_date"], s["sale_price"]) for s in sales]
            )

def initialize_and_populate_db():
    """Initialize database and populate with sample data only if empty"""
    DatabaseConnection.initialize_database()
    
    # Check if database is empty
    with DatabaseConnection.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        if product_count == 0:
            DataPopulator.populate_database()