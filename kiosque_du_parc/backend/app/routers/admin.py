"""
Admin routes for the dashboard.
All routes are protected and require authentication.
"""
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.db import get_db
from app.auth import (
    get_current_admin, authenticate_admin,
    set_session_cookie, clear_session_cookie
)
from app.crud import (
    get_products, get_product, create_product, update_product, delete_product,
    get_product_count, get_bestseller_count,
    get_schedules, get_schedule, create_schedule, update_schedule, delete_schedule,
    get_location, update_location,
    get_settings, update_settings,
    get_contact_messages, get_contact_message, mark_message_as_read,
    delete_contact_message, get_unread_message_count, get_message_count
)
from app.models import DAY_NAMES, CATEGORY_NAMES
from app.settings import BASE_DIR

router = APIRouter(prefix="/admin", tags=["Admin"])

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def admin_required(request: Request, db: Session = Depends(get_db)):
    """Dependency that requires admin authentication."""
    admin_data = get_current_admin(request)
    if not admin_data:
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return admin_data


# ============== Auth Routes ==============

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Login page."""
    # If already logged in, redirect to dashboard
    if get_current_admin(request):
        return RedirectResponse(url="/admin", status_code=303)

    return templates.TemplateResponse("admin/login.html", {
        "request": request,
        "error": None
    })


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form."""
    admin = authenticate_admin(db, username, password)

    if not admin:
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Identifiants invalides"
        })

    response = RedirectResponse(url="/admin", status_code=303)
    return set_session_cookie(response, admin)


@router.get("/logout")
def logout(request: Request):
    """Logout and clear session."""
    response = RedirectResponse(url="/admin/login", status_code=303)
    return clear_session_cookie(response)


# ============== Dashboard ==============

