"""
Database seeding with initial data.
"""
from sqlalchemy.orm import Session
from app.models import Product, Schedule, Location, Settings
from app.crud import (
    get_product_count, create_product,
    get_schedules, create_schedule,
    ensure_settings_exist, ensure_location_exists,
    get_admin_count, create_admin
)
from app.settings import INIT_ADMIN_USERNAME, INIT_ADMIN_PASSWORD


# Initial products data
INITIAL_PRODUCTS = [
    {
        "name": "Crepe au miel",
        "category": "crepes_sucrees",
        "price": 3.50,
        "image_filename": "Crêpe_miel.jpeg",
        "description": "Crepe nappee de miel dore",
        "is_active": True,
        "is_best_seller": True,
        "display_order": 1
    },
    {
        "name": "Crepe caramel",
        "category": "crepes_sucrees",
        "price": 3.50,
        "image_filename": "Crêpe_caramel.jpeg",
        "description": "Crepe au caramel onctueux",
        "is_active": True,
        "is_best_seller": True,
        "display_order": 2
    },
    {
        "name": "Crepe chocolat + banane",
        "category": "crepes_sucrees",
        "price": 4.90,
        "image_filename": "Crêpe_chocolat_banane.jpeg",
        "description": "Crepe chocolat avec banane fraiche",
        "is_active": True,
        "is_best_seller": True,
        "display_order": 3
    },
    {
        "name": "Crepe chocolat + coco rapee",
        "category": "crepes_sucrees",
        "price": 4.90,
        "image_filename": "Crêpe_chocolat_coco_râpée.jpeg",
        "description": "Crepe chocolat avec coco rapee",
        "is_active": True,
        "is_best_seller": False,
        "display_order": 4
    },
    {
        "name": "Crepe chocolat",
        "category": "crepes_sucrees",
        "price": 3.90,
        "image_filename": "Crêpe_chocolat.jpeg",
        "description": "Crepe au chocolat fondant",
        "is_active": True,
        "is_best_seller": False,
        "display_order": 5
    },
    {
        "name": "Crepe salee jambon-fromage",
        "category": "crepes_salees",
        "price": 5.50,
        "image_filename": "crêpe salée_jambon-fromage.jpeg",
        "description": "Crepe salee jambon et fromage fondu",
        "is_active": True,
        "is_best_seller": False,
        "display_order": 6
    },
    {
        "name": "Crepe salee poulet pane + fromage",
        "category": "crepes_salees",
        "price": 6.50,
        "image_filename": "crêpe_salée_pouletpané_fromage.jpeg",
        "description": "Crepe salee poulet pane croustillant avec fromage",
        "is_active": True,
        "is_best_seller": True,
        "display_order": 7
    },
    {
        "name": "Gaufre chocolat + eclats",
        "category": "gaufres",
        "price": 4.50,
        "image_filename": "Gaufre_chocolat_éclats.jpeg",
        "description": "Gaufre chocolat avec eclats croustillants",
        "is_active": True,
        "is_best_seller": True,
        "display_order": 8
    },
    {
        "name": "Gaufre nature + sucre glace",
        "category": "gaufres",
        "price": 3.50,
        "image_filename": "Gaufre nature_sucre_glace.jpeg",
        "description": "Gaufre nature saupoudree de sucre glace",
        "is_active": True,
        "is_best_seller": False,
        "display_order": 9
    },
    {
        "name": "Riz Crousty",
        "category": "box",
        "price": 7.90,
        "image_filename": "Riz_Crousty.jpeg",
        "description": "Box Riz Crousty genereux",
        "is_active": True,
        "is_best_seller": True,
        "display_order": 10
    }
]


# Initial schedule data
INITIAL_SCHEDULE = [
    {"day_of_week": 0, "place": "Marche du Centre", "start_time": "10:00", "end_time": "14:00"},
    {"day_of_week": 1, "place": "Place de la Gare", "start_time": "11:30", "end_time": "14:00"},
    {"day_of_week": 1, "place": "Place de la Gare", "start_time": "18:00", "end_time": "20:30"},
    {"day_of_week": 2, "place": "Parc des Expositions", "start_time": "11:00", "end_time": "15:00"},
    {"day_of_week": 3, "place": "Campus Universitaire", "start_time": "11:30", "end_time": "14:30"},
    {"day_of_week": 4, "place": "Zone Commerciale Nord", "start_time": "11:30", "end_time": "14:00"},
    {"day_of_week": 4, "place": "Zone Commerciale Nord", "start_time": "18:00", "end_time": "21:00"},
    {"day_of_week": 5, "place": "Marche couvert", "start_time": "09:00", "end_time": "15:00"},
    {"day_of_week": 6, "place": "Parc de la Mairie", "start_time": "10:00", "end_time": "14:00"},
]


def seed_database(db: Session):
    """
    Seed database with initial data if empty.
    Called at application startup.
    """
    # Seed products if none exist
    if get_product_count(db) == 0:
        print("[SEED] Creating initial products...")
        for product_data in INITIAL_PRODUCTS:
            create_product(db, **product_data)
        print(f"[SEED] Created {len(INITIAL_PRODUCTS)} products")

    # Seed schedule if none exist
    if len(get_schedules(db)) == 0:
        print("[SEED] Creating initial schedule...")
        for schedule_data in INITIAL_SCHEDULE:
            create_schedule(db, **schedule_data)
        print(f"[SEED] Created {len(INITIAL_SCHEDULE)} schedule entries")

    # Ensure settings exist
    ensure_settings_exist(db)
    print("[SEED] Settings initialized")

    # Ensure location exists
    ensure_location_exists(db)
    print("[SEED] Location initialized")

    # Create default admin if none exist
    if get_admin_count(db) == 0:
        print("[SEED] Creating default admin user...")
        create_admin(db, INIT_ADMIN_USERNAME, INIT_ADMIN_PASSWORD)
        print(f"[SEED] Admin '{INIT_ADMIN_USERNAME}' created (password: {INIT_ADMIN_PASSWORD})")
        print("[SEED] WARNING: Change the default password immediately!")
