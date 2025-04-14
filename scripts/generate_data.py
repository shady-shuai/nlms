# scripts/generate_data.py
"""
A comprehensive data generation script matching your nlms schema enums exactly.
Removes slicing for ENUM fields so that values match the table definitions:
 - BookCopies.status: available, borrowed, reserved, maintenance
 - Reservations.status: active, cancelled, fulfilled
 - Users.role: student, teacher, regular, admin
 - Payments.payment_method: cash, credit_card, debit_card, online
"""

import random
from faker import Faker
import mysql.connector
from datetime import datetime, timedelta

fake = Faker()

# Configure DB connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="group8",
    database="nlms"  # Ensure this DB & tables exist as defined
)
cursor = conn.cursor()

# 1. Categories
category_ids = []
for _ in range(10):
    name = fake.word().title()[:100]          # name VARCHAR(100)
    description = fake.sentence()[:65535]     # description TEXT
    cursor.execute(
        "INSERT INTO Categories (name, description) VALUES (%s, %s)",
        (name, description)
    )
    category_ids.append(cursor.lastrowid)
conn.commit()

# 2. LibraryBranches
branch_ids = []
for _ in range(5):
    city = fake.city()[:255]
    phone = fake.phone_number()[:20]
    branch_name = f"{city} Library"[:255]
    branch_location = f"{city}, ON"[:255]
    cursor.execute(
        """INSERT INTO LibraryBranches (branch_name, branch_location, phone)
           VALUES (%s, %s, %s)""",
        (branch_name, branch_location, phone)
    )
    branch_ids.append(cursor.lastrowid)
conn.commit()

# 3. Authors
author_ids = []
for _ in range(1000):
    first = fake.first_name()[:100]
    last = fake.last_name()[:100]
    bio = fake.text(max_nb_chars=200)[:65535]
    cursor.execute(
        "INSERT INTO Authors (first_name, last_name, bio) VALUES (%s, %s, %s)",
        (first, last, bio)
    )
    author_ids.append(cursor.lastrowid)
conn.commit()

# 4. Users
#   role ENUM('student','teacher','regular','admin') DEFAULT 'regular'
user_ids = []
possible_roles = ['student', 'teacher', 'regular', 'admin']
emails_seen = set()
for _ in range(10000):
    name = fake.name()[:255]
    email = fake.email()[:255]
    while email in emails_seen:
        email = fake.email()[:255]
    emails_seen.add(email)

    phone = fake.phone_number()[:20]
    password = "pass123"
    role = random.choice(possible_roles)  # pick from the 4 exactly
    cursor.execute(
        """INSERT INTO Users (name, email, phone, password, role)
           VALUES (%s, %s, %s, %s, %s)""",
        (name, email, phone, password, role)
    )
    user_ids.append(cursor.lastrowid)
conn.commit()

# 5. Books
book_ids = []
generated_isbns = set()
for _ in range(20000):
    title = fake.sentence(nb_words=4)[:255]
    isbn = fake.isbn13()[:20]
    while isbn in generated_isbns:
        isbn = fake.isbn13()[:20]
    generated_isbns.add(isbn)

    publisher = fake.company()[:255]
    year = random.randint(1950, 2025)
    category_id = random.choice(category_ids)
    cursor.execute(
        """INSERT INTO Books (title, isbn, publisher, publication_year, category_id)
           VALUES (%s, %s, %s, %s, %s)""",
        (title, isbn, publisher, year, category_id)
    )
    book_ids.append(cursor.lastrowid)
conn.commit()

# 6. BookAuthors
for book_id in book_ids:
    for _ in range(random.randint(1, 3)):
        author_id = random.choice(author_ids)
        cursor.execute(
            "INSERT IGNORE INTO BookAuthors (book_id, author_id) VALUES (%s, %s)",
            (book_id, author_id)
        )
conn.commit()

# 7. BookCopies
#   status ENUM('available','borrowed','reserved','maintenance') DEFAULT 'available'
copy_ids = []
generated_barcodes = set()
possible_bc_statuses = ['available', 'borrowed', 'reserved', 'maintenance']

