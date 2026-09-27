import os
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from src.integrations import supabase_client as _sb
from src.integrations.supabase_client import get_current_user
from src.integrations.stripe_client import create_checkout_session, StripeCheckoutRequest

router = APIRouter()


class SignupIn(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("Password must contain both letters and numbers")
        return v


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None
    plan: Optional[str] = None


def _get_sb():
    _sb.init_supabase()
    return _sb._supabase


@router.post("/signup", response_model=TokenOut)
async def signup(body: SignupIn):
    client = _get_sb()
    res = client.auth.sign_up({"email": body.email, "password": body.password, "options": {"data": {"full_name": body.full_name}}})
    user = getattr(res, "user", None)
    session = getattr(res, "session", None)
    if not user:
        raise HTTPException(status_code=400, detail="Signup failed")
    return TokenOut(
        access_token=getattr(session, "access_token", "") or "",
        user={"email": getattr(user, "email", None)},
        plan="free",
    )


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn):
    client = _get_sb()
    res = client.auth.sign_in_with_password({"email": body.email, "password": body.password})
    user = getattr(res, "user", None)
    session = getattr(res, "session", None)
    if not user or not session:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return TokenOut(
        access_token=getattr(session, "access_token", "") or "",
        user={"email": getattr(user, "email", None)},
        plan="free",
    )


@router.get("/me", response_model=TokenOut)
async def me(user=Depends(get_current_user)):
    return TokenOut(
        access_token="",
        user={"email": user.email},
        plan="free",
    )
