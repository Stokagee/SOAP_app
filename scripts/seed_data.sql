-- Insert sample books for testing
INSERT INTO books (title, author, isbn, year_published, genre, available) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', '978-0743273565', 1925, 'Fiction', TRUE),
('To Kill a Mockingbird', 'Harper Lee', '978-0061120084', 1960, 'Fiction', TRUE),
('1984', 'George Orwell', '978-0451524935', 1949, 'Dystopian', TRUE),
('Pride and Prejudice', 'Jane Austen', '978-0141439518', 1813, 'Romance', FALSE),
('The Catcher in the Rye', 'J.D. Salinger', '978-0316769488', 1951, 'Fiction', TRUE),
('Brave New World', 'Aldous Huxley', '978-0060850524', 1932, 'Dystopian', TRUE),
('The Hobbit', 'J.R.R. Tolkien', '978-0547928227', 1937, 'Fantasy', TRUE),
('Dune', 'Frank Herbert', '978-0441172719', 1965, 'Science Fiction', FALSE);

-- Set borrower for unavailable books (for testing SOAP Faults)
UPDATE books
SET borrower_name = 'John Smith',
    borrowed_date = CURRENT_TIMESTAMP - INTERVAL '5 days',
    due_date = CURRENT_TIMESTAMP + INTERVAL '9 days'
WHERE isbn = '978-0141439518';

UPDATE books
SET borrower_name = 'Jane Doe',
    borrowed_date = CURRENT_TIMESTAMP - INTERVAL '3 days',
    due_date = CURRENT_TIMESTAMP + INTERVAL '11 days'
WHERE isbn = '978-0441172719';
