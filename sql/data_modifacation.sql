-- Modification 1: Insert into Notifications from a subquery (adds reminder for overdue users)
INSERT INTO Notifications (user_id, message, created_at)
SELECT br.user_id, 'You have overdue books. Please return them.', NOW()
FROM BorrowingRecords br
WHERE br.is_overdue = TRUE;

-- Modification 2: Update all reserved book copies to available (bulk update)
UPDATE BookCopies
SET status = 'available'
WHERE status = 'reserved';

-- Modification 3: Delete reservations that expired more than 30 days ago (batch delete)
DELETE FROM Reservations
WHERE status = 'active'
  AND expiration_date < CURDATE() - INTERVAL 30 DAY;