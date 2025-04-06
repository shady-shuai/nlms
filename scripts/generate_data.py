# scripts/generate_data.py

import random
from faker import Faker
import mysql.connector

fake = Faker()

# Configure DB connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="group8",  
    database="nlms"
)
cursor = conn.cursor()

# 1. Generate Categories (10)
category_ids = []
for _ in range(10):
    name = fake.word().title()[:100]
    description = fake.sentence()[:65535]
    cursor.execute(
        "INSERT INTO Categories (name, description) VALUES (%s, %s)",
        (name, description)
    )
    category_ids.append(cursor.lastrowid)
conn.commit()

# 2. Generate LibraryBranches (5)
branch_ids = []
for _ in range(5):
    city = fake.city()[:255]
    phone = fake.phone_number()[:20]
    cursor.execute(
        "INSERT INTO LibraryBranches (branch_name, branch_location, phone) VALUES (%s, %s, %s)",
        (f"{city} Library", f"{city}, ON", phone)
    )
    branch_ids.append(cursor.lastrowid)
conn.commit()

# 3. Generate Authors (1000)
author_ids = []
for _ in range(1000):
    first = fake.first_name()[:100]
    last = fake.last_name()[:100]
    bio = fake.text(max_nb_chars=200)
    cursor.execute(
        "INSERT INTO Authors (first_name, last_name, bio) VALUES (%s, %s, %s)",
        (first, last, bio)
    )
    author_ids.append(cursor.lastrowid)
conn.commit()

# 4. Generate Users (10000) with unique emails
user_ids = []
roles = ['student', 'teacher', 'regular']
emails_seen = set()
for _ in range(10000):
    name = fake.name()[:255]
    # ensure unique email
    email = fake.email()
    while email in emails_seen:
        email = fake.email()
    emails_seen.add(email)
    phone = fake.phone_number()[:20]
    password = "pass123"
    role = random.choice(roles)
    cursor.execute(
        "INSERT INTO Users (name, email, phone, password, role) VALUES (%s, %s, %s, %s, %s)",
        (name, email, phone, password, role)
    )
    user_ids.append(cursor.lastrowid)
conn.commit()

# 5. Generate Books (20000)
book_ids = []
for _ in range(20000):
    title = fake.sentence(nb_words=4)[:255]
    isbn = fake.isbn13()[:20]
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

# 6. Generate BookAuthors (1-3 per book)
for book_id in book_ids:
    for _ in range(random.randint(1, 3)):
        author_id = random.choice(author_ids)
        cursor.execute(
            "INSERT IGNORE INTO BookAuthors (book_id, author_id) VALUES (%s, %s)",
            (book_id, author_id)
        )
conn.commit()

# 7. Generate BookCopies (1-5 per book)
for book_id in book_ids:
    for _ in range(random.randint(1, 5)):
        branch_id = random.choice(branch_ids)
        barcode = f"{book_id}-{fake.bothify(text='COPY-#####')}"[:50]
        status = random.choice(['available', 'borrowed', 'reserved', 'maintenance'])
        cursor.execute(
            """INSERT INTO BookCopies (book_id, branch_id, copy_barcode, status)
               VALUES (%s, %s, %s, %s)""",
            (book_id, branch_id, barcode, status)
        )
conn.commit()

print("Data generation complete.")
cursor.close()
conn.close()
