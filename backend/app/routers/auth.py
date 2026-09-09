"""Local authentication for FinPulse development and self-hosted deployments."""
import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()
PBKDF2_ITERATIONS = 600_000


class SignUpRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SignInRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


def _hash_password(password: str, salt: bytes) -> str:
    return base64.b64encode(hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)).decode()


def _issue_token(user_id: str, email: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(hours=settings.LOCAL_AUTH_TOKEN_HOURS)
    return jwt.encode({"sub": user_id, "email": email, "exp": expiry}, settings.LOCAL_AUTH_SECRET, algorithm="HS256")


@router.post("/sign-up")
async def sign_up(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
    user_id = secrets.token_urlsafe(24)
    salt = secrets.token_bytes(16)
    try:
        await db.execute(text("""
            INSERT INTO app_users (user_id, name, email, password_salt, password_hash)
            VALUES (:user_id, :name, :email, :password_salt, :password_hash)
        """), {"user_id": user_id, "name": request.name, "email": request.email.lower(),
              "password_salt": base64.b64encode(salt).decode(), "password_hash": _hash_password(request.password, salt)})

        try:
            await db.execute(text("""
                INSERT INTO neon_auth.users_sync (id, name, email)
                VALUES (:user_id, :name, :email)
                ON CONFLICT (id) DO NOTHING
            """), {"user_id": user_id, "name": request.name, "email": request.email.lower()})
        except Exception:
            pass

        await db.commit()
    except Exception as exc:
        await db.rollback()
        if "unique" in str(exc).lower():
            raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists.")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Could not create account: {type(exc).__name__}")
    return {"token": _issue_token(user_id, request.email.lower()), "user": {"id": user_id, "name": request.name, "email": request.email.lower()}}


@router.post("/sign-in")
async def sign_in(request: SignInRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""SELECT user_id, name, email, password_salt, password_hash
        FROM app_users WHERE email = :email"""), {"email": request.email.lower()})
    user = result.mappings().one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")
    salt = base64.b64decode(user["password_salt"])
    candidate = _hash_password(request.password, salt)
    if not hmac.compare_digest(candidate, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")
    return {"token": _issue_token(user["user_id"], user["email"]), "user": {"id": user["user_id"], "name": user["name"], "email": user["email"]}}
