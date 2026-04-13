import sqlite3
from config import DB_PATH
import os
from config import USERS_DIR

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def clear_all_users_and_files():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()

    # delete all JSON files
    for file in USERS_DIR.glob("*.json"):
        try:
            file.unlink()
        except Exception as e:
            print(f"Error deleting {file}: {e}")


def delete_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False

    cursor.execute(
        "DELETE FROM users WHERE username = ?",
        (username,)
    )
    conn.commit()
    conn.close()

    user_file = USERS_DIR / f"{username}.json"
    if user_file.exists():
        try:
            user_file.unlink()
        except Exception as e:
            print(f"Error deleting file {user_file}: {e}")

    return True



def main():
    while True:
        print("\n=== Database Menu ===")
        print("1. Exit")
        print("2. Clear all users from database and delete all user JSON files")
        print("3. Delete a specific user and their JSON file")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print("Exiting...")
            break

        elif choice == "2":
            confirm = input("Are you sure you want to delete ALL users and JSON files? (yes/no): ").strip().lower()
            if confirm == "yes":
                clear_all_users_and_files()
                print("All users deleted from database and all JSON files removed.")
            else:
                print("Operation cancelled.")

        elif choice == "3":
            username = input("Enter username to delete: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue

            success = delete_user(username)
            if success:
                print(f"User '{username}' and their JSON file were deleted.")
            else:
                print(f"User '{username}' was not found.")

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()