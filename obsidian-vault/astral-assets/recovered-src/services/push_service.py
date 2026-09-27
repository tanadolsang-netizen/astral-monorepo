import os
from typing import Optional
import httpx

PUSH_SERVICE_URL = os.getenv("PUSH_SERVICE_URL", "")
PUSH_API_KEY = os.getenv("PUSH_API_KEY", "")


async def send_push(user_id: str, title: str, body: str, data: Optional[dict] = None) -> dict:
    if not PUSH_SERVICE_URL or not PUSH_API_KEY:
        return {"status": "skipped", "reason": "not configured"}
    payload = {
        "user_id": user_id,
        "notification": {"title": title, "body": body},
        "data": data or {},
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            PUSH_SERVICE_URL,
            json=payload,
            headers={"Authorization": f"Bearer {PUSH_API_KEY}"},
        )
        r.raise_for_status()
        return {"status": "sent", "code": r.status_code}
