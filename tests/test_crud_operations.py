"""
Tests for AddBook, UpdateBook, DeleteBook SOAP operations.

Tests:
- test_add_valid_book: Add a new book with valid data
- test_update_book: Update existing book
- test_delete_book: Delete a book
- test_add_empty_title: Add book with empty title (InvalidInputFault)
- test_add_duplicate_isbn: Add book with existing ISBN (DuplicateISBNFault)
"""
import pytest
from zeep.exceptions import Fault
import uuid


class TestAddBook:
    """Tests for AddBook operation."""

    def test_add_valid_book(self, service, book_factory):
        """
        Test #3: AddBook with valid data creates and returns new book.

        Expected: Book object with generated ID
        """
        # Generate unique ISBN to avoid duplicates
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"

        book_input = book_factory(
            title="Test Book for Add",
            author="Test Author",
            isbn=unique_isbn,
            year=2024,
            genre="Test Genre"
        )

        result = service.AddBook(book_input)

        assert result is not None
        assert result.id is not None
        assert result.id > 0
        assert result.title == "Test Book for Add"
        assert result.author == "Test Author"
        assert result.isbn == unique_isbn
        assert result.year == 2024
        assert result.genre == "Test Genre"
        assert result.available is True

        # Cleanup - delete the created book
        service.DeleteBook(result.id)

    def test_add_book_with_minimal_fields(self, service, book_factory):
        """Test AddBook with only required fields (title, author, isbn)."""
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"

        book_input = book_factory(
            title="Minimal Book",
            author="Minimal Author",
            isbn=unique_isbn,
            year=None,
            genre=None
        )

        result = service.AddBook(book_input)

        assert result is not None
        assert result.id > 0
        assert result.title == "Minimal Book"

        # Cleanup
        service.DeleteBook(result.id)

    def test_add_empty_title(self, service, book_factory):
        """
        Test #14: AddBook with empty title raises InvalidInputFault.

        Expected: SOAP Fault with faultcode Client.InvalidInput
        """
        book_input = book_factory(
            title="",
            author="Author",
            isbn="978-0000000001"
        )

        with pytest.raises(Fault) as exc_info:
            service.AddBook(book_input)

        assert "InvalidInput" in str(exc_info.value.message) or "title" in str(exc_info.value.message).lower()

    def test_add_empty_author(self, service, book_factory):
        """Test AddBook with empty author raises InvalidInputFault."""
        book_input = book_factory(
            title="Title",
            author="",
            isbn="978-0000000002"
        )

        with pytest.raises(Fault) as exc_info:
            service.AddBook(book_input)

        assert "InvalidInput" in str(exc_info.value.message) or "author" in str(exc_info.value.message).lower()

    def test_add_empty_isbn(self, service, book_factory):
        """Test AddBook with empty ISBN raises InvalidInputFault."""
        book_input = book_factory(
            title="Title",
            author="Author",
            isbn=""
        )

        with pytest.raises(Fault) as exc_info:
            service.AddBook(book_input)

        assert "InvalidInput" in str(exc_info.value.message) or "isbn" in str(exc_info.value.message).lower()

    def test_add_duplicate_isbn(self, service, book_factory):
        """
        Test #15: AddBook with existing ISBN raises DuplicateISBNFault.

        Expected: SOAP Fault with faultcode Client.DuplicateISBN
        """
        # Use ISBN from seed data (The Great Gatsby)
        existing_isbn = "978-0743273565"

        book_input = book_factory(
            title="Duplicate ISBN Book",
            author="Some Author",
            isbn=existing_isbn
        )

        with pytest.raises(Fault) as exc_info:
            service.AddBook(book_input)

        assert "DuplicateISBN" in str(exc_info.value.message) or existing_isbn in str(exc_info.value.message)


class TestUpdateBook:
    """Tests for UpdateBook operation."""

    def test_update_book(self, service, book_factory):
        """
        Test #4: UpdateBook modifies existing book.

        Expected: Updated Book object
        """
        # First, create a book to update
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(
            title="Original Title",
            author="Original Author",
            isbn=unique_isbn
        )
        created = service.AddBook(book_input)

        # Update the book
        update_input = book_factory(
            title="Updated Title",
            author="Updated Author",
            isbn=unique_isbn,
            year=2025,
            genre="Updated Genre"
        )

        result = service.UpdateBook(created.id, update_input)

        assert result is not None
        assert result.id == created.id
        assert result.title == "Updated Title"
        assert result.author == "Updated Author"
        assert result.year == 2025
        assert result.genre == "Updated Genre"

        # Cleanup
        service.DeleteBook(created.id)

    def test_update_nonexistent_book(self, service, book_factory):
        """Test UpdateBook with non-existent ID raises BookNotFoundFault."""
        book_input = book_factory()

        with pytest.raises(Fault) as exc_info:
            service.UpdateBook(9999, book_input)

        assert "BookNotFound" in str(exc_info.value.message) or "9999" in str(exc_info.value.message)

    def test_update_partial_fields(self, service, book_factory):
        """Test UpdateBook with only some fields changed."""
        # Create a book
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(
            title="Original",
            author="Original Author",
            isbn=unique_isbn,
            year=2020,
            genre="Original Genre"
        )
        created = service.AddBook(book_input)

        # Update only title
        update_input = book_factory(
            title="Only Title Changed",
            author="Original Author",
            isbn=unique_isbn,
            year=2020,
            genre="Original Genre"
        )

        result = service.UpdateBook(created.id, update_input)

        assert result.title == "Only Title Changed"
        assert result.author == "Original Author"

        # Cleanup
        service.DeleteBook(created.id)


class TestDeleteBook:
    """Tests for DeleteBook operation."""

    def test_delete_book(self, service, book_factory):
        """
        Test #5: DeleteBook removes book and returns True.

        Expected: Boolean True
        """
        # Create a book to delete
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(
            title="Book to Delete",
            author="Delete Author",
            isbn=unique_isbn
        )
        created = service.AddBook(book_input)

        # Delete the book
        result = service.DeleteBook(created.id)

        assert result is True

        # Verify deletion - GetBook should raise fault
        with pytest.raises(Fault):
            service.GetBook(created.id)

    def test_delete_nonexistent_book(self, service):
        """
        Test #11: DeleteBook with non-existent ID raises BookNotFoundFault.

        Expected: SOAP Fault with faultcode Client.BookNotFound
        """
        with pytest.raises(Fault) as exc_info:
            service.DeleteBook(9999)

        assert "BookNotFound" in str(exc_info.value.message) or "9999" in str(exc_info.value.message)

    def test_delete_book_twice(self, service, book_factory):
        """Test deleting the same book twice raises BookNotFoundFault."""
        # Create and delete a book
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(isbn=unique_isbn)
        created = service.AddBook(book_input)

        # First delete succeeds
        service.DeleteBook(created.id)

        # Second delete should fail
        with pytest.raises(Fault) as exc_info:
            service.DeleteBook(created.id)

        fault_message = str(exc_info.value.message)
        assert "not found" in fault_message.lower() or str(created.id) in fault_message
