import pytest
from agents.sql_validator import validate_sql, ValidationError
def test_allows_select():
    assert validate_sql("SELECT name FROM products LIMIT ?", [5])
def test_blocks_delete():
    with pytest.raises(ValidationError): validate_sql("DELETE FROM products WHERE id=1")
def test_blocks_drop():
    with pytest.raises(ValidationError): validate_sql("DROP TABLE products")
def test_blocks_multiple_statements():
    with pytest.raises(ValidationError): validate_sql("SELECT * FROM products LIMIT 5; DELETE FROM products")
def test_blocks_non_select():
    with pytest.raises(ValidationError): validate_sql("UPDATE products SET price=1")
def test_requires_limit():
    with pytest.raises(ValidationError): validate_sql("SELECT * FROM products")
