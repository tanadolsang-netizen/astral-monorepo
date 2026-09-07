from fastapi import APIRouter, Depends, HTTPException
from src.integrations.stripe_client import create_checkout_session, StripeCheckoutRequest
from src.integrations.supabase_client import get_current_user

router = APIRouter()


@router.post("/checkout")
async def checkout(req: StripeCheckoutRequest, authorization: str = ""):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        try:
            user = await get_current_user(authorization)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(status_code=401, detail="Unauthorized") from exc
        session = await create_checkout_session(
            StripeCheckoutRequest(
                price_id=req.price_id,
                success_url=req.success_url,
                cancel_url=req.cancel_url,
                customer_email=user.email,
            )
        )
        return session
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
