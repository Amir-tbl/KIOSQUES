"""
Authentication utilities for admin users.
Uses cookie-based sessions with signed tokens.
"""
import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.settings import SECRET_KEY, ADMIN_SESSION_EXPIRE_MINUTES
from app.db import get_db
from app.models import Admin

# Session serializer
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Session cookie name
SESSION_COOKIE_NAME = "kdp_admin_session"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_session_token(admin_id: int, username: str) -> str:
    """Create a signed session token."""
    data = {"admin_id": admin_id, "username": username}
    return serializer.dumps(data)


def verify_session_token(token: str) -> dict | None:
    """
    Verify and decode a session token.
    Returns the session data or None if invalid/expired.
    """
    try:
        max_age = ADMIN_SESSION_EXPIRE_MINUTES * 60
        data = serializer.loads(token, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None


def authenticate_admin(db: Session, username: str, password: str) -> Admin | None:
    """
    Authenticate an admin user.
    Returns the Admin object if credentials are valid, None otherwise.
    """
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        return None
    if not admin.is_active:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin


def get_current_admin(request: Request) -> dict | None:
    """
    Get the current admin from session cookie.
    Returns session data or None if not authenticated.
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    return verify_session_token(token)


def require_admin(request: Request):
    """
    Dependency that requires admin authentication.
    Raises HTTPException or redirects to login if not authenticated.
    """
    admin_data = get_current_admin(request)
    if not admin_data:
        # For HTML pages, redirect to login
        raise HTTPException(
            status_code=303,
            headers={"Location": "/admin/login"}
        )
    return admin_data


def set_session_cookie(response: RedirectResponse, admin: Admin) -> RedirectResponse:
    """Set the session cookie on a response."""
    token = create_session_token(admin.id, admin.username)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=ADMIN_SESSION_EXPIRE_MINUTES * 60
    )
    return response


def clear_session_cookie(response: RedirectResponse) -> RedirectResponse:
    """Clear the session cookie."""
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return response