@router.get("", response_class=HTMLResponse)
def dashboard(
    request: Request,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Admin dashboard."""
    # Get stats
    total_products = get_product_count(db)
    active_products = get_product_count(db, active_only=True)
    bestsellers = get_bestseller_count(db)
    schedules = get_schedules(db, active_only=True)
    location = get_location(db)
    unread_messages = get_unread_message_count(db)
    total_messages = get_message_count(db)

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "admin": admin,
        "stats": {
            "total_products": total_products,
            "active_products": active_products,
            "bestsellers": bestsellers,
            "schedules_count": len(schedules),
            "unread_messages": unread_messages,
            "total_messages": total_messages
        },
        "location": location
    })


# ============== Products ==============

@router.get("/products", response_class=HTMLResponse)
def products_list(
    request: Request,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """List all products."""
    products = get_products(db)
    return templates.TemplateResponse("admin/products_list.html", {
        "request": request,
        "admin": admin,
        "products": products,
        "categories": CATEGORY_NAMES
    })


@router.get("/products/new", response_class=HTMLResponse)
def product_new(
    request: Request,
    admin: dict = Depends(admin_required)
):
    """New product form."""
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "admin": admin,
        "product": None,
        "categories": CATEGORY_NAMES,
        "error": None
    })


@router.post("/products/new", response_class=HTMLResponse)
def product_create(
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    image_filename: str = Form(""),
    description: str = Form(""),
    is_active: bool = Form(False),
    is_best_seller: bool = Form(False),
    display_order: int = Form(0),
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Create a new product."""
    try:
        create_product(
            db,
            name=name,
            category=category,
            price=price,
            image_filename=image_filename or None,
            description=description or None,
            is_active=is_active,
            is_best_seller=is_best_seller,
            display_order=display_order
        )
        return RedirectResponse(url="/admin/products", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("admin/product_form.html", {
            "request": request,
            "admin": admin,
            "product": None,
            "categories": CATEGORY_NAMES,
            "error": str(e)
        })


@router.get("/products/{product_id}/edit", response_class=HTMLResponse)
def product_edit(
    request: Request,
    product_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Edit product form."""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "admin": admin,
        "product": product,
        "categories": CATEGORY_NAMES,
        "error": None
    })


@router.post("/products/{product_id}/edit", response_class=HTMLResponse)
def product_update(
    request: Request,
    product_id: int,
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    image_filename: str = Form(""),
    description: str = Form(""),
    is_active: bool = Form(False),
    is_best_seller: bool = Form(False),
    display_order: int = Form(0),
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Update a product."""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        update_product(
            db,
            product_id,
            name=name,
            category=category,
            price=price,
            image_filename=image_filename or None,
            description=description or None,
            is_active=is_active,
            is_best_seller=is_best_seller,
            display_order=display_order
        )
        return RedirectResponse(url="/admin/products", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("admin/product_form.html", {
            "request": request,
            "admin": admin,
            "product": product,
            "categories": CATEGORY_NAMES,
            "error": str(e)
        })


@router.get("/products/{product_id}/delete", response_class=HTMLResponse)
def product_delete_confirm(
    request: Request,
    product_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete confirmation page."""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return templates.TemplateResponse("admin/product_delete.html", {
        "request": request,
        "admin": admin,
        "product": product
    })


@router.post("/products/{product_id}/delete")
def product_delete_action(
    product_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete a product."""
    if not delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return RedirectResponse(url="/admin/products", status_code=303)


# ============== Location ==============

@router.get("/location", response_class=HTMLResponse)
def location_edit(
    request: Request,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Edit location form."""
    location = get_location(db)
    return templates.TemplateResponse("admin/location_form.html", {
        "request": request,
        "admin": admin,
        "location": location,
        "success": False
    })


@router.post("/location", response_class=HTMLResponse)
def location_update(
    request: Request,
    today_location: str = Form(""),
    today_hours: str = Form(""),
    daily_message: str = Form(""),
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Update location."""
    update_location(
        db,
        today_location=today_location or None,
        today_hours=today_hours or None,
        daily_message=daily_message or None
    )
    location = get_location(db)
    return templates.TemplateResponse("admin/location_form.html", {
        "request": request,
        "admin": admin,
        "location": location,
        "success": True
    })


# ============== Schedule ==============

@router.get("/schedule", response_class=HTMLResponse)
def schedule_list(
    request: Request,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """List schedule entries."""
    schedules = get_schedules(db)
    return templates.TemplateResponse("admin/schedule_list.html", {
        "request": request,
        "admin": admin,
        "schedules": schedules,
        "day_names": DAY_NAMES
    })


@router.get("/schedule/new", response_class=HTMLResponse)
def schedule_new(
    request: Request,
    admin: dict = Depends(admin_required)
):
    """New schedule form."""
    return templates.TemplateResponse("admin/schedule_form.html", {
        "request": request,
        "admin": admin,
        "schedule": None,
        "day_names": DAY_NAMES,
        "error": None
    })


@router.post("/schedule/new", response_class=HTMLResponse)
def schedule_create(
    request: Request,
    day_of_week: int = Form(...),
    place: str = Form(...),
    start_time: str = Form(""),
    end_time: str = Form(""),
    is_active: bool = Form(False),
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Create a schedule entry."""
    try:
        create_schedule(
            db,
            day_of_week=day_of_week,
            place=place,
            start_time=start_time if place == "Ouvert" else None,
            end_time=end_time if place == "Ouvert" else None,
            is_active=is_active
        )
        return RedirectResponse(url="/admin/schedule", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("admin/schedule_form.html", {
            "request": request,
            "admin": admin,
            "schedule": None,
            "day_names": DAY_NAMES,
            "error": str(e)
        })


@router.get("/schedule/{schedule_id}/edit", response_class=HTMLResponse)
def schedule_edit(
    request: Request,
    schedule_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Edit schedule form."""
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return templates.TemplateResponse("admin/schedule_form.html", {
        "request": request,
        "admin": admin,
        "schedule": schedule,
        "day_names": DAY_NAMES,
        "error": None
    })


@router.post("/schedule/{schedule_id}/edit", response_class=HTMLResponse)
def schedule_update_action(
    request: Request,
    schedule_id: int,
    day_of_week: int = Form(...),
    place: str = Form(...),
    start_time: str = Form(""),
    end_time: str = Form(""),
    is_active: bool = Form(False),
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Update a schedule entry."""
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    try:
        update_schedule(
            db,
            schedule_id,
            day_of_week=day_of_week,
            place=place,
            start_time=start_time if place == "Ouvert" else None,
            end_time=end_time if place == "Ouvert" else None,
            is_active=is_active
        )
        return RedirectResponse(url="/admin/schedule", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("admin/schedule_form.html", {
            "request": request,
            "admin": admin,
            "schedule": schedule,
            "day_names": DAY_NAMES,
            "error": str(e)
        })


@router.get("/schedule/{schedule_id}/delete", response_class=HTMLResponse)
def schedule_delete_confirm(
    request: Request,
    schedule_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete confirmation page."""
    schedule = get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return templates.TemplateResponse("admin/schedule_delete.html", {
        "request": request,
        "admin": admin,
        "schedule": schedule,
        "day_names": DAY_NAMES
    })


@router.post("/schedule/{schedule_id}/delete")
def schedule_delete_action(
    schedule_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete a schedule entry."""
    if not delete_schedule(db, schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")
    return RedirectResponse(url="/admin/schedule", status_code=303)


# ============== Settings ==============

@router.get("/settings", response_class=HTMLResponse)
def settings_edit(
    request: Request,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Edit settings form."""
    settings = get_settings(db)
    return templates.TemplateResponse("admin/settings_form.html", {
        "request": request,
        "admin": admin,
        "settings": settings,
        "success": False
    })


@router.post("/settings", response_class=HTMLResponse)
def settings_update(
    request: Request,
    hours_weekday: str = Form(""),
    hours_evening: str = Form(""),
    hours_weekend: str = Form(""),
    instagram_url: str = Form(""),
    tiktok_url: str = Form(""),
    site_name: str = Form(""),
    slogan: str = Form(""),
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Update settings."""
    update_settings(
        db,
        hours_weekday=hours_weekday or None,
        hours_evening=hours_evening or None,
        hours_weekend=hours_weekend or None,
        instagram_url=instagram_url or None,
        tiktok_url=tiktok_url or None,
        site_name=site_name or None,
        slogan=slogan or None
    )
    settings = get_settings(db)
    return templates.TemplateResponse("admin/settings_form.html", {
        "request": request,
        "admin": admin,
        "settings": settings,
        "success": True
    })


# ============== Contact Messages ==============

@router.get("/messages", response_class=HTMLResponse)
def messages_list(
    request: Request,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """List all contact messages."""
    messages = get_contact_messages(db)
    return templates.TemplateResponse("admin/messages_list.html", {
        "request": request,
        "admin": admin,
        "messages": messages
    })


@router.get("/messages/{message_id}", response_class=HTMLResponse)
def message_view(
    request: Request,
    message_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """View a single message."""
    message = get_contact_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Mark as read
    if not message.is_read:
        mark_message_as_read(db, message_id)
        message.is_read = True

    return templates.TemplateResponse("admin/message_view.html", {
        "request": request,
        "admin": admin,
        "message": message
    })


@router.get("/messages/{message_id}/delete", response_class=HTMLResponse)
def message_delete_confirm(
    request: Request,
    message_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete confirmation page."""
    message = get_contact_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return templates.TemplateResponse("admin/message_delete.html", {
        "request": request,
        "admin": admin,
        "message": message
    })


@router.post("/messages/{message_id}/delete")
def message_delete_action(
    message_id: int,
    admin: dict = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Delete a message."""
    if not delete_contact_message(db, message_id):
        raise HTTPException(status_code=404, detail="Message not found")
    return RedirectResponse(url="/admin/messages", status_code=303)
