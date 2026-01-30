"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models import Admin, Product, Schedule, Location, Settings, ContactMessage
from app.auth import hash_password


# ============== Admin ==============

def get_admin_by_username(db: Session, username: str) -> Optional[Admin]:
    """Get admin by username."""
    return db.query(Admin).filter(Admin.username == username).first()


def create_admin(db: Session, username: str, password: str) -> Admin:
    """Create a new admin user."""
    admin = Admin(
        username=username,
        password_hash=hash_password(password),
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def get_admin_count(db: Session) -> int:
    """Get total number of admins."""
    return db.query(Admin).count()


# ============== Product ==============

def get_products(
    db: Session,
    category: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = False,
    best_sellers_only: bool = False
) -> List[Product]:
    """Get products with optional filters."""
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active == True)

    if best_sellers_only:
        query = query.filter(Product.is_best_seller == True)

    if category:
        query = query.filter(Product.category == category)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    return query.order_by(Product.display_order, Product.id).all()


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get a single product by ID."""
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, **kwargs) -> Product:
    """Create a new product."""
    product = Product(**kwargs)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, **kwargs) -> Optional[Product]:
    """Update a product."""
    product = get_product(db, product_id)
    if not product:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    """Delete a product."""
    product = get_product(db, product_id)
    if not product:
        return False

    db.delete(product)
    db.commit()
    return True


def get_product_count(db: Session, active_only: bool = False) -> int:
    """Get product count."""
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.count()


def get_bestseller_count(db: Session) -> int:
    """Get best seller count."""
    return db.query(Product).filter(
        Product.is_active == True,
        Product.is_best_seller == True
    ).count()


# ============== Schedule ==============

def get_schedules(db: Session, active_only: bool = False) -> List[Schedule]:
    """Get all schedules ordered by day."""
    query = db.query(Schedule)
    if active_only:
        query = query.filter(Schedule.is_active == True)
    return query.order_by(Schedule.day_of_week, Schedule.start_time).all()


def get_schedule(db: Session, schedule_id: int) -> Optional[Schedule]:
    """Get a single schedule by ID."""
    return db.query(Schedule).filter(Schedule.id == schedule_id).first()


def create_schedule(db: Session, **kwargs) -> Schedule:
    """Create a new schedule entry."""
    schedule = Schedule(**kwargs)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def update_schedule(db: Session, schedule_id: int, **kwargs) -> Optional[Schedule]:
    """Update a schedule entry."""
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)
    return schedule


def delete_schedule(db: Session, schedule_id: int) -> bool:
    """Delete a schedule entry."""
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        return False

    db.delete(schedule)
    db.commit()
    return True


# ============== Location ==============

def get_location(db: Session) -> Optional[Location]:
    """Get the current location (singleton)."""
    return db.query(Location).first()


def update_location(db: Session, **kwargs) -> Location:
    """Update or create location."""
    location = get_location(db)

    if not location:
        location = Location(**kwargs)
        db.add(location)
    else:
        for key, value in kwargs.items():
            setattr(location, key, value)

    db.commit()
    db.refresh(location)
    return location


# ============== Settings ==============

def get_settings(db: Session) -> Optional[Settings]:
    """Get settings (singleton)."""
    return db.query(Settings).first()


def update_settings(db: Session, **kwargs) -> Settings:
    """Update or create settings."""
    settings = get_settings(db)

    if not settings:
        settings = Settings(**kwargs)
        db.add(settings)
    else:
        for key, value in kwargs.items():
            if value is not None:
                setattr(settings, key, value)

    db.commit()
    db.refresh(settings)
    return settings


def ensure_settings_exist(db: Session) -> Settings:
    """Ensure settings row exists, create with defaults if not."""
    settings = get_settings(db)
    if not settings:
        settings = Settings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def ensure_location_exists(db: Session) -> Location:
    """Ensure location row exists, create with defaults if not."""
    location = get_location(db)
    if not location:
        location = Location(
            today_location="Parc de la Mairie - Centre-ville",
            today_hours="11h30 - 14h00 / 18h00 - 21h00"
        )
        db.add(location)
        db.commit()
        db.refresh(location)
    return location


# ============== Contact Messages ==============

def get_contact_messages(db: Session, unread_only: bool = False) -> List[ContactMessage]:
    """Get all contact messages ordered by date (newest first)."""
    query = db.query(ContactMessage)
    if unread_only:
        query = query.filter(ContactMessage.is_read == False)
    return query.order_by(ContactMessage.created_at.desc()).all()


def get_contact_message(db: Session, message_id: int) -> Optional[ContactMessage]:
    """Get a single contact message by ID."""
    return db.query(ContactMessage).filter(ContactMessage.id == message_id).first()


def create_contact_message(db: Session, **kwargs) -> ContactMessage:
    """Create a new contact message."""
    message = ContactMessage(**kwargs)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def mark_message_as_read(db: Session, message_id: int) -> Optional[ContactMessage]:
    """Mark a message as read."""
    message = get_contact_message(db, message_id)
    if not message:
        return None
    message.is_read = True
    db.commit()
    db.refresh(message)
    return message


def delete_contact_message(db: Session, message_id: int) -> bool:
    """Delete a contact message."""
    message = get_contact_message(db, message_id)
    if not message:
        return False
    db.delete(message)
    db.commit()
    return True


def get_unread_message_count(db: Session) -> int:
    """Get count of unread messages."""
    return db.query(ContactMessage).filter(ContactMessage.is_read == False).count()


def get_message_count(db: Session) -> int:
    """Get total message count."""
    return db.query(ContactMessage).count()
