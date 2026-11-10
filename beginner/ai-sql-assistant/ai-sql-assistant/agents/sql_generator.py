"""Agent 2: SQL Generator - Intent -> parameterized SQL."""
from agents.query_understanding import Intent

def generate_sql(intent: Intent) -> tuple[str, list]:
    """Returns (sql, params). All user values are params, never interpolated."""
    t = intent.intent_type
    limit = max(1, min(intent.limit, 100))
    if t == "top_products":
        sql = """SELECT p.name AS product, p.category, SUM(o.quantity) AS total_sold, SUM(o.total_amount) AS revenue
                 FROM orders o JOIN products p ON p.id=o.product_id GROUP BY p.id ORDER BY total_sold DESC LIMIT ?"""
        return sql, [limit]
    if t == "revenue_by_category":
        return ("SELECT p.category, SUM(o.total_amount) AS revenue, SUM(o.quantity) AS units FROM orders o JOIN products p ON p.id=o.product_id GROUP BY p.category ORDER BY revenue DESC LIMIT ?", [limit])
    if t == "top_customers":
        if intent.min_amount is not None:
            return ("SELECT c.name, c.city, SUM(o.total_amount) AS total_spent FROM orders o JOIN customers c ON c.id=o.customer_id GROUP BY c.id HAVING total_spent > ? ORDER BY total_spent DESC LIMIT ?", [intent.min_amount, limit])
        return ("SELECT c.name, c.city, SUM(o.total_amount) AS total_spent FROM orders o JOIN customers c ON c.id=o.customer_id GROUP BY c.id ORDER BY total_spent DESC LIMIT ?", [limit])
    if t == "total_revenue":
        return ("SELECT SUM(total_amount) AS total_revenue, COUNT(*) AS order_count FROM orders", [])
    if t == "list_products":
        if intent.category:
            return ("SELECT id, name, category, price, stock FROM products WHERE category=? ORDER BY name LIMIT ?", [intent.category, limit])
        return ("SELECT id, name, category, price, stock FROM products ORDER BY name LIMIT ?", [limit])
    if t == "orders_by_city":
        return ("SELECT c.city, COUNT(o.id) AS orders, SUM(o.total_amount) AS revenue FROM orders o JOIN customers c ON c.id=o.customer_id GROUP BY c.city ORDER BY revenue DESC LIMIT ?", [limit])
    # general fallback - safe default
    return ("SELECT p.name AS product, SUM(o.quantity) AS total_sold FROM orders o JOIN products p ON p.id=o.product_id GROUP BY p.id ORDER BY total_sold DESC LIMIT ?", [limit])
