from getpass import getpass

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def main():
    db = SessionLocal()

    try:
        email = input("Enter admin email: ").strip().lower()
        phone = input("Enter admin phone number: ").strip()
        password = getpass("Create admin password: ")

        existing = db.query(User).filter(
            (User.email == email) | (User.phone == phone)
        ).first()

        if existing:
            print("That email or phone number is already registered.")
            return

        admin = User(
            full_name="System Administrator",
            email=email,
            phone=phone,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_approved=True,
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()