for book_id in book_ids:
    for _ in range(random.randint(1, 5)):
        branch_id = random.choice(branch_ids)
        # generate unique barcode
        barcode = f"{book_id}-{fake.bothify(text='COPY-#####')}"[:50]
        while barcode in generated_barcodes:
            barcode = f"{book_id}-{fake.bothify(text='COPY-#####')}"[:50]
        generated_barcodes.add(barcode)

        status = random.choice(possible_bc_statuses)
        # no slicing here; these 4 match the ENUM definition exactly

        cursor.execute(
            """INSERT INTO BookCopies (book_id, branch_id, copy_barcode, status)
               VALUES (%s, %s, %s, %s)""",
            (book_id, branch_id, barcode, status)
        )
        copy_ids.append(cursor.lastrowid)
conn.commit()

# 8. BorrowingRecords
borrowing_record_ids = []
today = datetime.today().date()
num_borrowing_records = 15000

for _ in range(num_borrowing_records):
    user_id = random.choice(user_ids)
    copy_id = random.choice(copy_ids)
    borrow_date = fake.date_between(start_date='-2y', end_date='-30d')
    due_date = borrow_date + timedelta(days=random.randint(7, 30))
    # 70% chance returned
    if random.random() < 0.7:
        ret_date = fake.date_between(start_date=borrow_date, end_date=today)
        return_date = ret_date if ret_date <= due_date else due_date
    else:
        return_date = None

    is_overdue = (return_date is None and due_date < today)
    cursor.execute(
        """INSERT INTO BorrowingRecords (user_id, copy_id, borrow_date, due_date, return_date, is_overdue)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, copy_id, borrow_date, due_date, return_date, is_overdue)
    )
    borrowing_record_ids.append((cursor.lastrowid, user_id))
conn.commit()

# 9. Reservations
#   status ENUM('active','cancelled','fulfilled') DEFAULT 'active'
possible_res_statuses = ['active', 'cancelled', 'fulfilled']
num_reservations = 2000

for _ in range(num_reservations):
    user_id = random.choice(user_ids)
    copy_id = random.choice(copy_ids)
    reservation_date = fake.date_between(start_date='-1y', end_date='today')
    expiration_date = reservation_date + timedelta(days=random.choice([7, 14, 21]))
    status = random.choice(possible_res_statuses)  # matches your schema exactly

    cursor.execute(
        """INSERT INTO Reservations (user_id, copy_id, reservation_date, expiration_date, status)
           VALUES (%s, %s, %s, %s, %s)""",
        (user_id, copy_id, reservation_date, expiration_date, status)
    )
conn.commit()

# 10. Fines
fine_records = []
for record_id, user_id in borrowing_record_ids:
    if random.random() < 0.2:  # 20% have fines
        amount = round(random.uniform(1, 50), 2)
        fine_date = fake.date_between(start_date='-1y', end_date='today')
        is_paid = (random.random() < 0.7)
        cursor.execute(
            """INSERT INTO Fines (record_id, amount, fine_date, is_paid)
               VALUES (%s, %s, %s, %s)""",
            (record_id, amount, fine_date, is_paid)
        )
        fine_records.append((cursor.lastrowid, user_id, amount, is_paid))
conn.commit()

# 11. Payments
#   payment_method ENUM('cash','credit_card','debit_card','online') DEFAULT 'online'
pay_methods = ['cash', 'credit_card', 'debit_card', 'online']

for fine_id, user_id, amount, is_paid in fine_records:
    if is_paid:
        payment_date = fake.date_time_between(start_date='-1y', end_date='now')
        payment_method = random.choice(pay_methods)  # exactly as schema
        cursor.execute(
            """INSERT INTO Payments (fine_id, user_id, payment_date, payment_amount, payment_method)
               VALUES (%s, %s, %s, %s, %s)""",
            (fine_id, user_id, payment_date, amount, payment_method)
        )
conn.commit()

# 12. Notifications
num_notifications = 500
for _ in range(num_notifications):
    user_id = random.choice(user_ids)
    message = fake.sentence(nb_words=10)[:2000]  # TEXT can handle more, but let's be safe
    created_at = fake.date_time_between(start_date='-1y', end_date='now')
    if random.random() < 0.5:
        read_at = fake.date_time_between(start_date=created_at, end_date='now')
    else:
        read_at = None
    cursor.execute(
        """INSERT INTO Notifications (user_id, message, created_at, read_at)
           VALUES (%s, %s, %s, %s)""",
        (user_id, message, created_at, read_at)
    )
conn.commit()

print("Data generation complete.")
cursor.close()
conn.close()
