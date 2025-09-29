
from fastapi import FastAPI, Query, HTTPException, Path, Header, Depends
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
from openai import OpenAI
from routers import users, pizzas, ai, auth
from app.routes.clover_auth import router as clover_router
from app.routes.userCart import router as userCart
from app.routes.orderProcess import router as orderProcess
from app.routes.clover_data import router as clover_data_router, merchant_router as clover_merchant_router
from app.routes.cart import router as cart_router
from app.routes.clover_cart import router as clover_cart_router
from app.routes.merchant_routes import router as merchant_routes
from app.routes.merchant_categories import router as merchant_categories
import os
from urllib.parse import urlencode
import secrets
from typing import Optional,Dict, Any
from datetime import datetime
import httpx
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from helpers.merchant_helper import MerchantHelper
from models.merchant_token import MerchantToken
from fastapi.middleware.cors import CORSMiddleware
from app.routes import question_master
from routers.router import api_router
from fastapi.exceptions import RequestValidationError
from middleware.response_middleware import ResponseFormatMiddleware
from utils.response_formatter import success_response, error_response
from utils.exception_handlers import (
    http_exception_handler,
    starlette_http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)




from utils.merchant_extractor import (
    extract_merchant_details,
    get_merchant_summary,
    validate_merchant_response,
    extract_inventory_items,
    extract_orders
)


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add response formatting middleware
app.add_middleware(ResponseFormatMiddleware)

# Add exception handlers for consistent error responses
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
# Load environment variables
load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Make sure you have this in your .env file
# Get Clover configuration from environment variables
CLOVER_ACCESS_TOKEN = os.getenv("CLOVER_ACCESS_TOKEN")  # The token your colleague has
CLOVER_MERCHANT_ID = os.getenv("CLOVER_MERCHANT_ID")    # The merchant ID your colleague has
CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL", "https://apisandbox.dev.clover.com")

# Store merchant tokens (in production, use database)
merchant_tokens: Dict[str, str] = {}

class MerchantToken(BaseModel):
    merchant_id: str
    access_token: str

app = FastAPI(title="Pizza API", version="1.0.0")

# Include routers (this connects all your route files)
# app.include_router(pizzas.router, prefix="/api", tags=["pizzas"])
# app.include_router(users.router, prefix="/api", tags=["users"])
# app.include_router(ai.router, prefix="/auth", tags=["ai"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(clover_router)
app.include_router(clover_data_router)
app.include_router(clover_merchant_router)
app.include_router(cart_router)
app.include_router(clover_cart_router)
app.include_router(question_master.router)
app.include_router(merchant_routes)
app.include_router(merchant_categories)
app.include_router(api_router)



@app.get("/")
def read_root():
    return success_response(
        message="Welcome to FAST API!",
        data={"message": "Welcome to FAST API!"}
    )

@app.get("/merchant")
async def get_merchant_details():
    """Get merchant details - Mobile app calls this"""

    if not CLOVER_ACCESS_TOKEN or not CLOVER_MERCHANT_ID:
        raise HTTPException(
            status_code=500,
            detail="Clover credentials not configured. Check .env file."
        )

    # Call Clover API
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}"
    headers = {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return success_response(
                message="Merchant details retrieved successfully",
                data=response.json()
            )

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Clover API error: {e.response.text}"
            )

# @app.get("/merchant/properties")
async def get_merchant_properties():
    """Get merchant properties"""

    if not CLOVER_ACCESS_TOKEN or not CLOVER_MERCHANT_ID:
        raise HTTPException(status_code=500, detail="Clover credentials not configured")

    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/properties"
    headers = {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return success_response(
                message="Merchant properties retrieved successfully",
                data=response.json()
            )

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Clover API error: {e.response.text}"
            )


