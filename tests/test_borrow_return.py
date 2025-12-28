"""
Tests for BorrowBook and ReturnBook SOAP operations.

Tests:
- test_borrow_available: Borrow an available book
- test_return_borrowed: Return a borrowed book
- test_borrow_nonexistent: Borrow non-existent book (BookNotFoundFault)
- test_borrow_unavailable: Borrow already borrowed book (BookNotAvailableFault)
- test_return_not_borrowed: Return a book that isn't borrowed (InvalidInputFault)
- test_borrow_empty_name: Borrow with empty borrower name (InvalidInputFault)
"""
import pytest
from zeep.exceptions import Fault
import uuid


class TestBorrowBook:
    """Tests for BorrowBook operation."""

    def test_borrow_available_book(self, service, book_factory):
        """
        Test #8: BorrowBook on available book returns BorrowResult.

        Expected: BorrowResult with success=True, due_date, message
        """
        # Create a fresh book to borrow (to avoid test interference)
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(
            title="Book to Borrow",
            author="Author",
            isbn=unique_isbn
        )
        created = service.AddBook(book_input)

        try:
            # Borrow the book
            result = service.BorrowBook(created.id, "Test Borrower")

            assert result is not None
            assert result.success is True
            assert result.due_date is not None
            assert result.message is not None
            assert "successfully borrowed" in result.message.lower() or "Book to Borrow" in result.message

            # Verify book is now unavailable
            book = service.GetBook(created.id)
            assert book.available is False
            assert book.borrower == "Test Borrower"

        finally:
            # Cleanup - return and delete
            try:
                service.ReturnBook(created.id)
            except:
                pass
            service.DeleteBook(created.id)

    def test_borrow_nonexistent_book(self, service):
        """
        Test #12: BorrowBook with non-existent ID raises BookNotFoundFault.

        Expected: SOAP Fault with faultcode Client.BookNotFound
        """
        with pytest.raises(Fault) as exc_info:
            service.BorrowBook(9999, "Test Borrower")

        assert "BookNotFound" in str(exc_info.value.message) or "9999" in str(exc_info.value.message)

    def test_borrow_unavailable_book(self, service):
        """
        Test #13: BorrowBook on already borrowed book raises BookNotAvailableFault.

        Expected: SOAP Fault with faultcode Client.BookNotAvailable
        """
        # Book ID 4 (Pride and Prejudice) is borrowed by John Smith in seed data
        with pytest.raises(Fault) as exc_info:
            service.BorrowBook(4, "Another Borrower")

        fault_message = str(exc_info.value.message)
        assert "BookNotAvailable" in fault_message or "borrowed" in fault_message.lower()

    def test_borrow_empty_borrower_name(self, service):
        """
        Test #17: BorrowBook with empty borrower_name raises InvalidInputFault.

        Expected: SOAP Fault with faultcode Client.InvalidInput
        """
        # Use an available book
        with pytest.raises(Fault) as exc_info:
            service.BorrowBook(1, "")

        fault_message = str(exc_info.value.message)
        assert "InvalidInput" in fault_message or "borrower" in fault_message.lower()

    def test_borrow_whitespace_borrower_name(self, service):
        """BorrowBook with whitespace-only borrower name raises InvalidInputFault."""
        with pytest.raises(Fault) as exc_info:
            service.BorrowBook(1, "   ")

        fault_message = str(exc_info.value.message)
        assert "InvalidInput" in fault_message or "borrower" in fault_message.lower()

    def test_borrow_returns_due_date_in_future(self, service, book_factory):
        """Verify BorrowBook returns a due_date that is in the future."""
        from datetime import datetime

        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(isbn=unique_isbn)
        created = service.AddBook(book_input)

        try:
            result = service.BorrowBook(created.id, "Tester")

            # due_date should be in the future (typically 14 days)
            assert result.due_date is not None
            # Note: zeep returns datetime object
            if hasattr(result.due_date, 'date'):
                assert result.due_date > datetime.now()

        finally:
            try:
                service.ReturnBook(created.id)
            except:
                pass
            service.DeleteBook(created.id)


class TestReturnBook:
    """Tests for ReturnBook operation."""

    def test_return_borrowed_book(self, service, book_factory):
        """
        Test #9: ReturnBook on borrowed book returns True.

        Expected: Boolean True, book becomes available again
        """
        # Create and borrow a book
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(isbn=unique_isbn)
        created = service.AddBook(book_input)

        try:
            # Borrow the book
            service.BorrowBook(created.id, "Tester")

            # Return the book
            result = service.ReturnBook(created.id)

            assert result is True

            # Verify book is available again
            book = service.GetBook(created.id)
            assert book.available is True
            assert book.borrower is None or book.borrower == ""

        finally:
            service.DeleteBook(created.id)

    def test_return_not_borrowed_book(self, service):
        """
        Test #16: ReturnBook on available book raises InvalidInputFault.

        Expected: SOAP Fault - book is not currently borrowed
        """
        # Book ID 1 (The Great Gatsby) is available in seed data
        with pytest.raises(Fault) as exc_info:
            service.ReturnBook(1)

        fault_message = str(exc_info.value.message)
        assert "InvalidInput" in fault_message or "not" in fault_message.lower()

    def test_return_nonexistent_book(self, service):
        """ReturnBook with non-existent ID raises BookNotFoundFault."""
        with pytest.raises(Fault) as exc_info:
            service.ReturnBook(9999)

        assert "BookNotFound" in str(exc_info.value.message) or "9999" in str(exc_info.value.message)

    def test_return_seed_borrowed_book(self, service):
        """
        Return one of the seed borrowed books.

        Note: This modifies seed data - book ID 4 (Pride and Prejudice)
        After test, re-borrow to restore state.
        """
        # Return the book
        result = service.ReturnBook(4)
        assert result is True

        # Verify it's available
        book = service.GetBook(4)
        assert book.available is True

        # Re-borrow to restore seed state
        service.BorrowBook(4, "John Smith")

    def test_borrow_return_cycle(self, service, book_factory):
        """Test complete borrow-return cycle."""
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(isbn=unique_isbn)
        created = service.AddBook(book_input)

        try:
            # Initially available
            book = service.GetBook(created.id)
            assert book.available is True

            # Borrow
            service.BorrowBook(created.id, "Cycle Tester")
            book = service.GetBook(created.id)
            assert book.available is False

            # Return
            service.ReturnBook(created.id)
            book = service.GetBook(created.id)
            assert book.available is True

            # Borrow again
            service.BorrowBook(created.id, "Second Borrower")
            book = service.GetBook(created.id)
            assert book.available is False
            assert book.borrower == "Second Borrower"

        finally:
            try:
                service.ReturnBook(created.id)
            except:
                pass
            service.DeleteBook(created.id)
