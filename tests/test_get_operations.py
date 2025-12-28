"""
Tests for GetBook and GetAllBooks SOAP operations.

Tests:
- test_get_existing_book: Get a book that exists (ID 1)
- test_get_all_books: Get all books (should return 8)
- test_get_nonexistent_book: Get book with invalid ID (should raise BookNotFoundFault)
"""
import pytest
from zeep.exceptions import Fault


class TestGetBook:
    """Tests for GetBook operation."""

    def test_get_existing_book(self, service):
        """
        Test #1: GetBook with valid ID returns correct book.

        Expected: Book with ID 1 (The Great Gatsby)
        """
        result = service.GetBook(1)

        assert result is not None
        assert result.id == 1
        assert result.title == "The Great Gatsby"
        assert result.author == "F. Scott Fitzgerald"
        assert result.isbn == "978-0743273565"
        assert result.genre == "Fiction"
        assert result.available is True

    def test_get_book_returns_all_fields(self, service):
        """Verify all Book fields are returned correctly."""
        result = service.GetBook(3)

        assert result.id == 3
        assert result.title == "1984"
        assert result.author == "George Orwell"
        assert result.isbn == "978-0451524935"
        assert result.year == 1949
        assert result.genre == "Dystopian"
        assert result.available is True
        # borrower should be None/empty for available book
        assert result.borrower is None or result.borrower == ""

    def test_get_borrowed_book(self, service):
        """Test getting a book that is currently borrowed."""
        result = service.GetBook(4)  # Pride and Prejudice - borrowed

        assert result.id == 4
        assert result.available is False
        assert result.borrower is not None
        assert result.borrower == "John Smith"

    def test_get_nonexistent_book(self, service):
        """
        Test #10: GetBook with non-existent ID raises BookNotFoundFault.

        Expected: SOAP Fault with faultcode Client.BookNotFound
        """
        with pytest.raises(Fault) as exc_info:
            service.GetBook(9999)

        fault = exc_info.value
        assert "BookNotFound" in str(fault.message) or "9999" in str(fault.message)

    def test_get_book_with_zero_id(self, service):
        """Test GetBook with ID 0 (edge case)."""
        with pytest.raises(Fault) as exc_info:
            service.GetBook(0)

        # Should raise BookNotFoundFault
        assert "BookNotFound" in str(exc_info.value.message) or "not found" in str(exc_info.value.message).lower()

    def test_get_book_with_negative_id(self, service):
        """Test GetBook with negative ID (edge case)."""
        with pytest.raises(Fault) as exc_info:
            service.GetBook(-1)

        assert "BookNotFound" in str(exc_info.value.message) or "not found" in str(exc_info.value.message).lower()


class TestGetAllBooks:
    """Tests for GetAllBooks operation."""

    def test_get_all_books(self, service):
        """
        Test #2: GetAllBooks returns all 8 seed books.

        Expected: Array of 8 Book objects
        """
        result = service.GetAllBooks()

        assert result is not None
        assert len(result) >= 8  # At least 8 seed books

    def test_get_all_books_contains_expected_titles(self, service):
        """Verify GetAllBooks contains expected seed book titles."""
        result = service.GetAllBooks()

        titles = [book.title for book in result]

        expected_titles = [
            "The Great Gatsby",
            "To Kill a Mockingbird",
            "1984",
            "Pride and Prejudice",
        ]

        for title in expected_titles:
            assert title in titles, f"Expected title '{title}' not found in results"

    def test_get_all_books_returns_complete_objects(self, service):
        """Verify each book in GetAllBooks has all required fields."""
        result = service.GetAllBooks()

        for book in result:
            assert book.id is not None
            assert book.title is not None
            assert book.author is not None
            assert book.isbn is not None
            assert book.available is not None
