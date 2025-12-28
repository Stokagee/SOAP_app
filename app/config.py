"""
Application configuration from environment variables.
"""
import os


DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://library_user:library_password@localhost:5432/library_catalog'
)

SOAP_HOST = os.getenv('SOAP_HOST', '0.0.0.0')
SOAP_PORT = int(os.getenv('SOAP_PORT', 8000))

# Service configuration
SERVICE_NAME = 'LibraryCatalogService'
SERVICE_NAMESPACE = 'http://library.example.com/catalog'
TYPES_NAMESPACE = 'http://library.example.com/types'
FAULTS_NAMESPACE = 'http://library.example.com/faults'

# Borrow settings
DEFAULT_BORROW_DAYS = 14
