"""
Pytest configuration and fixtures for SOAP Library Catalog tests.

Usage:
    1. Start the SOAP service: docker-compose up -d
    2. Run tests: pytest tests/ -v
"""
import pytest
from zeep import Client
from zeep.exceptions import Fault

# SOAP service configuration
WSDL_URL = "http://localhost:8000/?wsdl"


@pytest.fixture(scope="session")
def soap_client():
    """
    Create a Zeep SOAP client for the entire test session.

    The client is reused across all tests for efficiency.
    """
    try:
        client = Client(WSDL_URL)
        return client
    except Exception as e:
        pytest.skip(f"SOAP service not available: {e}")


@pytest.fixture
def service(soap_client):
    """
    Get the SOAP service proxy for making operation calls.

    Usage in tests:
        def test_get_book(service):
            result = service.GetBook(1)
            assert result.id == 1
    """
    return soap_client.service


@pytest.fixture
def book_factory(soap_client):
    """
    Factory fixture for creating BookInput objects.

    Usage:
        book = book_factory(title="Test", author="Author", isbn="123")
    """
    # BookInput is in the types namespace
    book_type = soap_client.get_type('{http://library.example.com/types}BookInput')

    def _create_book(title="Test Book", author="Test Author",
                     isbn="978-1234567890", year=2024, genre="Test"):
        return book_type(
            title=title,
            author=author,
            isbn=isbn,
            year=year,
            genre=genre
        )

    return _create_book


def assert_soap_fault(exc_info, expected_fault_code):
    """
    Helper to assert SOAP fault details.

    Args:
        exc_info: pytest.raises exception info
        expected_fault_code: Expected faultcode (e.g., "Client.BookNotFound")
    """
    fault = exc_info.value
    assert expected_fault_code in str(fault.message), \
        f"Expected fault code '{expected_fault_code}' not found in '{fault.message}'"


# Test data - seed data from database
SEED_BOOKS = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "978-0743273565", "genre": "Fiction", "available": True},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "978-0061120084", "genre": "Fiction", "available": True},
    {"id": 3, "title": "1984", "author": "George Orwell", "isbn": "978-0451524935", "genre": "Dystopian", "available": True},
    {"id": 4, "title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "978-0141439518", "genre": "Romance", "available": False},  # Borrowed
    {"id": 5, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "isbn": "978-0316769488", "genre": "Fiction", "available": True},
    {"id": 6, "title": "Brave New World", "author": "Aldous Huxley", "isbn": "978-0060850524", "genre": "Dystopian", "available": True},
    {"id": 7, "title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "978-0547928227", "genre": "Fantasy", "available": True},
    {"id": 8, "title": "Dune", "author": "Frank Herbert", "isbn": "978-0441172719", "genre": "Science Fiction", "available": False},  # Borrowed
]

# Books that are already borrowed (for testing BorrowBook fault)
BORROWED_BOOK_IDS = [4, 8]

# Books that are available (for testing successful borrow)
AVAILABLE_BOOK_IDS = [1, 2, 3, 5, 6, 7]
