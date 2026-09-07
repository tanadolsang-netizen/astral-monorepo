import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from src.integrations import supabase_client as _sb
from src.integrations.supabase_client import get_current_user
from src.integrations.stripe_client import create_checkout_session, StripeCheckoutRequest

router = APIRouter()


class SignupIn(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


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
async def me(authorization: Optional[str] = None):
    if not authorization or not authorization.startswith("Bearer "):
        return TokenOut(access_token="", user=None, plan="free")
    try:
        user = await get_current_user(authorization)
    except (ValueError, RuntimeError):
        return TokenOut(access_token="", user=None, plan="free")
    return TokenOut(access_token=authorization.split(" ", 1)[1], user={"email": user.email}, plan="free")
