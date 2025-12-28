"""
Library Catalog SOAP Service.

This is the main service class that exposes all SOAP operations.
Each method decorated with @rpc becomes a SOAP operation in the WSDL.

Educational Notes - SOAP vs REST:
1. Operations are verb-based (GetBook, AddBook) not resource-based (/books/1)
2. All requests go to the SAME endpoint URL (/)
3. The operation is determined by the SOAPAction header and body content
4. Input/output types are strictly defined in WSDL
5. Errors are returned as SOAP Faults, not HTTP status codes
6. Parameters are named and ordered (defined in WSDL)

SOAP Request Structure:
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header/>  <!-- Optional headers for auth, transactions -->
    <soap:Body>
        <GetBook xmlns="http://library.example.com/catalog">
            <book_id>1</book_id>
        </GetBook>
    </soap:Body>
</soap:Envelope>
"""
from datetime import datetime, timedelta

from spyne import ServiceBase, rpc, Unicode, Integer, Boolean
from sqlalchemy.exc import IntegrityError

from .types import Book, BookInput, BorrowResult, ArrayOfBook
from .faults import (
    BookNotFoundFault,
    BookNotAvailableFault,
    InvalidInputFault,
    DuplicateISBNFault
)
from ..models.database import get_db_session
from ..models.book import BookModel
from ..config import DEFAULT_BORROW_DAYS


