USE nlms;


SELECT b.title, bc.copy_barcode, lb.branch_name, bc.status
FROM BookCopies bc
JOIN Books b ON bc.book_id = b.book_id
JOIN LibraryBranches lb ON bc.branch_id = lb.branch_id;


SELECT u.name, br.due_date
FROM BorrowingRecords br
JOIN Users u ON br.user_id = u.user_id
WHERE br.is_overdue = TRUE;


SELECT lb.branch_name, COUNT(*) AS available_count
FROM BookCopies bc
JOIN LibraryBranches lb ON bc.branch_id = lb.branch_id
WHERE bc.status = 'available'
GROUP BY lb.branch_name;


SELECT DISTINCT u.name
FROM Users u
JOIN Payments p ON u.user_id = p.user_id
JOIN Fines f ON p.fine_id = f.fine_id
WHERE f.is_paid = FALSE;


SELECT b.title, CONCAT(a.first_name, ' ', a.last_name) AS author
FROM Books b
JOIN BookAuthors ba ON b.book_id = ba.book_id
JOIN Authors a ON ba.author_id = a.author_id;


SELECT u.name, b.title, r.reservation_date, r.status
FROM Reservations r
JOIN Users u ON r.user_id = u.user_id
JOIN BookCopies bc ON r.copy_id = bc.copy_id
JOIN Books b ON bc.book_id = b.book_id;

--section 6:
-- Query 1: Basic SELECT to list all books with title, isbn, and publication year
SELECT title, isbn, publication_year FROM Books;

-- Query 2: Find books with 'Python' in the title
SELECT title, isbn FROM Books WHERE title LIKE '%Python%';

-- Query 3: Count how many books each author has written (uses GROUP BY)
SELECT CONCAT(a.first_name, ' ', a.last_name) AS author_name, COUNT(*) AS book_count
FROM Authors a
JOIN BookAuthors ba ON a.author_id = ba.author_id
GROUP BY a.author_id;

-- Query 4: List available books in branch 1 (uses JOIN + WHERE)
SELECT b.title, bc.copy_barcode, lb.branch_name
FROM BookCopies bc
JOIN Books b ON bc.book_id = b.book_id
JOIN LibraryBranches lb ON bc.branch_id = lb.branch_id
WHERE bc.branch_id = 1 AND bc.status = 'available';

-- Query 5: Find users with overdue or unreturned books (uses subquery)
SELECT DISTINCT u.name, u.email
FROM Users u
WHERE u.user_id IN (
  SELECT br.user_id
  FROM BorrowingRecords br
  WHERE br.return_date IS NULL OR br.is_overdue = TRUE
);

-- Query 6: Find users who have made at least one reservation (uses EXISTS)
SELECT u.user_id, u.name
FROM Users u
WHERE EXISTS (
  SELECT 1 FROM Reservations r WHERE r.user_id = u.user_id
);