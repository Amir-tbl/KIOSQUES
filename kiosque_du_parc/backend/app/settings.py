"""
Configuration settings for KIOSQUE DU PARC backend.
Uses environment variables with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/kiosque.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production-kiosque-du-parc-2024")
ADMIN_SESSION_EXPIRE_MINUTES = int(os.getenv("ADMIN_SESSION_EXPIRE_MINUTES", "480"))  # 8 hours

# Initial admin credentials (used only for first setup)
INIT_ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin")
INIT_ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "admin123")  # Change immediately after first login!

# Frontend path (relative to backend directory)
FRONTEND_DIR = BASE_DIR.parent  # Parent directory contains index.html and assets/

# Debug mode
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
