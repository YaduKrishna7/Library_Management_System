import sqlite3
from datetime import date

from database import create_tables, connect_db


# ============================================================
#                       UTILITY
# ============================================================

def pause():
    """
    Pause the program.
    """
    input("\nPress Enter to continue...")


# ============================================================
#                       SIGN UP
# ============================================================

def sign_up():

    print("\n")
    print("=" * 60)
    print("                         SIGN UP")
    print("=" * 60)

    print("\nSelect your role:")
    print("1. Librarian")
    print("2. Member")

    role_choice = input("\nEnter your choice: ").strip()

    if role_choice == "1":
        role = "Librarian"

    elif role_choice == "2":
        role = "Member"

    else:
        print("\nInvalid role.")
        return

    # --------------------------------------------------------
    # Username
    # --------------------------------------------------------

    username = input("\nEnter username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    # --------------------------------------------------------
    # Password
    # --------------------------------------------------------

    password = input("Enter password: ").strip()

    if not password:
        print("Password cannot be empty.")
        return

    if len(password) < 4:
        print("Password must contain at least 4 characters.")
        return

    # --------------------------------------------------------
    # Member details
    # --------------------------------------------------------

    name = None
    phone = None
    email = None

    if role == "Member":

        print("\nEnter Member Details")
        print("-" * 40)

        name = input("Enter name: ").strip()

        if not name:
            print("Name cannot be empty.")
            return

        phone = input("Enter phone number: ").strip()

        if not phone:
            print("Phone number cannot be empty.")
            return

        if not phone.isdigit():
            print("Phone number must contain only digits.")
            return

        email = input("Enter email: ").strip()

        if not email:
            print("Email cannot be empty.")
            return

        if "@" not in email or "." not in email:
            print("Please enter a valid email address.")
            return

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    connection = connect_db()
    cursor = connection.cursor()

    try:

        # Insert user
        cursor.execute("""
            INSERT INTO users
            (
                username,
                password,
                role
            )
            VALUES (?, ?, ?)
        """, (
            username,
            password,
            role
        ))

        user_id = cursor.lastrowid

        # Create member profile
        if role == "Member":

            registration_date = date.today().isoformat()

            cursor.execute("""
                INSERT INTO members
                (
                    user_id,
                    name,
                    phone,
                    email,
                    registration_date
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                name,
                phone,
                email,
                registration_date
            ))

        connection.commit()

        print("\n" + "=" * 60)
        print("                 SIGN UP SUCCESSFUL")
        print("=" * 60)

        print(f"Username : {username}")
        print(f"Role     : {role}")

        if role == "Member":
            print(f"Name     : {name}")
            print(f"Email    : {email}")

    except sqlite3.IntegrityError as error:

        connection.rollback()

        error_message = str(error).lower()

        if "username" in error_message:
            print("\nUsername already exists.")

        elif "email" in error_message:
            print("\nEmail already exists.")

        else:
            print("\nRegistration failed.")
            print("Database error:", error)

    except sqlite3.Error as error:

        connection.rollback()

        print("\nDatabase error:", error)

    finally:

        connection.close()


# ============================================================
#                       SIGN IN
# ============================================================

def sign_in():

    print("\n")
    print("=" * 60)
    print("                         SIGN IN")
    print("=" * 60)

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if not username or not password:

        print("\nUsername and password are required.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_id,
            username,
            role
        FROM users
        WHERE username = ?
          AND password = ?
    """, (
        username,
        password
    ))

    user = cursor.fetchone()

    connection.close()

    if user is None:

        print("\nInvalid username or password.")
        return

    user_id = user[0]
    username = user[1]
    role = user[2]

    print("\n" + "=" * 60)
    print("                  LOGIN SUCCESSFUL")
    print("=" * 60)

    print(f"Welcome, {username}!")
    print(f"Role: {role}")

    # Role-based access
    if role == "Librarian":

        librarian_menu(user_id, username)

    elif role == "Member":

        member_menu(user_id, username)

    else:

        print("Invalid role.")


# ============================================================
#                    BOOK MANAGEMENT
# ============================================================

# ------------------------------------------------------------
# ADD BOOK
# ------------------------------------------------------------

def add_book():

    print("\n")
    print("=" * 60)
    print("                         ADD BOOK")
    print("=" * 60)

    title = input("Enter book title: ").strip()

    if not title:
        print("Book title cannot be empty.")
        return

    author = input("Enter author name: ").strip()

    if not author:
        print("Author name cannot be empty.")
        return

    category = input("Enter category: ").strip()

    if not category:
        print("Category cannot be empty.")
        return

    copies_input = input("Enter available copies: ").strip()

    try:

        available_copies = int(copies_input)

        if available_copies < 0:
            print("Available copies cannot be negative.")
            return

    except ValueError:

        print("Please enter a valid number.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO books
            (
                title,
                author,
                category,
                available_copies
            )
            VALUES (?, ?, ?, ?)
        """, (
            title,
            author,
            category,
            available_copies
        ))

        connection.commit()

        print("\nBook added successfully!")
        print(f"Book ID: {cursor.lastrowid}")

    except sqlite3.Error as error:

        connection.rollback()

        print("\nFailed to add book.")
        print("Database error:", error)

    finally:

        connection.close()


# ------------------------------------------------------------
# VIEW ALL BOOKS
# ------------------------------------------------------------

def view_books():

    print("\n")
    print("=" * 90)
    print("                           ALL BOOKS")
    print("=" * 90)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            book_id,
            title,
            author,
            category,
            available_copies
        FROM books
        ORDER BY book_id
    """)

    books = cursor.fetchall()

    connection.close()

    if not books:

        print("\nNo books found.")
        return

    print("-" * 90)

    print(
        f"{'ID':<5}"
        f"{'TITLE':<28}"
        f"{'AUTHOR':<22}"
        f"{'CATEGORY':<20}"
        f"{'COPIES':<8}"
    )

    print("-" * 90)

    for book in books:

        print(
            f"{book[0]:<5}"
            f"{book[1][:26]:<28}"
            f"{book[2][:20]:<22}"
            f"{book[3][:18]:<20}"
            f"{book[4]:<8}"
        )

    print("-" * 90)


# ------------------------------------------------------------
# SEARCH BOOK
# ------------------------------------------------------------

def search_book():

    print("\n")
    print("=" * 60)
    print("                       SEARCH BOOK")
    print("=" * 60)

    search_text = input("Enter title, author or category: ").strip()
    if not search_text:

        print("Search value cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    search_value = "%" + search_text + "%"

    cursor.execute("""
        SELECT
            book_id,
            title,
            author,
            category,
            available_copies
        FROM books
        WHERE title LIKE ?
           OR author LIKE ?
           OR category LIKE ?
        ORDER BY title
    """, (
        search_value,
        search_value,
        search_value
    ))

    books = cursor.fetchall()

    connection.close()

    if not books:

        print("\nNo matching books found.")
        return

    print("\nSearch Results")
    print("-" * 80)

    for book in books:

        print(f"Book ID          : {book[0]}")
        print(f"Title            : {book[1]}")
        print(f"Author           : {book[2]}")
        print(f"Category         : {book[3]}")
        print(f"Available Copies : {book[4]}")

        print("-" * 80)


# ------------------------------------------------------------
# UPDATE BOOK
# ------------------------------------------------------------

def update_book():

    print("\n")
    print("=" * 60)
    print("                       UPDATE BOOK")
    print("=" * 60)

    book_id_input = input("Enter book ID: ").strip()

    try:

        book_id = int(book_id_input)

    except ValueError:

        print("Please enter a valid book ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            book_id,
            title,
            author,
            category,
            available_copies
        FROM books
        WHERE book_id = ?
    """, (book_id,))

    book = cursor.fetchone()

    if not book:

        print("\nBook not found.")

        connection.close()

        return

    print("\nCurrent Details")
    print("-" * 40)

    print(f"Title            : {book[1]}")
    print(f"Author           : {book[2]}")
    print(f"Category         : {book[3]}")
    print(f"Available Copies : {book[4]}")

    print("\nEnter new details.")
    print("Press Enter to keep the existing value.")

    title = input(f"Title [{book[1]}]: ").strip()

    if not title:
        title = book[1]

    author = input(f"Author [{book[2]}]: ").strip()

    if not author:
        author = book[2]

    category = input(f"Category [{book[3]}]: ").strip()

    if not category:
        category = book[3]

    copies_input = input(f"Available copies [{book[4]}]: ").strip()

    if copies_input:

        try:

            available_copies = int(copies_input)

            if available_copies < 0:

                print("Available copies cannot be negative.")

                connection.close()

                return

        except ValueError:

            print("Please enter a valid number.")

            connection.close()

            return

    else:

        available_copies = book[4]

    try:

        cursor.execute("""
            UPDATE books
            SET
                title = ?,
                author = ?,
                category = ?,
                available_copies = ?
            WHERE book_id = ?
        """, (
            title,
            author,
            category,
            available_copies,
            book_id
        ))

        connection.commit()

        print("\nBook updated successfully!")

    except sqlite3.Error as error:

        connection.rollback()

        print("\nFailed to update book.")
        print("Database error:", error)

    finally:

        connection.close()


# ------------------------------------------------------------
# DELETE BOOK
# ------------------------------------------------------------

def delete_book():

    print("\n")
    print("=" * 60)
    print("                       DELETE BOOK")
    print("=" * 60)

    book_id_input = input("Enter book ID: ").strip()

    try:

        book_id = int(book_id_input)

    except ValueError:

        print("Please enter a valid book ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT title FROM books WHERE book_id = ?", (book_id,))

    book = cursor.fetchone()

    if not book:

        print("\nBook not found.")

        connection.close()

        return

    print(f"\nBook: {book[0]}")

    confirmation = input("Are you sure you want to delete this book? (y/n): ").strip().lower()

    if confirmation != "y":

        print("Delete operation cancelled.")

        connection.close()

        return

    try:

        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

        connection.commit()

        print("\nBook deleted successfully!")

    except sqlite3.IntegrityError:

        connection.rollback()

        print("\nThis book cannot be deleted because it has borrowing records.")

    except sqlite3.Error as error:

        connection.rollback()

        print("\nFailed to delete book.")
        print("Database error:", error)

    finally:

        connection.close()


# ============================================================
#                   MEMBER MANAGEMENT
# ============================================================

# ------------------------------------------------------------
# VIEW MEMBERS
# ------------------------------------------------------------

def view_members():

    print("\n")
    print("=" * 100)
    print("                         ALL MEMBERS")
    print("=" * 100)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT member_id, name, phone, email, registration_date FROM members ORDER BY member_id")

    members = cursor.fetchall()

    connection.close()

    if not members:

        print("\nNo members registered.")
        return

    print("-" * 100)

    print(
        f"{'ID':<5}"
        f"{'NAME':<22}"
        f"{'PHONE':<16}"
        f"{'EMAIL':<32}"
        f"{'REGISTERED':<15}"
    )

    print("-" * 100)

    for member in members:

        print(
            f"{member[0]:<5}"
            f"{member[1][:20]:<22}"
            f"{member[2]:<16}"
            f"{member[3][:30]:<32}"
            f"{member[4]:<15}"
        )

    print("-" * 100)


# ------------------------------------------------------------
# SEARCH MEMBER
# ------------------------------------------------------------

def search_member():

    print("\n")
    print("=" * 60)
    print("                       SEARCH MEMBER")
    print("=" * 60)

    search_text = input(
        "Enter name, phone or email: "
    ).strip()

    if not search_text:

        print("Search value cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    search_value = "%" + search_text + "%"

    cursor.execute("""
        SELECT
            member_id,
            name,
            phone,
            email,
            registration_date
        FROM members
        WHERE name LIKE ?
           OR phone LIKE ?
           OR email LIKE ?
        ORDER BY name
    """, (
        search_value,
        search_value,
        search_value
    ))

    members = cursor.fetchall()

    connection.close()

    if not members:

        print("\nNo matching member found.")
        return

    print("\nSearch Results")
    print("-" * 80)

    for member in members:

        print(f"Member ID        : {member[0]}")
        print(f"Name             : {member[1]}")
        print(f"Phone            : {member[2]}")
        print(f"Email            : {member[3]}")
        print(f"Registration Date: {member[4]}")

        print("-" * 80)


# ------------------------------------------------------------
# UPDATE MEMBER
# ------------------------------------------------------------

def update_member():

    print("\n")
    print("=" * 60)
    print("                       UPDATE MEMBER")
    print("=" * 60)

    member_id_input = input("Enter member ID: ").strip()

    try:

        member_id = int(member_id_input)

    except ValueError:

        print("Please enter a valid member ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            member_id,
            name,
            phone,
            email
        FROM members
        WHERE member_id = ?
    """, (member_id,))

    member = cursor.fetchone()

    if not member:

        print("\nMember not found.")

        connection.close()

        return

    print("\nCurrent Details")
    print("-" * 40)

    print(f"Name  : {member[1]}")
    print(f"Phone : {member[2]}")
    print(f"Email : {member[3]}")

    print("\nPress Enter to keep the current value.")

    name = input(
        f"Name [{member[1]}]: "
    ).strip()

    if not name:
        name = member[1]

    phone = input(
        f"Phone [{member[2]}]: "
    ).strip()

    if not phone:

        phone = member[2]

    elif not phone.isdigit():

        print("Phone number must contain only digits.")

        connection.close()

        return

    email = input(
        f"Email [{member[3]}]: "
    ).strip()

    if not email:

        email = member[3]

    elif "@" not in email or "." not in email:

        print("Please enter a valid email address.")

        connection.close()

        return

    try:

        cursor.execute("""
            UPDATE members
            SET
                name = ?,
                phone = ?,
                email = ?
            WHERE member_id = ?
        """, (
            name,
            phone,
            email,
            member_id
        ))

        connection.commit()

        print("\nMember updated successfully!")

    except sqlite3.IntegrityError:

        connection.rollback()

        print("\nEmail already exists.")

    except sqlite3.Error as error:

        connection.rollback()

        print("\nDatabase error:", error)

    finally:

        connection.close()


# ------------------------------------------------------------
# DELETE MEMBER
# ------------------------------------------------------------

def delete_member():

    print("\n")
    print("=" * 60)
    print("                       DELETE MEMBER")
    print("=" * 60)

    member_id_input = input("Enter member ID: ").strip()

    try:

        member_id = int(member_id_input)

    except ValueError:

        print("Please enter a valid member ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            member_id,
            user_id,
            name
        FROM members
        WHERE member_id = ?
    """, (member_id,))

    member = cursor.fetchone()

    if not member:

        print("\nMember not found.")

        connection.close()

        return

    print(f"\nMember: {member[2]}")

    confirmation = input(
        "Delete this member account? (y/n): "
    ).strip().lower()

    if confirmation != "y":

        print("Delete operation cancelled.")

        connection.close()

        return

    try:

        # Check whether member has borrowing records
        cursor.execute("""
            SELECT COUNT(*)
            FROM borrowings
            WHERE member_id = ?
        """, (member_id,))

        borrowing_count = cursor.fetchone()[0]

        if borrowing_count > 0:

            print(
                "\nThis member cannot be deleted because "
                "borrowing records exist."
            )

            connection.close()

            return

        # Delete member profile
        cursor.execute("""
            DELETE FROM members
            WHERE member_id = ?
        """, (member_id,))

        # Delete linked user account
        cursor.execute("""
            DELETE FROM users
            WHERE user_id = ?
        """, (member[1],))

        connection.commit()

        print("\nMember deleted successfully!")

    except sqlite3.Error as error:

        connection.rollback()

        print("\nFailed to delete member.")
        print("Database error:", error)

    finally:

        connection.close()


# ============================================================
#                       ISSUE BOOK
# ============================================================

def issue_book():

    print("\n")
    print("=" * 60)
    print("                        ISSUE BOOK")
    print("=" * 60)

    # --------------------------------------------------------
    # Member ID
    # --------------------------------------------------------

    member_id_input = input("Enter member ID: ").strip()

    try:

        member_id = int(member_id_input)

    except ValueError:

        print("Please enter a valid member ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    # Check member
    cursor.execute("""
        SELECT
            member_id,
            name
        FROM members
        WHERE member_id = ?
    """, (member_id,))

    member = cursor.fetchone()

    if not member:

        print("\nMember not found.")

        connection.close()

        return

    print(f"\nMember: {member[1]}")

    # --------------------------------------------------------
    # Book ID
    # --------------------------------------------------------

    book_id_input = input("Enter book ID: ").strip()

    try:

        book_id = int(book_id_input)

    except ValueError:

        print("Please enter a valid book ID.")

        connection.close()

        return

    # Check book
    cursor.execute("""
        SELECT
            book_id,
            title,
            available_copies
        FROM books
        WHERE book_id = ?
    """, (book_id,))

    book = cursor.fetchone()

    if not book:

        print("\nBook not found.")

        connection.close()

        return

    print(f"Book: {book[1]}")
    print(f"Available copies: {book[2]}")

    # --------------------------------------------------------
    # Check availability
    # --------------------------------------------------------

    if book[2] <= 0:

        print("\nBook is currently unavailable.")

        connection.close()

        return

    # --------------------------------------------------------
    # Check whether member already has this book
    # --------------------------------------------------------

    cursor.execute("""
        SELECT borrowing_id
        FROM borrowings
        WHERE member_id = ?
          AND book_id = ?
          AND status = 'Issued'
    """, (
        member_id,
        book_id
    ))

    existing_borrowing = cursor.fetchone()

    if existing_borrowing:

        print(
            "\nThis member has already borrowed "
            "this book and has not returned it."
        )

        connection.close()

        return

    # --------------------------------------------------------
    # Issue book
    # --------------------------------------------------------

    issue_date = date.today().isoformat()

    try:

        # Insert borrowing record
        cursor.execute("""
            INSERT INTO borrowings
            (
                book_id,
                member_id,
                issue_date,
                status
            )
            VALUES (?, ?, ?, 'Issued')
        """, (
            book_id,
            member_id,
            issue_date
        ))

        # Reduce available copies
        cursor.execute("""
            UPDATE books
            SET available_copies = available_copies - 1
            WHERE book_id = ?
        """, (book_id,))

        connection.commit()

        print("\n" + "=" * 60)
        print("                  BOOK ISSUED SUCCESSFULLY")
        print("=" * 60)

        print(f"Member       : {member[1]}")
        print(f"Book         : {book[1]}")
        print(f"Issue Date   : {issue_date}")
        print(f"Borrowing ID : {cursor.lastrowid}")

    except sqlite3.Error as error:

        connection.rollback()

        print("\nFailed to issue book.")
        print("Database error:", error)

    finally:

        connection.close()


# ============================================================
#                       RETURN BOOK
# ============================================================

def return_book():

    print("\n")
    print("=" * 60)
    print("                       RETURN BOOK")
    print("=" * 60)

    borrowing_id_input = input(
        "Enter borrowing ID: "
    ).strip()

    try:

        borrowing_id = int(borrowing_id_input)

    except ValueError:

        print("Please enter a valid borrowing ID.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # Find active borrowing
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            b.borrowing_id,
            b.book_id,
            b.member_id,
            books.title,
            members.name,
            b.issue_date,
            b.status
        FROM borrowings b

        JOIN books
            ON b.book_id = books.book_id

        JOIN members
            ON b.member_id = members.member_id

        WHERE b.borrowing_id = ?
    """, (borrowing_id,))

    borrowing = cursor.fetchone()

    if not borrowing:

        print("\nBorrowing record not found.")

        connection.close()

        return

    print("\nBorrowing Details")
    print("-" * 50)

    print(f"Borrowing ID : {borrowing[0]}")
    print(f"Book         : {borrowing[3]}")
    print(f"Member       : {borrowing[4]}")
    print(f"Issue Date   : {borrowing[5]}")
    print(f"Status       : {borrowing[6]}")

    # --------------------------------------------------------
    # Already returned
    # --------------------------------------------------------

    if borrowing[6] == "Returned":

        print("\nThis book has already been returned.")

        connection.close()

        return

    # --------------------------------------------------------
    # Return book
    # --------------------------------------------------------

    return_date = date.today().isoformat()

    try:

        # Update borrowing
        cursor.execute("""
            UPDATE borrowings
            SET
                return_date = ?,
                status = 'Returned'
            WHERE borrowing_id = ?
        """, (
            return_date,
            borrowing_id
        ))

        # Increase available copies
        cursor.execute("""
            UPDATE books
            SET available_copies = available_copies + 1
            WHERE book_id = ?
        """, (borrowing[1],))

        connection.commit()

        print("\n" + "=" * 60)
        print("                 BOOK RETURNED SUCCESSFULLY")
        print("=" * 60)

        print(f"Book        : {borrowing[3]}")
        print(f"Member      : {borrowing[4]}")
        print(f"Return Date : {return_date}")

    except sqlite3.Error as error:

        connection.rollback()

        print("\nFailed to return book.")
        print("Database error:", error)

    finally:

        connection.close()


# ============================================================
#                    VIEW BORROWINGS
# ============================================================

def view_borrowings():

    print("\n")
    print("=" * 110)
    print("                         BORROWING RECORDS")
    print("=" * 110)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            b.borrowing_id,
            books.title,
            members.name,
            b.issue_date,
            b.return_date,
            b.status
        FROM borrowings b

        JOIN books
            ON b.book_id = books.book_id

        JOIN members
            ON b.member_id = members.member_id

        ORDER BY b.borrowing_id
    """)

    borrowings = cursor.fetchall()

    connection.close()

    if not borrowings:

        print("\nNo borrowing records found.")
        return

    print("-" * 110)

    print(
        f"{'ID':<6}"
        f"{'BOOK':<30}"
        f"{'MEMBER':<22}"
        f"{'ISSUED':<14}"
        f"{'RETURNED':<14}"
        f"{'STATUS':<12}"
    )

    print("-" * 110)

    for borrowing in borrowings:

        return_date = borrowing[4]

        if return_date is None:
            return_date = "-"

        print(
            f"{borrowing[0]:<6}"
            f"{borrowing[1][:28]:<30}"
            f"{borrowing[2][:20]:<22}"
            f"{borrowing[3]:<14}"
            f"{return_date:<14}"
            f"{borrowing[5]:<12}"
        )

    print("-" * 110)


# ============================================================
#                 BOOK MANAGEMENT MENU
# ============================================================

def book_management_menu():

    while True:

        print("\n")
        print("=" * 60)
        print("                     BOOK MANAGEMENT")
        print("=" * 60)

        print("1. Add Book")
        print("2. View All Books")
        print("3. Search Book")
        print("4. Update Book")
        print("5. Delete Book")
        print("6. Back")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            add_book()
            pause()

        elif choice == "2":

            view_books()
            pause()

        elif choice == "3":

            search_book()
            pause()

        elif choice == "4":

            update_book()
            pause()

        elif choice == "5":

            delete_book()
            pause()

        elif choice == "6":

            break

        else:

            print("\nInvalid choice. Please try again.")


# ============================================================
#                 MEMBER MANAGEMENT MENU
# ============================================================

def member_management_menu():

    while True:

        print("\n")
        print("=" * 60)
        print("                    MEMBER MANAGEMENT")
        print("=" * 60)

        print("1. View All Members")
        print("2. Search Member")
        print("3. Update Member")
        print("4. Delete Member")
        print("5. Back")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            view_members()
            pause()

        elif choice == "2":

            search_member()
            pause()

        elif choice == "3":

            update_member()
            pause()

        elif choice == "4":

            delete_member()
            pause()

        elif choice == "5":

            break

        else:

            print("\nInvalid choice. Please try again.")


def view_book_requests():
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                br.request_id,
                m.member_id,
                m.name,
                b.book_id,
                b.title,
                br.request_date,
                br.status,
                b.available_copies
            FROM book_requests br
            JOIN members m
                ON br.member_id = m.member_id
            JOIN books b
                ON br.book_id = b.book_id
            ORDER BY
                CASE
                    WHEN br.status = 'Pending' THEN 1
                    WHEN br.status = 'Approved' THEN 2
                    ELSE 3
                END,
                br.request_id DESC
        """)

        requests = cursor.fetchall()

        print("\n" + "=" * 100)
        print("                         BOOK REQUESTS")
        print("=" * 100)

        if not requests:
            print("\nNo book requests found.")
            return

        print(
            f"{'Req ID':<8}"
            f"{'Member ID':<11}"
            f"{'Member Name':<20}"
            f"{'Book ID':<9}"
            f"{'Book':<28}"
            f"{'Date':<12}"
            f"{'Status':<12}"
            f"{'Copies':<8}"
        )

        print("-" * 108)

        for request in requests:
            print(
                f"{request[0]:<8}"
                f"{request[1]:<11}"
                f"{request[2][:18]:<20}"
                f"{request[3]:<9}"
                f"{request[4][:26]:<28}"
                f"{request[5]:<12}"
                f"{request[6]:<12}"
                f"{request[7]:<8}"
            )

        print("-" * 108)

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()


def process_book_request():
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                br.request_id,
                m.member_id,
                m.name,
                b.book_id,
                b.title,
                b.available_copies,
                br.status
            FROM book_requests br
            JOIN members m
                ON br.member_id = m.member_id
            JOIN books b
                ON br.book_id = b.book_id
            WHERE br.status = 'Pending'
            ORDER BY br.request_id
        """)

        requests = cursor.fetchall()

        if not requests:
            print("\nNo pending book requests.")
            return

        print("\n" + "=" * 90)
        print("                    PENDING BOOK REQUESTS")
        print("=" * 90)

        for request in requests:
            print(f"Request ID      : {request[0]}")
            print(f"Member ID       : {request[1]}")
            print(f"Member Name     : {request[2]}")
            print(f"Book ID         : {request[3]}")
            print(f"Book            : {request[4]}")
            print(f"Available Copies: {request[5]}")
            print(f"Status          : {request[6]}")
            print("-" * 90)

        try:
            request_id = int(input("\nEnter Request ID to process: "))
        except ValueError:
            print("\nInvalid Request ID.")
            return

        cursor.execute("""
            SELECT
                br.request_id,
                br.member_id,
                br.book_id,
                b.title,
                b.available_copies
            FROM book_requests br
            JOIN books b
                ON br.book_id = b.book_id
            WHERE br.request_id = ?
              AND br.status = 'Pending'
        """, (request_id,))

        request = cursor.fetchone()

        if not request:
            print("\nPending request not found.")
            return

        print("\nSelected Request")
        print("-" * 40)
        print(f"Request ID      : {request[0]}")
        print(f"Member ID       : {request[1]}")
        print(f"Book ID         : {request[2]}")
        print(f"Book            : {request[3]}")
        print(f"Available Copies: {request[4]}")

        print("\n1. Approve")
        print("2. Reject")
        print("3. Cancel")

        action = input("\nEnter your choice: ").strip()

        if action == "1":

            cursor.execute("""
                UPDATE book_requests
                SET status = 'Approved'
                WHERE request_id = ?
            """, (request_id,))

            connection.commit()

            print("\nBook request approved.")
            print(f"Member ID: {request[1]}")
            print(f"Book ID  : {request[2]}")
            print("\nYou can now use 'Issue Book' to issue this book.")

        elif action == "2":

            cursor.execute("""
                UPDATE book_requests
                SET status = 'Rejected'
                WHERE request_id = ?
            """, (request_id,))

            connection.commit()

            print("\nBook request rejected.")

        elif action == "3":
            print("\nRequest processing cancelled.")

        else:
            print("\nInvalid choice.")

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()


# ============================================================
#                    LIBRARIAN MENU
# ============================================================

def librarian_menu(user_id, username):
    while True:
        print("\n" + "=" * 55)
        print("                  LIBRARIAN MENU")
        print("=" * 55)
        print(f"Welcome, {username}!")
        print()
        print("1. Book Management")
        print("2. Member Management")
        print("3. Book Requests")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. View Borrowings")
        print("7. Logout")
        print("=" * 55)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            book_management_menu()
            pause()

        elif choice == "2":
            member_management_menu()
            pause()

        elif choice == "3":
            while True:
                print("\n" + "=" * 50)
                print("             BOOK REQUEST MANAGEMENT")
                print("=" * 50)
                print("1. View Book Requests")
                print("2. Process Book Request")
                print("3. Back")
                print("=" * 50)

                request_choice = input("Enter your choice: ").strip()

                if request_choice == "1":
                    view_book_requests()
                    pause()

                elif request_choice == "2":
                    process_book_request()
                    pause()

                elif request_choice == "3":
                    break

                else:
                    print("\nInvalid choice.")

        elif choice == "4":
            issue_book()
            pause()

        elif choice == "5":
            return_book()
            pause()

        elif choice == "6":
            view_borrowings()
            pause()

        elif choice == "7":
            print("\nLogging out...")
            break

        else:
            print("\nInvalid choice. Please try again.")


# ============================================================
#                    MEMBER FUNCTIONS
# ============================================================

def member_view_books():

    print("\n")
    print("=" * 90)
    print("                      AVAILABLE BOOKS")
    print("=" * 90)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            book_id,
            title,
            author,
            category,
            available_copies
        FROM books
        WHERE available_copies > 0
        ORDER BY title
    """)

    books = cursor.fetchall()

    connection.close()

    if not books:

        print("\nNo books are currently available.")
        return

    print("-" * 90)

    print(
        f"{'ID':<5}"
        f"{'TITLE':<28}"
        f"{'AUTHOR':<22}"
        f"{'CATEGORY':<20}"
        f"{'COPIES':<8}"
    )

    print("-" * 90)

    for book in books:

        print(
            f"{book[0]:<5}"
            f"{book[1][:26]:<28}"
            f"{book[2][:20]:<22}"
            f"{book[3][:18]:<20}"
            f"{book[4]:<8}"
        )

    print("-" * 90)


