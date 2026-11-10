"""Config for Project 18."""
import pathlib
BASE_DIR = pathlib.Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "sample.db"
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
MAX_ROWS = 100
QUERY_TIMEOUT = 5.0  # seconds

SCHEMA = {
    "products": ["id", "name", "category", "price", "stock"],
    "customers": ["id", "name", "city", "email"],
    "orders": ["id", "customer_id", "product_id", "quantity", "total_amount", "order_date"],
}
