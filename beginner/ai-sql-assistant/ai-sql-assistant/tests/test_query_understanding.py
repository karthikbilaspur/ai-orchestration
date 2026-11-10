from agents.query_understanding import parse_question
def test_top_products():
    i = parse_question("What are the top 5 highest-selling products?")
    assert i.intent_type == "top_products" and i.limit == 5
def test_revenue_by_category():
    assert parse_question("Show total revenue by category").intent_type == "revenue_by_category"
def test_min_amount():
    i = parse_question("Which customers spent more than 5000?")
    assert i.intent_type == "top_customers" and i.min_amount == 5000
def test_default_limit():
    assert parse_question("Show top products").limit == 5
