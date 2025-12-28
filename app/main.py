"""
Main entry point for the Library Catalog SOAP Service.

This module starts the WSGI server and serves the SOAP application.

To run:
    python -m app.main

The service will be available at:
    - Service endpoint: http://localhost:8000/
    - WSDL definition: http://localhost:8000/?wsdl

For production, consider using Gunicorn or uWSGI instead of wsgiref:
    gunicorn -w 4 -b 0.0.0.0:8000 'app.main:create_app()'
"""
import logging
from wsgiref.simple_server import make_server

from .soap.application import create_soap_application, get_wsdl_url
from .config import SOAP_HOST, SOAP_PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Spyne logging - set to DEBUG to see request/response XML
logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)


def create_app():
    """Create and return the WSGI application (for Gunicorn)."""
    return create_soap_application()


def main():
    """Start the SOAP web service server."""
    # Create the SOAP application
    wsgi_app = create_soap_application()

    logger.info("=" * 60)
    logger.info("Library Catalog SOAP Service")
    logger.info("=" * 60)
    logger.info(f"Service endpoint: http://{SOAP_HOST}:{SOAP_PORT}/")
    logger.info(f"WSDL available at: {get_wsdl_url(SOAP_HOST, SOAP_PORT)}")
    logger.info("")
    logger.info("Available operations:")
    logger.info("  - GetBook(book_id)")
    logger.info("  - GetAllBooks()")
    logger.info("  - AddBook(book)")
    logger.info("  - UpdateBook(book_id, book)")
    logger.info("  - DeleteBook(book_id)")
    logger.info("  - SearchBooks(query, genre)")
    logger.info("  - BorrowBook(book_id, borrower_name)")
    logger.info("  - ReturnBook(book_id)")
    logger.info("")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 60)

    # Create and start the WSGI server
    server = make_server(SOAP_HOST, SOAP_PORT, wsgi_app)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.shutdown()


if __name__ == '__main__':
    main()