def member_search_books():

    print("\n")
    print("=" * 60)
    print("                       SEARCH BOOK")
    print("=" * 60)

    search_text = input(
        "Enter title, author or category: "
    ).strip()

    if not search_text:

        print("Search value cannot be empty.")
        return

    connection = connect_db()
    cursor = connection.cursor()

    search_value = "%" + search_text + "%"

    cursor.execute("""
        SELECT
            book_id,
            title,
            author,
            category,
            available_copies
        FROM books
        WHERE title LIKE ?
           OR author LIKE ?
           OR category LIKE ?
        ORDER BY title
    """, (
        search_value,
        search_value,
        search_value
    ))

    books = cursor.fetchall()

    connection.close()

    if not books:

        print("\nNo matching books found.")
        return

    print("\nSearch Results")
    print("-" * 80)

    for book in books:

        print(f"Book ID          : {book[0]}")
        print(f"Title            : {book[1]}")
        print(f"Author           : {book[2]}")
        print(f"Category         : {book[3]}")
        print(f"Available Copies : {book[4]}")

        print("-" * 80)


def view_my_profile(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                m.member_id,
                m.name,
                m.phone,
                m.email,
                m.registration_date,
                u.username
            FROM members m
            JOIN users u
                ON m.user_id = u.user_id
            WHERE m.user_id = ?
        """, (user_id,))

        member = cursor.fetchone()

        if not member:
            print("\nMember profile not found.")
            return

        print("\n" + "=" * 50)
        print("                 MY PROFILE")
        print("=" * 50)

        print(f"Member ID        : {member[0]}")
        print(f"Name             : {member[1]}")
        print(f"Username         : {member[5]}")
        print(f"Phone            : {member[2]}")
        print(f"Email            : {member[3]}")
        print(f"Registration Date: {member[4]}")

        print("=" * 50)

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()

def view_my_borrowed_books(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT member_id
            FROM members
            WHERE user_id = ?
        """, (user_id,))

        member = cursor.fetchone()

        if not member:
            print("\nMember profile not found.")
            return

        member_id = member[0]

        cursor.execute("""
            SELECT
                br.borrowing_id,
                b.book_id,
                b.title,
                b.author,
                br.issue_date,
                br.status
            FROM borrowings br
            JOIN books b
                ON br.book_id = b.book_id
            WHERE br.member_id = ?
              AND br.status = 'Issued'
            ORDER BY br.issue_date DESC
        """, (member_id,))

        borrowed_books = cursor.fetchall()

        print("\n" + "=" * 90)
        print("                    MY BORROWED BOOKS")
        print("=" * 90)

        if not borrowed_books:
            print("\nYou currently have no borrowed books.")
            return

        print(
            f"{'Borrowing ID':<14}"
            f"{'Book ID':<9}"
            f"{'Title':<30}"
            f"{'Author':<20}"
            f"{'Issue Date':<12}"
            f"{'Status':<10}"
        )

        print("-" * 95)

        for book in borrowed_books:
            print(
                f"{book[0]:<14}"
                f"{book[1]:<9}"
                f"{book[2][:28]:<30}"
                f"{book[3][:18]:<20}"
                f"{book[4]:<12}"
                f"{book[5]:<10}"
            )

        print("-" * 95)

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()