class LibraryCatalogService(ServiceBase):
    """
    SOAP Web Service for Library Book Catalog Management.

    Service namespace: http://library.example.com/catalog

    This service demonstrates common CRUD operations plus
    business logic operations (borrow/return) via SOAP.

    Operations:
    - GetBook: Retrieve single book by ID
    - GetAllBooks: List all books
    - AddBook: Create new book
    - UpdateBook: Modify existing book
    - DeleteBook: Remove book
    - SearchBooks: Find books by query/genre
    - BorrowBook: Borrow a book
    - ReturnBook: Return a borrowed book
    """

    @rpc(Integer, _returns=Book, _throws=[BookNotFoundFault])
    def GetBook(ctx, book_id):
        """
        Retrieve a single book by its ID.

        @param book_id: The unique identifier of the book
        @return: Book details if found
        @raises BookNotFoundFault: If book with given ID doesn't exist

        SOAP Request Example:
        <GetBook>
            <book_id>1</book_id>
        </GetBook>

        SOAP Response Example:
        <GetBookResponse>
            <GetBookResult>
                <id>1</id>
                <title>The Great Gatsby</title>
                ...
            </GetBookResult>
        </GetBookResponse>
        """
        session = get_db_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()

            if not db_book:
                raise BookNotFoundFault(book_id)

            return _map_to_soap_book(db_book)
        finally:
            session.close()

    @rpc(_returns=ArrayOfBook)
    def GetAllBooks(ctx):
        """
        Retrieve all books in the catalog.

        @return: Array of all Book records

        Note: In production, this should support pagination.
        For learning purposes, we return all books.

        SOAP Response contains ArrayOfBook with multiple Book elements.
        """
        session = get_db_session()
        try:
            db_books = session.query(BookModel).all()
            return [_map_to_soap_book(book) for book in db_books]
        finally:
            session.close()

    @rpc(BookInput, _returns=Book, _throws=[InvalidInputFault, DuplicateISBNFault])
    def AddBook(ctx, book):
        """
        Add a new book to the catalog.

        @param book: BookInput containing new book details
        @return: The created Book with generated ID
        @raises InvalidInputFault: If required fields are missing
        @raises DuplicateISBNFault: If ISBN already exists

        SOAP Request Example:
        <AddBook>
            <book>
                <title>Clean Code</title>
                <author>Robert C. Martin</author>
                <isbn>978-0132350884</isbn>
                <year>2008</year>
                <genre>Programming</genre>
            </book>
        </AddBook>
        """
        # Validate required fields
        if not book.title or not book.title.strip():
            raise InvalidInputFault('title', 'Title is required and cannot be empty')
        if not book.author or not book.author.strip():
            raise InvalidInputFault('author', 'Author is required and cannot be empty')
        if not book.isbn or not book.isbn.strip():
            raise InvalidInputFault('isbn', 'ISBN is required and cannot be empty')

        session = get_db_session()
        try:
            db_book = BookModel(
                title=book.title.strip(),
                author=book.author.strip(),
                isbn=book.isbn.strip(),
                year_published=book.year,
                genre=book.genre.strip() if book.genre else None,
                available=True
            )
            session.add(db_book)
            session.commit()
            session.refresh(db_book)

            return _map_to_soap_book(db_book)
        except IntegrityError:
            session.rollback()
            raise DuplicateISBNFault(book.isbn)
        finally:
            session.close()

    @rpc(Integer, BookInput, _returns=Book, _throws=[BookNotFoundFault, InvalidInputFault, DuplicateISBNFault])
    def UpdateBook(ctx, book_id, book):
        """
        Update an existing book's details.

        @param book_id: ID of the book to update
        @param book: BookInput with updated details
        @return: The updated Book
        @raises BookNotFoundFault: If book doesn't exist
        @raises InvalidInputFault: If validation fails

        SOAP Request Example:
        <UpdateBook>
            <book_id>1</book_id>
            <book>
                <title>Updated Title</title>
                <author>Same Author</author>
                <isbn>978-0743273565</isbn>
            </book>
        </UpdateBook>
        """
        session = get_db_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()

            if not db_book:
                raise BookNotFoundFault(book_id)

            # Update fields if provided
            if book.title and book.title.strip():
                db_book.title = book.title.strip()
            if book.author and book.author.strip():
                db_book.author = book.author.strip()
            if book.isbn and book.isbn.strip():
                db_book.isbn = book.isbn.strip()
            if book.year is not None:
                db_book.year_published = book.year
            if book.genre is not None:
                db_book.genre = book.genre.strip() if book.genre else None

            try:
                session.commit()
                session.refresh(db_book)
            except IntegrityError:
                session.rollback()
                raise DuplicateISBNFault(book.isbn)

            return _map_to_soap_book(db_book)
        finally:
            session.close()

    @rpc(Integer, _returns=Boolean, _throws=[BookNotFoundFault])
    def DeleteBook(ctx, book_id):
        """
        Delete a book from the catalog.

        @param book_id: ID of the book to delete
        @return: True if deletion was successful
        @raises BookNotFoundFault: If book doesn't exist

        SOAP Request Example:
        <DeleteBook>
            <book_id>1</book_id>
        </DeleteBook>

        SOAP Response:
        <DeleteBookResponse>
            <DeleteBookResult>true</DeleteBookResult>
        </DeleteBookResponse>
        """
        session = get_db_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()

            if not db_book:
                raise BookNotFoundFault(book_id)

            session.delete(db_book)
            session.commit()
            return True
        finally:
            session.close()

    @rpc(Unicode, Unicode, _returns=ArrayOfBook)
    def SearchBooks(ctx, query, genre):
        """
        Search for books by title/author text and optionally filter by genre.

        @param query: Search text to match against title and author (case-insensitive)
        @param genre: Optional genre filter (case-insensitive)
        @return: Array of matching Book records

        SOAP Request Example:
        <SearchBooks>
            <query>gatsby</query>
            <genre>Fiction</genre>
        </SearchBooks>

        Both parameters are optional - empty string or nil means no filter.
        """
        session = get_db_session()
        try:
            db_query = session.query(BookModel)

            # Apply text search filter
            if query and query.strip():
                search_term = f'%{query.strip().lower()}%'
                db_query = db_query.filter(
                    (BookModel.title.ilike(search_term)) |
                    (BookModel.author.ilike(search_term))
                )

            # Apply genre filter (with wildcard for partial match)
            if genre and genre.strip():
                genre_term = f'%{genre.strip()}%'
                db_query = db_query.filter(BookModel.genre.ilike(genre_term))

            db_books = db_query.all()
            return [_map_to_soap_book(book) for book in db_books]
        finally:
            session.close()

    @rpc(Integer, Unicode, _returns=BorrowResult,
         _throws=[BookNotFoundFault, BookNotAvailableFault, InvalidInputFault])
    def BorrowBook(ctx, book_id, borrower_name):
        """
        Borrow a book from the library.

        @param book_id: ID of the book to borrow
        @param borrower_name: Name of the person borrowing
        @return: BorrowResult with due date and status message
        @raises BookNotFoundFault: If book doesn't exist
        @raises BookNotAvailableFault: If book is already borrowed
        @raises InvalidInputFault: If borrower_name is empty

        Business Logic:
        - Books are borrowed for 14 days by default
        - Only available books can be borrowed
        - Attempting to borrow an already borrowed book returns BookNotAvailableFault

        SOAP Request Example:
        <BorrowBook>
            <book_id>1</book_id>
            <borrower_name>John Doe</borrower_name>
        </BorrowBook>
        """
        if not borrower_name or not borrower_name.strip():
            raise InvalidInputFault('borrower_name', 'Borrower name is required')

        session = get_db_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()

            if not db_book:
                raise BookNotFoundFault(book_id)

            if not db_book.available:
                raise BookNotAvailableFault(book_id, db_book.borrower_name)

            # Set borrow details
            db_book.available = False
            db_book.borrower_name = borrower_name.strip()
            db_book.borrowed_date = datetime.now()
            db_book.due_date = datetime.now() + timedelta(days=DEFAULT_BORROW_DAYS)

            session.commit()

            result = BorrowResult()
            result.success = True
            result.due_date = db_book.due_date
            result.message = (
                f'Book "{db_book.title}" successfully borrowed. '
                f'Please return by {db_book.due_date.strftime("%Y-%m-%d")}.'
            )

            return result
        finally:
            session.close()

    @rpc(Integer, _returns=Boolean, _throws=[BookNotFoundFault, InvalidInputFault])
    def ReturnBook(ctx, book_id):
        """
        Return a borrowed book to the library.

        @param book_id: ID of the book to return
        @return: True if return was successful
        @raises BookNotFoundFault: If book doesn't exist
        @raises InvalidInputFault: If book is not currently borrowed

        SOAP Request Example:
        <ReturnBook>
            <book_id>4</book_id>
        </ReturnBook>
        """
        session = get_db_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()

            if not db_book:
                raise BookNotFoundFault(book_id)

            if db_book.available:
                raise InvalidInputFault('book_id', 'This book is not currently borrowed')

            # Clear borrow details
            db_book.available = True
            db_book.borrower_name = None
            db_book.borrowed_date = None
            db_book.due_date = None

            session.commit()
            return True
        finally:
            session.close()


def _map_to_soap_book(db_book: BookModel) -> Book:
    """Helper function to map SQLAlchemy model to Spyne ComplexModel."""
    soap_book = Book()
    soap_book.id = db_book.id
    soap_book.title = db_book.title
    soap_book.author = db_book.author
    soap_book.isbn = db_book.isbn
    soap_book.year = db_book.year_published
    soap_book.genre = db_book.genre
    soap_book.available = db_book.available
    soap_book.borrower = db_book.borrower_name
    return soap_book
