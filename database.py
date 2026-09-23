import sqlite3


DATABASE_NAME = "library_management.db"


def connect_db():
    """
    Create and return a SQLite database connection.
    """

    connection = sqlite3.connect(DATABASE_NAME)

    # Enable foreign key constraints
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    """
    Create all required tables.
    """

    connection = connect_db()
    cursor = connection.cursor()

    # ======================================================
    # USERS TABLE
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
                CHECK (role IN ('Librarian', 'Member'))
        )
    """)

    # ======================================================
    # BOOKS TABLE
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            available_copies INTEGER NOT NULL
                CHECK (available_copies >= 0)
        )
    """)

    # ======================================================
    # MEMBERS TABLE
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            registration_date TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
    """)

    # ======================================================
    # BORROWINGS TABLE
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowings (
            borrowing_id INTEGER PRIMARY KEY AUTOINCREMENT,

            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,

            issue_date TEXT NOT NULL,
            return_date TEXT,

            status TEXT NOT NULL
                CHECK (status IN ('Issued', 'Returned')),

            FOREIGN KEY (book_id)
                REFERENCES books(book_id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,

            FOREIGN KEY (member_id)
                REFERENCES members(member_id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            request_date TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK (status IN ('Pending', 'Approved', 'Rejected')),
            FOREIGN KEY (member_id)
                REFERENCES members(member_id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,
            FOREIGN KEY (book_id)
                REFERENCES books(book_id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        )
    """)

    connection.commit()
    connection.close()

    print("Database tables are ready.")