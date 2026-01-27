"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ============== Auth ==============

class LoginForm(BaseModel):
    """Login form data."""
    username: str
    password: str


# ============== Product ==============

class ProductBase(BaseModel):
    """Base product schema."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., pattern="^(crepes_sucrees|crepes_salees|gaufres|box)$")
    price: float = Field(..., gt=0)
    image_filename: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_best_seller: bool = False
    display_order: int = 0


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, pattern="^(crepes_sucrees|crepes_salees|gaufres|box)$")
    price: Optional[float] = Field(None, gt=0)
    image_filename: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_best_seller: Optional[bool] = None
    display_order: Optional[int] = None


class ProductResponse(ProductBase):
    """Product response schema."""
    id: int

    class Config:
        from_attributes = True


# ============== Schedule ==============

class ScheduleBase(BaseModel):
    """Base schedule schema."""
    day_of_week: int = Field(..., ge=0, le=6)
    place: str = Field(..., min_length=1, max_length=200)
    start_time: str = Field(..., pattern="^[0-2][0-9]:[0-5][0-9]$")
    end_time: str = Field(..., pattern="^[0-2][0-9]:[0-5][0-9]$")
    is_active: bool = True


class ScheduleCreate(ScheduleBase):
    """Schema for creating a schedule entry."""
    pass


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule entry."""
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    place: Optional[str] = Field(None, min_length=1, max_length=200)
    start_time: Optional[str] = Field(None, pattern="^[0-2][0-9]:[0-5][0-9]$")
    end_time: Optional[str] = Field(None, pattern="^[0-2][0-9]:[0-5][0-9]$")
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    """Schedule response schema."""
    id: int
    day_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============== Location ==============

class LocationBase(BaseModel):
    """Base location schema."""
    today_location: Optional[str] = None
    today_hours: Optional[str] = None
    daily_message: Optional[str] = None


class LocationUpdate(LocationBase):
    """Schema for updating location."""
    pass


class LocationResponse(LocationBase):
    """Location response schema."""
    id: int

    class Config:
        from_attributes = True


# ============== Settings ==============

class SettingsBase(BaseModel):
    """Base settings schema."""
    hours_weekday: str = "11h30 - 14h00"
    hours_evening: str = "18h00 - 21h00"
    hours_weekend: str = "09h00 - 15h00"
    instagram_url: str = "https://instagram.com"
    tiktok_url: str = "https://tiktok.com"
    site_name: str = "KIOSQUE DU PARC"
    slogan: str = "Du sucré, du salé, fait minute."


class SettingsUpdate(BaseModel):
    """Schema for updating settings."""
    hours_weekday: Optional[str] = None
    hours_evening: Optional[str] = None
    hours_weekend: Optional[str] = None
    instagram_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    site_name: Optional[str] = None
    slogan: Optional[str] = None


class SettingsResponse(SettingsBase):
    """Settings response schema."""
    id: int

    class Config:
        from_attributes = True


# ============== API Responses ==============

class APIProductResponse(BaseModel):
    """Product response for public API (frontend)."""
    id: int
    name: str
    category: str
    category_label: str
    price: float
    image: str
    alt: str
    tags: List[str]
    bestseller: bool

    class Config:
        from_attributes = True


class APILocationResponse(BaseModel):
    """Location response for public API."""
    place: str
    hours: str
    message: Optional[str] = None


class APIScheduleResponse(BaseModel):
    """Schedule response for public API."""
    day: str
    day_index: int
    place: str
    hours: str
    is_weekend: bool


# ============== Contact ==============

class ContactCreate(BaseModel):
    """Schema for creating a contact message."""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    phone: Optional[str] = Field(None, max_length=20)
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)


class ContactResponse(BaseModel):
    """Contact message response schema."""
    id: int
    name: str
    email: str
    phone: Optional[str]
    subject: str
    message: str
    created_at: str
    is_read: bool

    class Config:
        from_attributes = True