def view_my_borrowing_history(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT member_id
            FROM members
            WHERE user_id = ?
        """, (user_id,))

        member = cursor.fetchone()

        if not member:
            print("\nMember profile not found.")
            return

        member_id = member[0]

        cursor.execute("""
            SELECT
                br.borrowing_id,
                b.book_id,
                b.title,
                b.author,
                br.issue_date,
                br.return_date,
                br.status
            FROM borrowings br
            JOIN books b
                ON br.book_id = b.book_id
            WHERE br.member_id = ?
            ORDER BY br.issue_date DESC
        """, (member_id,))

        history = cursor.fetchall()

        print("\n" + "=" * 105)
        print("                    MY BORROWING HISTORY")
        print("=" * 105)

        if not history:
            print("\nYou do not have any borrowing history.")
            return

        print(
            f"{'Borrowing ID':<14}"
            f"{'Book ID':<9}"
            f"{'Title':<28}"
            f"{'Author':<18}"
            f"{'Issue Date':<13}"
            f"{'Return Date':<13}"
            f"{'Status':<10}"
        )

        print("-" * 105)

        for record in history:
            return_date = record[5] if record[5] else "-"

            print(
                f"{record[0]:<14}"
                f"{record[1]:<9}"
                f"{record[2][:26]:<28}"
                f"{record[3][:16]:<18}"
                f"{record[4]:<13}"
                f"{return_date:<13}"
                f"{record[6]:<10}"
            )

        print("-" * 105)

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()


def request_book(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        # Get member ID from logged-in user
        cursor.execute("""
            SELECT member_id, name
            FROM members
            WHERE user_id = ?
        """, (user_id,))

        member = cursor.fetchone()

        if not member:
            print("\nMember profile not found.")
            return

        member_id = member[0]
        member_name = member[1]

        print("\n" + "=" * 60)
        print("              REQUEST A BOOK")
        print("=" * 60)

        # Display all books
        cursor.execute("""
            SELECT book_id, title, author, category, available_copies
            FROM books
            ORDER BY title
        """)

        books = cursor.fetchall()

        if not books:
            print("\nNo books are available in the library.")
            return

        print(
            f"\n{'ID':<5}"
            f"{'Title':<30}"
            f"{'Author':<20}"
            f"{'Category':<15}"
            f"{'Available':<10}"
        )

        print("-" * 80)

        for book in books:
            print(
                f"{book[0]:<5}"
                f"{book[1][:28]:<30}"
                f"{book[2][:18]:<20}"
                f"{book[3][:13]:<15}"
                f"{book[4]:<10}"
            )

        print("-" * 80)

        try:
            book_id = int(input("\nEnter Book ID to request: "))
        except ValueError:
            print("\nInvalid Book ID.")
            return

        # Check whether book exists
        cursor.execute("""
            SELECT book_id, title, available_copies
            FROM books
            WHERE book_id = ?
        """, (book_id,))

        book = cursor.fetchone()

        if not book:
            print("\nBook not found.")
            return

        book_id = book[0]
        book_title = book[1]
        available_copies = book[2]

        # Check if member already has this book
        cursor.execute("""
            SELECT borrowing_id
            FROM borrowings
            WHERE member_id = ?
              AND book_id = ?
              AND status = 'Issued'
        """, (member_id, book_id))

        existing_borrowing = cursor.fetchone()

        if existing_borrowing:
            print("\nYou already have this book issued.")
            return

        # Check for existing pending request
        cursor.execute("""
            SELECT request_id
            FROM book_requests
            WHERE member_id = ?
              AND book_id = ?
              AND status = 'Pending'
        """, (member_id, book_id))

        existing_request = cursor.fetchone()

        if existing_request:
            print("\nYou already have a pending request for this book.")
            return

        # Create request
        request_date = date.today().isoformat()

        cursor.execute("""
            INSERT INTO book_requests
            (member_id, book_id, request_date, status)
            VALUES (?, ?, ?, 'Pending')
        """, (member_id, book_id, request_date))

        connection.commit()

        print("\n" + "=" * 60)
        print("BOOK REQUEST SUBMITTED SUCCESSFULLY")
        print("=" * 60)
        print(f"Member          : {member_name}")
        print(f"Book            : {book_title}")
        print(f"Available Copies: {available_copies}")
        print(f"Request Date    : {request_date}")
        print("Status          : Pending")

        if available_copies == 0:
            print("\nNote: This book is currently unavailable.")
            print("The librarian will review your request when copies are available.")

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()


def view_my_requests(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT member_id
            FROM members
            WHERE user_id = ?
        """, (user_id,))

        member = cursor.fetchone()

        if not member:
            print("\nMember profile not found.")
            return

        member_id = member[0]

        cursor.execute("""
            SELECT
                br.request_id,
                b.title,
                b.author,
                br.request_date,
                br.status
            FROM book_requests br
            JOIN books b
                ON br.book_id = b.book_id
            WHERE br.member_id = ?
            ORDER BY br.request_id DESC
        """, (member_id,))

        requests = cursor.fetchall()

        print("\n" + "=" * 75)
        print("                     MY BOOK REQUESTS")
        print("=" * 75)

        if not requests:
            print("\nYou have not made any book requests.")
            return

        print(
            f"{'Request ID':<12}"
            f"{'Book':<30}"
            f"{'Author':<20}"
            f"{'Date':<12}"
            f"{'Status':<12}"
        )

        print("-" * 86)

        for request in requests:
            print(
                f"{request[0]:<12}"
                f"{request[1][:28]:<30}"
                f"{request[2][:18]:<20}"
                f"{request[3]:<12}"
                f"{request[4]:<12}"
            )

        print("-" * 86)

    except sqlite3.Error as error:
        print(f"\nDatabase error: {error}")

    finally:
        connection.close()

