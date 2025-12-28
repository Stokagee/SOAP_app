"""
Tests for SearchBooks SOAP operation.

Tests:
- test_search_by_query: Search by title/author
- test_search_by_genre: Search by exact genre
- test_search_empty_params: Search with empty parameters
- test_search_combined: Search with both query and genre
"""
import pytest
from zeep.exceptions import Fault


class TestSearchBooks:
    """Tests for SearchBooks operation."""

    def test_search_by_query_title(self, service):
        """
        Test #6: SearchBooks by title query.

        Expected: Books matching "gatsby" in title
        """
        result = service.SearchBooks("gatsby", "")

        assert result is not None
        assert len(result) >= 1

        # Should find The Great Gatsby
        titles = [book.title for book in result]
        assert any("Gatsby" in title for title in titles)

    def test_search_by_query_author(self, service):
        """Search by author name."""
        result = service.SearchBooks("Orwell", "")

        assert result is not None
        assert len(result) >= 1

        # Should find 1984 by George Orwell
        authors = [book.author for book in result]
        assert any("Orwell" in author for author in authors)

    def test_search_by_query_case_insensitive(self, service):
        """Verify search is case-insensitive."""
        result_lower = service.SearchBooks("gatsby", "")
        result_upper = service.SearchBooks("GATSBY", "")
        result_mixed = service.SearchBooks("GaTsBy", "")

        # All should return same results
        assert len(result_lower) == len(result_upper) == len(result_mixed)

    def test_search_by_genre_exact(self, service):
        """
        Test #7: SearchBooks by genre (partial match after BUG #1 fix).

        Expected: Books with genre containing "Fiction"
        """
        result = service.SearchBooks("", "Fiction")

        assert result is not None
        assert len(result) >= 1

        # All results should contain Fiction in genre (partial match)
        for book in result:
            assert "Fiction" in book.genre, f"Expected genre containing 'Fiction', got '{book.genre}'"

    def test_search_by_genre_dystopian(self, service):
        """Search for Dystopian genre books."""
        result = service.SearchBooks("", "Dystopian")

        assert result is not None
        assert len(result) >= 2  # 1984 and Brave New World

        titles = [book.title for book in result]
        assert "1984" in titles
        assert "Brave New World" in titles

    def test_search_empty_params_returns_all(self, service):
        """Search with both parameters empty returns all books."""
        result = service.SearchBooks("", "")

        assert result is not None
        assert len(result) >= 8  # At least all seed books

    def test_search_combined_query_and_genre(self, service):
        """Search with both query and genre filters."""
        # Search for books with "the" in title AND Fiction genre
        result = service.SearchBooks("the", "Fiction")

        assert result is not None
        # Should find The Great Gatsby and The Catcher in the Rye
        for book in result:
            assert book.genre == "Fiction"
            assert "the" in book.title.lower() or "the" in book.author.lower()

    def test_search_no_results(self, service):
        """Search that returns no results."""
        result = service.SearchBooks("xyznonexistent123qwerty", "")

        # SOAP may return None or empty list for no results
        assert result is None or len(result) == 0

    def test_search_by_partial_title(self, service):
        """Search by partial title."""
        result = service.SearchBooks("Kill", "")

        assert result is not None
        assert len(result) >= 1

        # Should find To Kill a Mockingbird
        titles = [book.title for book in result]
        assert any("Mockingbird" in title for title in titles)

    def test_search_genre_case_insensitive(self, service):
        """Verify genre search is case-insensitive."""
        result_normal = service.SearchBooks("", "Fiction")
        result_lower = service.SearchBooks("", "fiction")
        result_upper = service.SearchBooks("", "FICTION")

        # All should return same results
        assert len(result_normal) == len(result_lower) == len(result_upper)

    def test_search_with_whitespace(self, service):
        """Search handles whitespace correctly."""
        result = service.SearchBooks("  gatsby  ", "")

        assert result is not None
        assert len(result) >= 1
