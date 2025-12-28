"""
Custom SOAP Faults for Library Catalog Service.

SOAP Faults are the SOAP equivalent of HTTP error responses in REST.
They provide structured error information in XML format.

Key difference from REST:
- SOAP always returns HTTP 200 or 500, error details are in the SOAP envelope
- Faults have faultcode (category) and faultstring (message)
- Custom faults can include additional detail elements

SOAP Fault structure:
<soap:Fault>
    <faultcode>Client.BookNotFound</faultcode>
    <faultstring>Book with ID 999 was not found in the catalog.</faultstring>
    <detail>
        <!-- Additional custom error data -->
    </detail>
</soap:Fault>

Faultcode conventions:
- 'Client.*' indicates client-side error (bad request, invalid input)
- 'Server.*' indicates server-side error (database down, internal error)
"""
from spyne import Fault

from ..config import FAULTS_NAMESPACE


class BookNotFoundFault(Fault):
    """
    Raised when a requested book does not exist.

    Use case: GetBook, UpdateBook, DeleteBook, BorrowBook, ReturnBook
    with non-existent book_id.
    """
    __namespace__ = FAULTS_NAMESPACE

    def __init__(self, book_id: int):
        super(BookNotFoundFault, self).__init__(
            faultcode='Client.BookNotFound',
            faultstring=f'Book with ID {book_id} was not found in the catalog.'
        )
        self.book_id = book_id


class BookNotAvailableFault(Fault):
    """
    Raised when attempting to borrow a book that is already borrowed.

    Use case: BorrowBook when book.available is False.
    """
    __namespace__ = FAULTS_NAMESPACE

    def __init__(self, book_id: int, current_borrower: str):
        super(BookNotAvailableFault, self).__init__(
            faultcode='Client.BookNotAvailable',
            faultstring=f'Book with ID {book_id} is currently borrowed by {current_borrower}.'
        )
        self.book_id = book_id
        self.current_borrower = current_borrower


class InvalidInputFault(Fault):
    """
    Raised when input validation fails.

    Use case: AddBook with missing required fields, BorrowBook with empty
    borrower name, ReturnBook on a book that isn't borrowed.
    """
    __namespace__ = FAULTS_NAMESPACE

    def __init__(self, field: str, message: str):
        super(InvalidInputFault, self).__init__(
            faultcode='Client.InvalidInput',
            faultstring=f'Validation error on field "{field}": {message}'
        )
        self.field = field
        self.validation_message = message


class DuplicateISBNFault(Fault):
    """
    Raised when attempting to add a book with an ISBN that already exists.

    Use case: AddBook with an ISBN that's already in the database.
    """
    __namespace__ = FAULTS_NAMESPACE

    def __init__(self, isbn: str):
        super(DuplicateISBNFault, self).__init__(
            faultcode='Client.DuplicateISBN',
            faultstring=f'A book with ISBN {isbn} already exists in the catalog.'
        )
        self.isbn = isbn
