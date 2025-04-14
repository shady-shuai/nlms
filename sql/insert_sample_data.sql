-- insert_sample_data.sql
-- Insert sample data into NLMS system

-- 1. Library Branches
INSERT INTO LibraryBranches (branch_name, branch_location, phone) VALUES
('Toronto Central Library', 'Toronto, ON', '416-555-1234'),
('Vancouver Public Library', 'Vancouver, BC', '604-555-5678');

-- 2. Categories
INSERT INTO Categories (name, description) VALUES
('Science Fiction', 'Futuristic themes'),
('History', 'Historical records and studies');

-- 3. Authors
INSERT INTO Authors (first_name, last_name, bio) VALUES
('Isaac', 'Asimov', 'Sci-fi author'),
('Yuval', 'Harari', 'Historian and philosopher');

-- 4. Books
INSERT INTO Books (title, isbn, publisher, publication_year, category_id) VALUES
('Foundation', '9780553293357', 'Spectra', 1988, 1),
('Sapiens', '9780062316097', 'Harper', 2014, 2);

-- 5. BookAuthors
INSERT INTO BookAuthors (book_id, author_id) VALUES
(1, 1),
(2, 2);

-- 6. BookCopies
INSERT INTO BookCopies (book_id, branch_id, copy_barcode, status) VALUES
(1, 1, 'TCL-FOUND-001', 'available'),
(1, 2, 'VPL-FOUND-002', 'borrowed'),
(2, 1, 'TCL-SAPIENS-001', 'available');

-- 7. Users
INSERT INTO Users (name, email, phone, password, role) VALUES
('Alice Smith', 'alice@example.com', '111-222-3333', 'pass123', 'regular'),
('Bob Lee', 'bob@example.com', '444-555-6666', 'pass456', 'student');

-- 8. BorrowingRecords
INSERT INTO BorrowingRecords (user_id, copy_id, borrow_date, due_date, return_date, is_overdue) VALUES
(1, 2, '2025-03-01', '2025-03-15', NULL, TRUE);

-- 9. Reservations
INSERT INTO Reservations (user_id, copy_id, reservation_date, expiration_date, status) VALUES
(2, 2, '2025-03-10', '2025-03-20', 'active');

-- 10. Fines
INSERT INTO Fines (record_id, amount, fine_date, is_paid) VALUES
(1, 5.00, '2025-03-20', FALSE);

-- 11. Payments
INSERT INTO Payments (fine_id, user_id, payment_date, payment_amount, payment_method) VALUES
(1, 1, '2025-03-21 14:30:00', 5.00, 'online');

-- 12. Notifications
INSERT INTO Notifications (user_id, message, created_at, read_at) VALUES
(1, 'Your borrowed book is overdue.', '2025-03-16 08:00:00', NULL),
(2, 'Reservation confirmed for Sapiens.', '2025-03-11 09:00:00', '2025-03-11 09:30:00');
--section 3:
-- INSERT 1: Standard INSERT INTO ... VALUES (basic insertion of multiple rows into Categories)
INSERT INTO Categories (name, description) VALUES
  ('Engineering', 'Books on engineering topics'),
  ('Science Fiction', 'Books about science and futuristic concepts'),
  ('History', 'Historical records and narratives');

-- INSERT 2: INSERT INTO ... SELECT (copies Sci-Fi books into a new table for testing)
CREATE TABLE IF NOT EXISTS SciFiBooks AS
SELECT b.book_id, b.title, b.isbn
FROM Books b
JOIN Categories c ON b.category_id = c.category_id
WHERE c.name = 'Science Fiction';
-- INSERT 3: INSERT INTO ... SELECT with subquery (creates a welcome notification for recent users)
INSERT INTO Notifications (user_id, message, created_at)
SELECT u.user_id,
       CONCAT('Welcome ', u.name, '! Enjoy using the system.'),
       NOW()
FROM Users u
WHERE u.user_id > (SELECT MAX(user_id) - 5 FROM Users);



INSERT INTO Users (name, email, phone, password, role)
VALUES ('Admin User', 'admin@admin.com', '1234567890', 'admin', 'admin');

INSERT INTO Users (name, email, phone, password, role)
VALUES ('test User', 'test@test.com', '1234567890', 'test', 'regular');