# ============================================================
#                       MEMBER MENU
# ============================================================

def member_menu(user_id, username):
    while True:
        print("\n" + "=" * 55)
        print("                    MEMBER MENU")
        print("=" * 55)
        print(f"Welcome, {username}!")
        print()
        print("1. View My Profile")
        print("2. View Available Books")
        print("3. Search Books")
        print("4. Request a Book")
        print("5. View My Requests")
        print("6. View My Borrowed Books")
        print("7. View My Borrowing History")
        print("8. Logout")
        print("=" * 55)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_my_profile(user_id)
            pause()

        elif choice == "2":
            member_view_books()
            pause()

        elif choice == "3":
            member_search_books()
            pause()

        elif choice == "4":
            request_book(user_id)
            pause()

        elif choice == "5":
            view_my_requests(user_id)
            pause()

        elif choice == "6":
            view_my_borrowed_books(user_id)
            pause()

        elif choice == "7":
            view_my_borrowing_history(user_id)
            pause()

        elif choice == "8":
            print("\nLogging out...")
            break

        else:
            print("\nInvalid choice. Please try again.")


# ============================================================
#                       MAIN MENU
# ============================================================

def main():

    # Create all database tables
    create_tables()

    while True:

        print("\n")
        print("=" * 60)
        print("              LIBRARY MANAGEMENT SYSTEM")
        print("=" * 60)

        print("1. Sign Up")
        print("2. Sign In")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            sign_up()
            pause()

        elif choice == "2":

            sign_in()
            pause()

        elif choice == "3":

            print("\nThank you for using Library Management System.")
            break

        else:

            print("\nInvalid choice. Please try again.")




if __name__ == "__main__":
    main()