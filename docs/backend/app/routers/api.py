"""
Public API routes for the frontend.
These endpoints return JSON data for the website.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import get_db
from app.crud import (
    get_products, get_location, get_schedules, get_settings,
    create_contact_message
)
from app.models import DAY_NAMES, CATEGORY_NAMES
from app.schemas import ContactCreate

router = APIRouter(prefix="/api", tags=["API"])


def format_product_for_api(product) -> dict:
    """Format a product for the frontend API."""
    # Determine tags
    tags = []
    if product.category in ["crepes_sucrees", "gaufres"]:
        tags.append("sweet")
    elif product.category in ["crepes_salees", "box"]:
        tags.append("savory")

    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "category_label": CATEGORY_NAMES.get(product.category, product.category),
        "price": product.price,
        "image": f"assets/img/{product.image_filename}" if product.image_filename else "",
        "alt": product.description or product.name,
        "tags": tags,
        "bestseller": product.is_best_seller
    }


@router.get("/products")
def api_get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get all active products.
    Supports filtering by category and search by name.
    """
    products = get_products(
        db,
        category=category,
        search=search,
        active_only=True
    )
    return [format_product_for_api(p) for p in products]


@router.get("/products/best-sellers")
def api_get_best_sellers(db: Session = Depends(get_db)) -> List[dict]:
    """Get best-selling products."""
    products = get_products(db, active_only=True, best_sellers_only=True)
    return [format_product_for_api(p) for p in products]


@router.get("/location/today")
def api_get_location_today(db: Session = Depends(get_db)) -> dict:
    """Get today's location and message."""
    location = get_location(db)
    if not location:
        return {
            "place": "Emplacement non defini",
            "hours": "",
            "message": None
        }
    return {
        "place": location.today_location or "Emplacement non defini",
        "hours": location.today_hours or "",
        "message": location.daily_message
    }


@router.get("/schedule")
def api_get_schedule(db: Session = Depends(get_db)) -> List[dict]:
    """Get weekly schedule."""
    schedules = get_schedules(db, active_only=True)

    # Group by day and format
    result = []
    for schedule in schedules:
        # Format hours only if status is "Ouvert" and times exist
        if schedule.place == "Ouvert" and schedule.start_time and schedule.end_time:
            hours = f"{schedule.start_time} - {schedule.end_time}"
        else:
            hours = "-"

        # Check if same day already exists (multiple time slots)
        existing = next(
            (s for s in result if s["day_index"] == schedule.day_of_week and s["place"] == schedule.place),
            None
        )
        if existing and hours != "-":
            existing["hours"] += f" / {hours}"
        else:
            result.append({
                "day": DAY_NAMES.get(schedule.day_of_week, ""),
                "day_index": schedule.day_of_week,
                "place": schedule.place,
                "hours": hours,
                "is_weekend": schedule.day_of_week >= 5
            })

    return sorted(result, key=lambda x: x["day_index"])


@router.get("/settings")
def api_get_settings(db: Session = Depends(get_db)) -> dict:
    """Get general settings."""
    settings = get_settings(db)
    if not settings:
        return {
            "hours_weekday": "11h30 - 14h00",
            "hours_evening": "18h00 - 21h00",
            "hours_weekend": "09h00 - 15h00",
            "instagram_url": "https://instagram.com",
            "tiktok_url": "https://tiktok.com",
            "site_name": "KIOSQUE DU PARC",
            "slogan": "Du sucré, du salé, fait minute."
        }
    return {
        "hours_weekday": settings.hours_weekday,
        "hours_evening": settings.hours_evening,
        "hours_weekend": settings.hours_weekend,
        "instagram_url": settings.instagram_url,
        "tiktok_url": settings.tiktok_url,
        "site_name": settings.site_name,
        "slogan": settings.slogan
    }


@router.post("/contact")
def api_submit_contact(data: ContactCreate, db: Session = Depends(get_db)) -> dict:
    """Submit a contact form message."""
    try:
        create_contact_message(
            db,
            name=data.name,
            email=data.email,
            phone=data.phone,
            subject=data.subject,
            message=data.message
        )
        return {"success": True, "message": "Message envoye avec succes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du message")
