from fastapi import FastAPI, Request
import os, hmac, hashlib
import httpx

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID", "")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID", "")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET", "")
ZOOM_WEBHOOK_SECRET = os.getenv("ZOOM_WEBHOOK_SECRET", "")

async def get_zoom_access_token():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://zoom.us/oauth/token",
            params={"grant_type": "account_credentials", "account_id": ZOOM_ACCOUNT_ID},
            auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET),
            timeout=20
        )
        r.raise_for_status()
        return r.json()["access_token"]

@app.get("/")
async def root():
    return {"ok": True}

@app.post("/zoom/webhook")
async def zoom_webhook(req: Request):
    body = await req.json()
    # Валидация URL (challenge)
    if body.get("event") == "endpoint.url_validation":
        plain = body["payload"]["plainToken"]
        sig = hmac.new(ZOOM_WEBHOOK_SECRET.encode(), plain.encode(), hashlib.sha256).hexdigest()
        return {"plainToken": plain, "encryptedToken": sig}
    return {"ok": True}

@app.post("/tg/webhook")
async def tg_webhook(req: Request):
    update = await req.json()
    return {"ok": True}
