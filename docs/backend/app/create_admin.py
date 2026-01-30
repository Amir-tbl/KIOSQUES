"""
Script to create an admin user.
Run with: python -m app.create_admin [username] [password]
"""
import sys
from app.db import SessionLocal, init_db
from app.crud import get_admin_by_username, create_admin, get_admin_count
from app.settings import INIT_ADMIN_USERNAME, INIT_ADMIN_PASSWORD


def main():
    """Create an admin user."""
    # Initialize database
    init_db()

    # Get credentials from args or environment
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = INIT_ADMIN_USERNAME
        password = INIT_ADMIN_PASSWORD
        print(f"Using default credentials from environment/settings")

    # Create session
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing = get_admin_by_username(db, username)
        if existing:
            print(f"[ERROR] Admin '{username}' already exists!")
            sys.exit(1)

        # Create admin
        admin = create_admin(db, username, password)
        print(f"[OK] Admin '{admin.username}' created successfully!")
        print(f"     You can now login at /admin/login")

        if password == "admin123":
            print(f"\n[WARNING] You are using the default password.")
            print(f"          Please change it immediately after first login!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
