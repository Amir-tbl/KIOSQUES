"""
SQLAlchemy models for KIOSQUE DU PARC.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.db import Base
import enum
from datetime import datetime


class ProductCategory(str, enum.Enum):
    """Product categories."""
    CREPES_SUCREES = "crepes_sucrees"
    CREPES_SALEES = "crepes_salees"
    GAUFRES = "gaufres"
    BOX = "box"


class DayOfWeek(int, enum.Enum):
    """Days of the week (0 = Monday, 6 = Sunday)."""
    LUNDI = 0
    MARDI = 1
    MERCREDI = 2
    JEUDI = 3
    VENDREDI = 4
    SAMEDI = 5
    DIMANCHE = 6


class Admin(Base):
    """Admin user model."""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)


class Product(Base):
    """Product model for menu items."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # Uses ProductCategory values
    price = Column(Float, nullable=False)
    image_filename = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_best_seller = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)


class Schedule(Base):
    """Weekly schedule model."""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Monday-Sunday)
    place = Column(String(200), nullable=False)  # "Ouvert" or "Fermé"
    start_time = Column(String(5), nullable=True)  # HH:MM format (optional if closed)
    end_time = Column(String(5), nullable=True)    # HH:MM format (optional if closed)
    is_active = Column(Boolean, default=True)


class Location(Base):
    """Current location and daily message."""
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, index=True)
    today_location = Column(String(300), nullable=True)
    today_hours = Column(String(100), nullable=True)
    daily_message = Column(Text, nullable=True)  # Optional message (e.g., "Closed today")


class Settings(Base):
    """General settings (singleton pattern - only one row)."""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    # General hours text
    hours_weekday = Column(String(100), default="11h30 - 14h00")
    hours_evening = Column(String(100), default="18h00 - 21h00")
    hours_weekend = Column(String(100), default="09h00 - 15h00")
    # Social links
    instagram_url = Column(String(255), default="https://instagram.com")
    tiktok_url = Column(String(255), default="https://tiktok.com")
    # Site info
    site_name = Column(String(100), default="KIOSQUE DU PARC")
    slogan = Column(String(200), default="Du sucré, du salé, fait minute.")


class ContactMessage(Base):
    """Contact form messages."""
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)


# Day names mapping for display
DAY_NAMES = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche"
}

# Category names mapping for display
CATEGORY_NAMES = {
    "crepes_sucrees": "Crêpes sucrées",
    "crepes_salees": "Crêpes salées",
    "gaufres": "Gaufres",
    "box": "Box"
}
