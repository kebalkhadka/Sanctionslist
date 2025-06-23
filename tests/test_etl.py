import sys
import os
from unittest.mock import patch

# Add project root to Python path so `etl` can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from etl.etl import test_db_connection

def test_db_connection_returns_boolean():
    """Ensure the function returns True or False (i.e., a boolean)"""
    result = test_db_connection()
    assert isinstance(result, bool)

@patch("etl.etl.get_connection")
def test_db_connection_success(mock_get_conn):
    """Simulate successful DB connection"""
    mock_conn = mock_get_conn.return_value
    mock_conn.close = lambda: None  # mock the .close() method
    result = test_db_connection()
    assert result is True

@patch("etl.etl.get_connection", return_value=None)
def test_db_connection_failure(mock_get_conn):
    """Simulate DB connection failure (returns None)"""
    result = test_db_connection()
    assert result is False

