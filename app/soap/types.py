"""
SOAP Complex Types for Library Catalog Service.

These ComplexModel classes define the XML schema types that will appear in the WSDL.
SoapUI will use these definitions to understand the service contract.

SOAP vs REST note:
- In REST, you typically use JSON with flexible schemas
- In SOAP, all types are strictly defined in WSDL using XML Schema (XSD)
- This provides compile-time type safety and automatic validation
"""
from spyne import ComplexModel, Unicode, Integer, Boolean, DateTime, Array

from ..config import TYPES_NAMESPACE


class Book(ComplexModel):
    """
    Represents a complete book record (output type).

    This is the primary output type for book operations.
    In WSDL, this becomes a complex type with all fields as elements.

    Example XML:
    <Book>
        <id>1</id>
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
        <isbn>978-0743273565</isbn>
        <year>1925</year>
        <genre>Fiction</genre>
        <available>true</available>
        <borrower/>
    </Book>
    """
    __namespace__ = TYPES_NAMESPACE

    id = Integer(doc="Unique book identifier")
    title = Unicode(doc="Book title", min_len=1, max_len=255)
    author = Unicode(doc="Author name", min_len=1, max_len=255)
    isbn = Unicode(doc="ISBN-13 format", min_len=10, max_len=20)
    year = Integer(doc="Year of publication")
    genre = Unicode(doc="Book genre/category", max_len=100)
    available = Boolean(doc="Whether book is available for borrowing")
    borrower = Unicode(doc="Name of current borrower if borrowed", max_len=255)


class BookInput(ComplexModel):
    """
    Input type for creating or updating books.

    Separating input from output types is a SOAP best practice.
    This allows validation rules specific to input data.

    Required fields are marked with min_occurs=1.
    Optional fields have min_occurs=0 (default).

    Example XML:
    <book>
        <title>Clean Code</title>
        <author>Robert C. Martin</author>
        <isbn>978-0132350884</isbn>
        <year>2008</year>
        <genre>Programming</genre>
    </book>
    """
    __namespace__ = TYPES_NAMESPACE

    title = Unicode(min_occurs=1, doc="Book title (required)")
    author = Unicode(min_occurs=1, doc="Author name (required)")
    isbn = Unicode(min_occurs=1, doc="ISBN-13 format (required)")
    year = Integer(min_occurs=0, doc="Year of publication (optional)")
    genre = Unicode(min_occurs=0, doc="Book genre/category (optional)")


class BorrowResult(ComplexModel):
    """
    Result type for borrow operations.

    Complex return types allow rich responses with multiple fields,
    unlike REST which often relies on HTTP status codes alone.

    Example XML:
    <BorrowResult>
        <success>true</success>
        <due_date>2024-01-15T00:00:00</due_date>
        <message>Book successfully borrowed. Please return by 2024-01-15.</message>
    </BorrowResult>
    """
    __namespace__ = TYPES_NAMESPACE

    success = Boolean(doc="Whether the borrow operation succeeded")
    due_date = DateTime(doc="When the book is due for return")
    message = Unicode(doc="Human-readable result message")


# Array type for returning multiple books
# In WSDL, this becomes a complex type with a sequence of Book elements
ArrayOfBook = Array(Book, doc="Collection of Book records")
