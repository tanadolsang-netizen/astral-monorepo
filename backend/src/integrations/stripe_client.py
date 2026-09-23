import os
from typing import Optional

import stripe
from fastapi import HTTPException
from pydantic import BaseModel

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def init_stripe() -> None:
    if not stripe.api_key:
        raise RuntimeError("STRIPE_SECRET_KEY missing")


class StripeCheckoutRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str
    customer_email: str


class StripeCheckoutResponse(BaseModel):
    url: str


async def create_checkout_session(req: StripeCheckoutRequest) -> StripeCheckoutResponse:
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": req.price_id, "quantity": 1}],
            customer_email=req.customer_email,
            success_url=req.success_url,
            cancel_url=req.cancel_url,
        )
        return StripeCheckoutResponse(url=session.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