async def store_merchant_in_db(
    db: Session,
    clover_merchant_id: str,
    merchant_data: Dict[str, Any],
    access_token: str
):
    """Store merchant data in database tables"""

    # 1. Store in merchants table
    merchant_query = db.execute(
        "SELECT id FROM merchants WHERE clover_merchant_id = %s",
        (clover_merchant_id,)
    )
    merchant_record = merchant_query.fetchone()

    if not merchant_record:
        # Insert new merchant
        db.execute(
            """INSERT INTO merchants (clover_merchant_id, name, email, created_at)
        VALUES (%s, %s, %s, %s)""",
            (
                clover_merchant_id,
                merchant_data.get("name"),
                merchant_data.get("email"),
                datetime.now()
            )
        )
        db.commit()

        # Get the inserted merchant ID
        merchant_id_result = db.execute(
            "SELECT id FROM merchants WHERE clover_merchant_id = %s",
            (clover_merchant_id,)
        )
        merchant_id = merchant_id_result.fetchone()[0]
    else:
        merchant_id = merchant_record[0]

        # Update existing merchant
        db.execute(
            """UPDATE merchants
        SET name = %s, email = %s
        WHERE clover_merchant_id = %s""",
            (
                merchant_data.get("name"),
                merchant_data.get("email"),
                clover_merchant_id
            )
        )

    # 2. Store/Update access token in merchant_tokens table
    token_query = db.execute(
        "SELECT id FROM merchant_tokens WHERE merchant_id = %s",
        (merchant_id,)
    )
    token_record = token_query.fetchone()

    if not token_record:
        # Insert new token
        db.execute(
            """INSERT INTO merchant_tokens (merchant_id, token, token_type, created_at)VALUES (%s, %s, %s, %s)""",
            (merchant_id, access_token, "bearer", datetime.now())
        )
    else:
        # Update existing token
        db.execute(
            """UPDATE merchant_tokens
        SET token = %s, token_type = %s
        WHERE merchant_id = %s""",
            (access_token, "bearer", merchant_id)
        )

    # 3. Store detailed merchant info in merchant_detail table
    detail_exists = db.execute(
        "SELECT id FROM merchant_detail WHERE clover_merchant_id = %s",
        (clover_merchant_id,)
    )

    if not detail_exists.fetchone():
        # Insert new merchant details
        db.execute(
            """INSERT INTO merchant_detail (
                clover_merchant_id, name, currency, timezone, email,
                address, city, state, country, postal_code, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                clover_merchant_id,
                merchant_data.get("name"),
                merchant_data.get("currency"),
                merchant_data.get("timezone"),
                merchant_data.get("email"),
                merchant_data.get("address", {}).get("address1"),
                merchant_data.get("address", {}).get("city"),
                merchant_data.get("address", {}).get("state"),
                merchant_data.get("address", {}).get("country"),
                merchant_data.get("address", {}).get("zip"),
                datetime.now()
            )
        )
    else:
        # Update existing merchant details
        db.execute(
            """UPDATE merchant_detail SET
                name = %s, currency = %s, timezone = %s, email = %s,
                address = %s, city = %s, state = %s, country = %s,
                postal_code = %s, updated_at = %s
        WHERE clover_merchant_id = %s""",
            (
                merchant_data.get("name"),
                merchant_data.get("currency"),
                merchant_data.get("timezone"),
                merchant_data.get("email"),
                merchant_data.get("address", {}).get("address1"),
                merchant_data.get("address", {}).get("city"),
                merchant_data.get("address", {}).get("state"),
                merchant_data.get("address", {}).get("country"),
                merchant_data.get("address", {}).get("zip"),
                datetime.now(),
                clover_merchant_id
            )
        )

    db.commit()
    return merchant_id


# @app.post("/merchants/add")
# async def add_merchant_token(merchant: MerchantToken):
#     """Add a merchant and their access token"""

#     # Store the token for this merchant
#     merchant_tokens[merchant.merchant_id] = merchant.access_token

#     # Test if the token works
#     url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant.merchant_id}"
#     headers = {
#         "Authorization": f"Bearer {merchant.access_token}",
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             merchant_data = response.json()

#             # Validate the response
#             if not validate_merchant_response(merchant_data):
#                 raise HTTPException(status_code=400, detail="Invalid merchant data received")

#             # Extract clean merchant summary
#             summary = get_merchant_summary(merchant_data)

#             return {
#                 "success": True,
#                 "message": f"✅ Merchant {merchant.merchant_id} added successfully",
#                 "merchant_info": summary,
#                 "total_merchants": len(merchant_tokens)
#             }

#         except httpx.HTTPStatusError as e:
#             # Remove the token if it doesn't work
#             merchant_tokens.pop(merchant.merchant_id, None)
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid token for merchant {merchant.merchant_id}: {e.response.text}"
#             )


# @app.post("/merchants/add")
# async def add_merchant_token(merchant: MerchantToken, db: Session = Depends(get_db)):
#     """Add a merchant and their access token with database storage"""
#     # Test if the token works first
#     url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant.merchant_id}"
#     headers = {
#         "Authorization": f"Bearer {merchant.access_token}",
#         "Content-Type": "application/json"
#     }


#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers)
#             response.raise_for_status()
#             merchant_data = response.json()


#             # Validate the response
#             if not validate_merchant_response(merchant_data):
#                 raise HTTPException(status_code=400, detail="Invalid merchant data received")

#             # Store in database using helper
#             merchant_id = MerchantHelper.store_complete_merchant_data(
#                 db,
#                 merchant.merchant_id,
#                 merchant_data,
#                 merchant.access_token
#             )
#             print(merchant_id)

#             # Extract clean merchant summary for response
#             summary = get_merchant_summary(merchant_data)
#             print(summary)
#             # Get total merchants count
#             total_count = MerchantHelper.get_total_merchants_count(db)

#             return {
#                 "success": True,
#                 "message": f"✅ Merchant {merchant.merchant_id} added successfully",
#                 "merchant_info": summary,
#                 "database_id": merchant_id,
#                 "total_merchants": total_count
#             }

#         except httpx.HTTPStatusError as e:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid token for merchant {merchant.merchant_id}: {e.response.text}"
#             )
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Database error: {str(e)}"
#             )

@app.post("/merchants/add")
async def add_merchant_token(merchant: MerchantToken, db: Session = Depends(get_db)):
    """Add a merchant and their access token with database storage"""

    # Test if the token works first
    url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant.merchant_id}"
    headers = {
        "Authorization": f"Bearer {merchant.access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            merchant_data = response.json()

            # DEBUG: Print the merchant data structure
            # print("=== MERCHANT DATA DEBUG ===")
            # print(f"Full merchant_data type: {type(merchant_data)}")
            # print(f"Full merchant_data: {merchant_data}")

            # Check each field and its type
            for key, value in merchant_data.items():
                print(f"Field '{key}': Type={type(value).__name__}, Value={repr(value)}")
                if isinstance(value, dict):
                    print(f"  -> DICT DETECTED in field '{key}': {value}")
                elif isinstance(value, list):
                    print(f"  -> LIST DETECTED in field '{key}': {value}")

            # Validate the response
            if not validate_merchant_response(merchant_data):
                raise HTTPException(status_code=400, detail="Invalid merchant data received")


            # Store in database using helper (this is where the error occurs)
            merchant_id = await MerchantHelper.store_complete_merchant_data(
                db,
                merchant.merchant_id,
                merchant_data,
                merchant.access_token
            )

            # Extract clean merchant summary for response
            summary = get_merchant_summary(merchant_data)

            # Get total merchants count
            total_count = MerchantHelper.get_total_merchants_count(db)

            return success_response(
                message=f"✅ Merchant {merchant.merchant_id} added successfully",
                data={
                    "merchant_info": summary,
                    "database_id": merchant_id,
                    "total_merchants": total_count
                }
            )

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid token for merchant {merchant.merchant_id}: {e.response.text}"
            )
        except Exception as e:
            print(f"Full error details: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )


# @app.get("/inventory/items")
# async def get_inventory_items(limit: Optional[int] = 100):
#     """Get inventory items"""

#     if not CLOVER_ACCESS_TOKEN or not CLOVER_MERCHANT_ID:
#         raise HTTPException(status_code=500, detail="Clover credentials not configured")

#     url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/items"
#     params = {"limit": limit}
#     headers = {
#         "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, headers=headers, params=params)
#             response.raise_for_status()

#             return {
#                 "success": True,
#                 "data": response.json()
#             }

#         except httpx.HTTPStatusError as e:
#             raise HTTPException(
#                 status_code=e.response.status_code,
#                 detail=f"Clover API error: {e.response.text}"
#             )


@app.get("/merchants/{clover_merchant_id}/token")
async def get_merchant_token(clover_merchant_id: str, db: Session = Depends(get_db)):
    """Get merchant access token"""
    token = MerchantHelper.get_merchant_token(db, clover_merchant_id)
    if not token:
        raise HTTPException(status_code=404, detail="Merchant token not found")

    return {"merchant_id": clover_merchant_id, "has_token": True}


# def get_merchant_token(merchant_id: str) -> str:
#     """Helper function to get token for a merchant"""
#     if merchant_id not in merchant_tokens:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Merchant {merchant_id} not found. Please add merchant token first using POST /merchants/add"
#         )
#     return merchant_tokens[merchant_id]

@app.get("/merchants/{merchant_id}")
async def get_merchant_details_endpoint(merchant_id: str = Path(..., description="Merchant ID")):
    """Get merchant details for specific merchant"""

    access_token = await get_merchant_token(merchant_id)

    url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            raw_data = response.json()

            # Extract only relevant merchant details using our utility function
            cleaned_data = extract_merchant_details(raw_data)

            return {
                "success": True,
                "merchant_id": merchant_id,
                "merchant_details": cleaned_data
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Clover API error for merchant {merchant_id}: {e.response.text}"
            )

@app.get("/merchants/{merchant_id}/inventory/items")
async def get_inventory_items(
    merchant_id: str = Path(..., description="Merchant ID"),
    limit: Optional[int] = 100
):
    """Get inventory items for specific merchant"""

    access_token = get_merchant_token(merchant_id)

    url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}/items"
    params = {"limit": limit}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            raw_data = response.json()

            # Extract and clean inventory data
            cleaned_data = extract_inventory_items(raw_data)

            return {
                "success": True,
                "merchant_id": merchant_id,
                "inventory": cleaned_data
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Clover API error for merchant {merchant_id}: {e.response.text}"
            )

@app.get("/merchants/{merchant_id}/orders")
async def get_orders(
    merchant_id: str = Path(..., description="Merchant ID"),
    limit: Optional[int] = 100
):
    """Get orders for specific merchant"""

    access_token = get_merchant_token(merchant_id)

    url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}/orders"
    params = {"limit": limit}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            raw_data = response.json()

            # Extract and clean orders data
            cleaned_data = extract_orders(raw_data)

            return {
                "success": True,
                "merchant_id": merchant_id,
                "orders": cleaned_data
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Clover API error for merchant {merchant_id}: {e.response.text}"
            )

@app.delete("/merchants/{merchant_id}")
async def remove_merchant(merchant_id: str = Path(..., description="Merchant ID")):
    """Remove merchant and their token"""

    if merchant_id not in merchant_tokens:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_id} not found")

    del merchant_tokens[merchant_id]

    return {
        "success": True,
        "message": f"Merchant {merchant_id} removed successfully",
        "remaining_merchants": len(merchant_tokens)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/orders")
async def get_orders(limit: Optional[int] = 100):
    """Get orders"""

    if not CLOVER_ACCESS_TOKEN or not CLOVER_MERCHANT_ID:
        raise HTTPException(status_code=500, detail="Clover credentials not configured")

    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/orders"
    params = {"limit": limit}
    headers = {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            return {
                "success": True,
                "data": response.json()
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Clover API error: {e.response.text}"
            )


@app.get("/test-connection")
async def test_clover_connection():
    """Test if Clover connection is working"""

    if not CLOVER_ACCESS_TOKEN or not CLOVER_MERCHANT_ID:
        return {
            "success": False,
            "message": "❌ Clover credentials not configured",
            "missing": {
                "token": "Set CLOVER_ACCESS_TOKEN in .env",
                "merchant_id": "Set CLOVER_MERCHANT_ID in .env"
            }
        }

    # Test connection
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}"
    headers = {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return {
                "success": True,
                "message": "✅ Clover connection working!",
                "merchant_id": CLOVER_MERCHANT_ID,
                "token_status": "Valid"
            }

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "message": "❌ Clover connection failed",
                "error": e.response.text,
                "status_code": e.response.status_code
            }

# @app.get("/health", tags=["Root"])
# async def health_check():
#     return {
#         "status": "OK",
#         "timestamp": datetime.now().isoformat(),
#         "version": "1.0.0"
#     }

# @app.get("/", tags=["Root"])
# async def root():
#     return {
#         "message": "Multilingual Food Recommendation API",
#         "version": "1.0.0",
#         "docs_url": "/docs",
#         "endpoints": {
#             "Food Routes": {
#                 "POST /api/food/conversation": "Natural language food requests",
#                 "POST /api/food/preferences": "Structured preference input",
#                 "GET /api/food/options": "Get available options"
#             },
#             "OpenAI Routes": {
#                 "POST /api/openai/detect-language": "Detect text language",
#                 "POST /api/openai/translate": "Translate text",
#                 "POST /api/openai/chat": "General chat completion"
#             },
#             "Gemini Routes": {
#                 "POST /api/gemini/extract-preferences": "Extract food preferences",
#                 "POST /api/gemini/recommend": "Generate recommendations",
#                 "POST /api/gemini/generate": "General content generation"
#             }
#         }
#     }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
