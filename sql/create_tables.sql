-- 1. LibraryBranches
CREATE TABLE LibraryBranches (
  branch_id INT AUTO_INCREMENT PRIMARY KEY,
  branch_name VARCHAR(255),
  branch_location VARCHAR(255),
  phone VARCHAR(20)
);

-- 2. Categories
CREATE TABLE Categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  description TEXT
);

-- 3. Authors
CREATE TABLE Authors (
  author_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  bio TEXT
);

-- 4. Books
CREATE TABLE Books (
  book_id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255),
  isbn VARCHAR(20) UNIQUE,
  publisher VARCHAR(255),
  publication_year INT,
  category_id INT,
  FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- 5. BookAuthors
CREATE TABLE BookAuthors (
  book_id INT,
  author_id INT,
  PRIMARY KEY (book_id, author_id),
  FOREIGN KEY (book_id) REFERENCES Books(book_id),
  FOREIGN KEY (author_id) REFERENCES Authors(author_id)
);

-- 6. BookCopies
CREATE TABLE BookCopies (
  copy_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT,
  branch_id INT,
  copy_barcode VARCHAR(50) UNIQUE,
  status ENUM('available', 'borrowed', 'maintenance') DEFAULT 'available',
  FOREIGN KEY (book_id) REFERENCES Books(book_id),
  FOREIGN KEY (branch_id) REFERENCES LibraryBranches(branch_id)
);

-- 7. Users
CREATE TABLE Users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(20),
  password VARCHAR(255),
  role ENUM('student','teacher','regular','admin') DEFAULT 'regular'
);

-- 8. BorrowingRecords
CREATE TABLE BorrowingRecords (
  record_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  copy_id INT,
  borrow_date DATE,
  due_date DATE,
  return_date DATE,
  is_overdue BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (copy_id) REFERENCES BookCopies(copy_id)
);




-- to do in the feature.


--9. Fines
-- CREATE TABLE Fines (
--   fine_id INT AUTO_INCREMENT PRIMARY KEY,
--   record_id INT,
--   amount DECIMAL(10,2),
--   fine_date DATE,
--   is_paid BOOLEAN DEFAULT FALSE,
--   FOREIGN KEY (record_id) REFERENCES BorrowingRecords(record_id)
-- );

-- -- 11. Payments
-- CREATE TABLE Payments (
--   payment_id INT AUTO_INCREMENT PRIMARY KEY,
--   fine_id INT,
--   user_id INT,
--   payment_date DATETIME,
--   payment_amount DECIMAL(10,2),
--   payment_method ENUM('cash','credit_card','debit_card','online') DEFAULT 'online',
--   FOREIGN KEY (fine_id) REFERENCES Fines(fine_id),
--   FOREIGN KEY (user_id) REFERENCES Users(user_id)
-- );

-- -- 12. Notifications
-- CREATE TABLE Notifications (
--   notification_id INT AUTO_INCREMENT PRIMARY KEY,
--   user_id INT,
--   message TEXT,
--   created_at DATETIME,
--   read_at DATETIME,
--   FOREIGN KEY (user_id) REFERENCES Users(user_id)
-- );
