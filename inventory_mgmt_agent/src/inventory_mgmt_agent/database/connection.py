from sqlite3 import Connection, Cursor, Row, connect
from contextlib import contextmanager
from typing import Generator

from ..config import DB_PATH
import logging

logger = logging.getLogger(__name__) # __name__ for current file

PRODUCTS_TABLE = "products"
SALES_TRANSACTIONS_TABLE = "sales_transactions"
PURCHASE_ORDERS_TABLE = "purchase_orders"

class DatabaseConnection:
    @staticmethod
    @contextmanager
    def get_connection() -> Generator[Connection, None, None]:
        """Create a context manager for database connections
        
        Returns:
            Generator[Connection, None, None]: SQLite database connection
            
        Raises:
            sqlite3.Error: If database connection fails
            Exception: For other unexpected errors
        """
        logger.info("Creating new database connection")
        conn = connect(DB_PATH)
        conn.row_factory = Row  # This enables column access by name
        try:
            yield conn
            conn.commit()
            logger.info("Database connection established successfully")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
        finally:
            conn.close()
    @staticmethod
    def initialize_database() -> None:
        """Create database tables if they don't exist and manage schema versions
        
        Raises:
            sqlite3.Error: If table creation fails
        """
        print("Initializing database ================================")
        with DatabaseConnection.get_connection() as conn:
            cursor: Cursor = conn.cursor()
            
            print("Creating schema_version table")
            # Create schema_version table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("products table")
            # Create products table
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {PRODUCTS_TABLE} (
                    product_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    current_stock INTEGER NOT NULL,
                    reorder_threshold INTEGER NOT NULL,
                    supplier_email TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    supplier_name TEXT NOT NULL
                )
            ''')
            print("sales_transactions table")
            # Create sales_transactions table
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {SALES_TRANSACTIONS_TABLE} (
                    transaction_id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    sale_date DATE NOT NULL,
                    sale_price REAL NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES {PRODUCTS_TABLE}(product_id)
                )
            ''')
            print("purchase_orders table")  
            # Create purchase_orders table
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {PURCHASE_ORDERS_TABLE} (
                    po_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    order_date DATETIME NOT NULL,
                    status TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES {PRODUCTS_TABLE}(product_id)
                )
            ''')
        

            # Create indices for foreign keys
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_sales_product_id 
                ON {SALES_TRANSACTIONS_TABLE}(product_id)
            ''')
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_po_product_id 
                ON {PURCHASE_ORDERS_TABLE}(product_id)
            ''')