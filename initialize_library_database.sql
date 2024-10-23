-- Create the database and select it
CREATE DATABASE IF NOT EXISTS library2;
USE library2;

-- Drop and create the books table
DROP TABLE IF EXISTS books;
CREATE TABLE books (
    Title VARCHAR(500) NOT NULL,
    Authors VARCHAR(500),
    Description TEXT,
    Category VARCHAR(100),
    Publisher VARCHAR(500),
    Publish_date VARCHAR(100),
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Add id as primary key
    total_copies INT NOT NULL DEFAULT 3,  -- Total number of copies of the book
    available_copies INT NOT NULL DEFAULT 3  -- Number of available copies
);

-- Load data from the CSV file into the books table
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/BooksDatasetClean.csv'
INTO TABLE books
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Title, Authors, Description, Category, Publisher, Publish_date);

-- Drop and create the customers table
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,  -- Adjust length as needed
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Auto-incrementing primary key
    UNIQUE (phone_number)  -- Enforce unique phone numbers
);

-- Insert sample customer data
INSERT INTO customers (customer_name, phone_number) VALUES
('Alice Cohen', '050-1234567'),
('Bob Levi', '052-2345678'),
('Charlie David', '053-3456789'),
('David Goldstein', '054-4567890'),
('Eva Katz', '055-5678901'),
('Fiona Stein', '056-6789012'),
('George Ben', '057-7890123'),
('Hannah Green', '058-8901234'),
('Iris Blue', '059-9012345'),
('Jack Brown', '050-0123456'),
('Kira White', '051-1234567'),
('Liam Black', '052-8765432'), 
('Maya Silver', '053-2345678'),  
('Noah Gold', '054-9876543'),  
('Olivia Rose', '055-6789012'),  
('Peter Grey', '056-3456789'), 
('Quinn Purple', '057-1234567'), 
('Ruth Orange', '058-9876543'), 
('Sam Red', '059-3456789'), 
('Tina Yellow', '050-6543210'), 
('Victor Gold', '051-7654321');  

-- Create the book_copy table
DROP TABLE IF EXISTS book_copy;
CREATE TABLE book_copy (
    book_id INT NOT NULL,  -- Foreign key referencing books table
    copy_number INT NOT NULL,  -- Sequential copy number for each book
    available BOOLEAN DEFAULT TRUE,  -- Availability status of the book copy
    PRIMARY KEY (book_id, copy_number),  -- Composite primary key
    FOREIGN KEY (book_id) REFERENCES books(id)  -- Foreign key relationship
);

-- Trigger to automatically increment copy numbers when a new copy is added
DELIMITER //
CREATE TRIGGER before_insert_book_copy
BEFORE INSERT ON book_copy
FOR EACH ROW
BEGIN
    DECLARE max_copy_number INT;
    
    SELECT COALESCE(MAX(copy_number), 0) INTO max_copy_number
    FROM book_copy
    WHERE book_id = NEW.book_id;
    
    SET NEW.copy_number = max_copy_number + 1;
END//
DELIMITER ;

INSERT INTO book_copy (book_id, copy_number)
SELECT id, 1 FROM books  -- Insert the first copy
UNION ALL
SELECT id, 2 FROM books  -- Insert the second copy
UNION ALL
SELECT id, 3 FROM books;  -- Insert the third copy



-- Create the borrowed_books table
DROP TABLE IF EXISTS borrowed_books;
CREATE TABLE borrowed_books (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique identifier for each transaction
    book_id INT,                        -- Foreign key referencing the books table
    copy_number INT,                    -- The copy number of the book
    customer_id INT,                    -- Foreign key referencing the customers table
    borrow_date DATE,                   -- The date the book was borrowed
    expected_return_date DATE,          -- The date the book is expected to be returned
    actual_return_date DATE DEFAULT NULL,  -- The actual date the book was returned, if returned
    FOREIGN KEY (book_id, copy_number) REFERENCES book_copy(book_id, copy_number),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);


