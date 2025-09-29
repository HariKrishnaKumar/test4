from dotenv import load_dotenv
import base64
import jwt
import time
import uuid
import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.merchant_detail import MerchantDetail
router = APIRouter()

CLOVER_ACCESS_TOKEN = os.getenv("CLOVER_ACCESS_TOKEN")
CLOVER_MERCHANT_ID = os.getenv("CLOVER_MERCHANT_ID")
CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL")
DOORDASH_URL = os.getenv("DOORDASH_URL")
DOORDASH_DEVELOPER_ID = os.getenv("DOORDASH_DEVELOPER_ID")
DOORDASH_KEY_ID = os.getenv("DOORDASH_KEY_ID")
DOORDASH_SIGNING_SECRET = os.getenv("DOORDASH_SIGNING_SECRET")

def generate_doordash_jwt():
    """Generate a short-lived JWT for DoorDash API"""
    now = int(time.time())
    payload = {
        "aud": "doordash",
        "iss": DOORDASH_DEVELOPER_ID,
        "kid": DOORDASH_KEY_ID,
        "iat": now,
        "exp": now + 180,
        "jti": str(uuid.uuid4())
    }
    secret_bytes = base64.urlsafe_b64decode(DOORDASH_SIGNING_SECRET + '==')  # pad with == if needed
    token = jwt.encode(
        payload,
        secret_bytes,
        algorithm="HS256",
        headers={"dd-ver": "DD-JWT-V1"}
    )
    return token

@router.post("/create")
async def create_order(order_data: dict, db: Session = Depends(get_db)):
    """Create a Clover order, and trigger DoorDash delivery if order_type is delivery."""
    merchant_id = order_data.get("merchant_id")
    if not merchant_id:
        raise HTTPException(status_code=400, detail="merchant_id is required")
    merchant = db.query(MerchantDetail).filter_by(clover_merchant_id=merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    if not CLOVER_ACCESS_TOKEN or not CLOVER_BASE_URL:
        raise HTTPException(status_code=500, detail="Clover credentials not configured")
    url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant.clover_merchant_id}/orders"
    headers = {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            clover_resp = await client.post(url, headers=headers, json=order_data)
            clover_resp.raise_for_status()
            clover_order = clover_resp.json()
            result = {"clover_order": clover_order}
            if order_data.get("order_type") == "delivery":
                dd_token = generate_doordash_jwt()
                if not dd_token or dd_token.strip() == "":
                    raise HTTPException(status_code=500, detail="Generated DoorDash JWT is empty")
                dd_headers = {
                    "Authorization": f"Bearer {dd_token}",
                    "Content-Type": "application/json"
                }
                merchant = db.query(MerchantDetail).filter(MerchantDetail.id == merchant_id).first()
                pickup_full_address = f"{merchant.address}, {merchant.city}, {merchant.state}"
                pickup_mobile = "+12065551212"
                pickup_business_name = f"{merchant.name}"
                dd_payload = {
                    "external_delivery_id": f"d-{uuid.uuid4()}",
                    "pickup_address": pickup_full_address,
                    "pickup_business_name": pickup_business_name,
                    "pickup_phone_number": pickup_mobile,
                    # "pickup_instructions": "Knock on the front door",
                    "pickup_reference_tag": f"{clover_order.get('id')}",
                    "dropoff_address": order_data.get("location"),
                    "dropoff_business_name": order_data.get("receiver_name"),
                    "dropoff_phone_number": order_data.get("receiver_mobile"),
                    "dropoff_instructions": "Call on arrival",
                    "dropoff_contact_given_name": order_data.get("receiver_name").split(" ")[0] if order_data.get("receiver_name") else "",
                    "dropoff_contact_family_name": order_data.get("receiver_name").split(" ")[-1] if order_data.get("receiver_name") else "",
                    "dropoff_contact_send_notifications": True,
                    "scheduling_model": "asap",
                    "order_value": order_data.get("amount"),
                    "currency": "USD",
                    "contactless_dropoff": False,
                    "action_if_undeliverable": "return_to_pickup"
                }
                dd_resp = await client.post(DOORDASH_URL, headers=dd_headers, json=dd_payload)
                dd_resp.raise_for_status()
                result["doordash_delivery"] = dd_resp.json()
            return {"success": True, "data": result}
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"API error: {e.response.text}"
            )
        except Exception as e:
            import traceback
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)} | Traceback: {traceback.format_exc()}"
            )
