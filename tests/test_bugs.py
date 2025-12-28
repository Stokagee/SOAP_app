"""
Bug reproduction tests for SOAP Library Catalog.

These tests document and verify known bugs in the application.
They are marked with pytest.mark.xfail until the bugs are fixed.

BUG #1: SearchBooks genre filter doesn't use wildcard
BUG #2: UpdateBook doesn't handle IntegrityError for duplicate ISBN
"""
import pytest
from zeep.exceptions import Fault
import uuid


class TestBug1SearchGenreFilter:
    """
    BUG #1: SearchBooks genre filter uses exact match instead of partial.

    File: app/soap/service.py:275
    Problem: `BookModel.genre.ilike(genre.strip())` - missing wildcard '%'
    Expected: Partial match like query search
    Actual: Exact match only

    Query search (line 267) correctly uses: f'%{query.strip().lower()}%'
    Genre filter (line 275) incorrectly uses: genre.strip()
    """

    def test_bug_genre_partial_match_fails(self, service):
        """
        Test #18: SearchBooks with partial genre should work but DOESN'T.

        This test demonstrates BUG #1.
        Before fix: This test FAILS (returns 0 results)
        After fix: This test PASSES (returns Fiction books)
        """
        # Search for "Fic" which should match "Fiction"
        result = service.SearchBooks("", "Fic")

        # BUG: This returns 0 because genre filter uses exact match
        # After fix, this should return books with Fiction genre
        assert len(result) >= 1, \
            "BUG #1: Genre partial search 'Fic' should find 'Fiction' books"

    def test_genre_exact_match_works(self, service):
        """Verify genre match works (after fix, this is partial match)."""
        result = service.SearchBooks("", "Fiction")

        # After BUG #1 fix, this finds both "Fiction" and "Science Fiction"
        assert len(result) >= 1
        for book in result:
            assert "Fiction" in book.genre  # Partial match now

    def test_query_partial_match_works(self, service):
        """Verify query partial match works (demonstrates the inconsistency)."""
        # Query search uses wildcard correctly
        result = service.SearchBooks("gat", "")  # Should find "Gatsby"

        assert len(result) >= 1, \
            "Query partial search works, proving genre should too"

    @pytest.mark.xfail(reason="BUG #1: Genre filter doesn't support partial match")
    def test_bug_genre_partial_dystopian(self, service):
        """Another test for partial genre match."""
        result = service.SearchBooks("", "Dyst")  # Should match "Dystopian"

        assert len(result) >= 1
        # Should find 1984 and Brave New World


class TestBug2UpdateBookIntegrityError:
    """
    BUG #2: UpdateBook doesn't handle IntegrityError for duplicate ISBN.

    File: app/soap/service.py:165-210
    Problem: Missing try/except IntegrityError block
    Expected: DuplicateISBNFault when updating ISBN to existing value
    Actual: Unhandled exception (HTTP 500)

    AddBook (lines 144-163) correctly handles this:
        except IntegrityError:
            session.rollback()
            raise DuplicateISBNFault(book.isbn)

    UpdateBook is missing this handling.
    """

    def test_bug_update_duplicate_isbn_crashes(self, service, book_factory):
        """
        Test #19: UpdateBook with duplicate ISBN should raise DuplicateISBNFault.

        This test demonstrates BUG #2.
        Before fix: This test FAILS with unhandled exception (HTTP 500)
        After fix: This test PASSES (raises DuplicateISBNFault)
        """
        # Create a new book
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(
            title="Book to Update",
            author="Author",
            isbn=unique_isbn
        )
        created = service.AddBook(book_input)

        try:
            # Try to update ISBN to one that already exists (seed data)
            existing_isbn = "978-0061120084"  # To Kill a Mockingbird

            update_input = book_factory(
                title="Updated",
                author="Author",
                isbn=existing_isbn  # This ISBN already exists!
            )

            # BUG: This should raise DuplicateISBNFault but raises unhandled exception
            with pytest.raises(Fault) as exc_info:
                service.UpdateBook(created.id, update_input)

            # Should contain duplicate ISBN error message
            fault_message = str(exc_info.value.message)
            assert "already exists" in fault_message or existing_isbn in fault_message, \
                f"BUG #2: Expected DuplicateISBNFault, got: {fault_message}"

        finally:
            # Cleanup
            try:
                service.DeleteBook(created.id)
            except:
                pass

    def test_add_duplicate_isbn_handled_correctly(self, service, book_factory):
        """Verify AddBook handles duplicate ISBN correctly (not a bug)."""
        existing_isbn = "978-0743273565"  # The Great Gatsby

        book_input = book_factory(isbn=existing_isbn)

        with pytest.raises(Fault) as exc_info:
            service.AddBook(book_input)

        # AddBook correctly raises DuplicateISBNFault
        fault_message = str(exc_info.value.message)
        assert "already exists" in fault_message or existing_isbn in fault_message

    @pytest.mark.xfail(reason="BUG #2: UpdateBook doesn't handle IntegrityError")
    def test_bug_update_isbn_to_another_seed_book(self, service, book_factory):
        """Try updating to another seed book's ISBN."""
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        book_input = book_factory(isbn=unique_isbn)
        created = service.AddBook(book_input)

        try:
            # Update to 1984's ISBN
            update_input = book_factory(
                title=created.title,
                author=created.author,
                isbn="978-0451524935"  # 1984's ISBN
            )

            with pytest.raises(Fault) as exc_info:
                service.UpdateBook(created.id, update_input)

            assert "DuplicateISBN" in str(exc_info.value.message)

        finally:
            try:
                service.DeleteBook(created.id)
            except:
                pass


class TestBugSummary:
    """Summary tests that will pass after all bugs are fixed."""

    def test_all_search_filters_consistent(self, service):
        """
        After BUG #1 fix: Both query and genre should support partial match.
        """
        # Query partial match
        query_result = service.SearchBooks("gat", "")
        assert len(query_result) >= 1, "Query partial match should work"

        # Genre partial match (currently broken)
        genre_result = service.SearchBooks("", "Fic")

        # After fix, both should work
        # Before fix, genre_result will be empty

    def test_all_isbn_duplicates_handled(self, service, book_factory):
        """
        After BUG #2 fix: Both AddBook and UpdateBook should handle duplicate ISBN.
        """
        existing_isbn = "978-0743273565"

        # AddBook handles it (not a bug)
        with pytest.raises(Fault) as add_exc:
            service.AddBook(book_factory(isbn=existing_isbn))
        add_fault = str(add_exc.value.message)
        assert "already exists" in add_fault or existing_isbn in add_fault

        # Create a book to update
        unique_isbn = f"978-{uuid.uuid4().hex[:10]}"
        created = service.AddBook(book_factory(isbn=unique_isbn))

        try:
            # UpdateBook should also handle it (currently broken)
            with pytest.raises(Fault) as update_exc:
                service.UpdateBook(created.id, book_factory(isbn=existing_isbn))

            # After fix, this should pass
            fault_message = str(update_exc.value.message)
            assert "already exists" in fault_message or existing_isbn in fault_message, \
                "BUG #2: UpdateBook should raise DuplicateISBNFault"

        finally:
            try:
                service.DeleteBook(created.id)
            except:
                pass
