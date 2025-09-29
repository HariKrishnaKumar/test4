from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from database.database import get_db
from helpers.merchant_helper import MerchantHelper
from utils.response_formatter import success_response, error_response
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/merchant-categories", tags=["Merchant Categories"])

CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL", "https://apisandbox.dev.clover.com")


def _build_headers(access_token: str):
    """Build headers for Clover API requests"""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


async def _fetch_merchant_categories(merchant_id: str, access_token: str, limit: int = 100) -> Dict[str, Any]:
    """Fetch categories for a single merchant from Clover API"""
    try:
        url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}/categories"
        params = {"limit": limit}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=_build_headers(access_token),
                params=params,
                timeout=30.0
            )

            if response.status_code >= 400:
                logger.warning(f"Failed to fetch categories for merchant {merchant_id}: {response.status_code} - {response.text}")
                return {
                    "merchant_id": merchant_id,
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "categories": []
                }

            data = response.json()
            categories = data.get("elements", [])

            return {
                "merchant_id": merchant_id,
                "success": True,
                "categories": categories,
                "total_categories": len(categories)
            }

    except httpx.TimeoutException:
        logger.error(f"Timeout fetching categories for merchant {merchant_id}")
        return {
            "merchant_id": merchant_id,
            "success": False,
            "error": "Request timeout",
            "categories": []
        }
    except Exception as e:
        logger.error(f"Error fetching categories for merchant {merchant_id}: {str(e)}")
        return {
            "merchant_id": merchant_id,
            "success": False,
            "error": str(e),
            "categories": []
        }


@router.get("/categories/all")
async def get_all_merchant_categories(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000, description="Limit categories per merchant"),
    include_failed: bool = Query(False, description="Include merchants that failed to fetch categories")
):
    """
    Retrieve categories from all merchants stored in the database

    Args:
        db: Database session
        limit: Maximum number of categories to fetch per merchant
        include_failed: Whether to include merchants that failed to fetch categories

    Returns:
        Merged categories from all merchants
    """
    try:
        # Get all merchants with their tokens
        merchants_query = db.execute(text("""
            SELECT m.clover_merchant_id, m.name, mt.token
            FROM merchants m
            JOIN merchant_tokens mt ON m.id = mt.merchant_id
            WHERE mt.token IS NOT NULL
        """))

        merchants = merchants_query.fetchall()

        if not merchants:
            return success_response(
                message="No merchants found with valid tokens",
                data={
                    "merchants": [],
                    "total_merchants": 0,
                    "total_categories": 0,
                    "categories": []
                }
            )

        # Fetch categories from all merchants concurrently
        import asyncio

        tasks = []
        for merchant in merchants:
            clover_merchant_id, name, token = merchant
            task = _fetch_merchant_categories(clover_merchant_id, token, limit)
            tasks.append(task)

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        all_categories = []
        merchant_results = []
        successful_merchants = 0
        failed_merchants = 0

        for i, result in enumerate(results):
            merchant = merchants[i]
            clover_merchant_id, name, token = merchant

            if isinstance(result, Exception):
                # Handle exceptions from asyncio.gather
                merchant_result = {
                    "merchant_id": clover_merchant_id,
                    "merchant_name": name,
                    "success": False,
                    "error": str(result),
                    "categories": []
                }
                failed_merchants += 1
            else:
                # Process successful result
                merchant_result = {
                    "merchant_id": clover_merchant_id,
                    "merchant_name": name,
                    "success": result["success"],
                    "categories": result["categories"],
                    "total_categories": result["total_categories"]
                }

                if result["success"]:
                    successful_merchants += 1
                    # Add merchant info to each category
                    for category in result["categories"]:
                        category["merchant_id"] = clover_merchant_id
                        category["merchant_name"] = name
                        all_categories.append(category)
                else:
                    failed_merchants += 1
                    merchant_result["error"] = result.get("error", "Unknown error")

            # Include failed merchants if requested
            if include_failed or merchant_result["success"]:
                merchant_results.append(merchant_result)

        # Remove duplicates based on category ID and merchant
        unique_categories = []
        seen_categories = set()

        for category in all_categories:
            category_key = f"{category.get('id', '')}_{category.get('merchant_id', '')}"
            if category_key not in seen_categories:
                seen_categories.add(category_key)
                unique_categories.append(category)

        return success_response(
            message="Merchant categories retrieved successfully",
            data={
                "merchants": merchant_results,
                "total_merchants": len(merchants),
                "successful_merchants": successful_merchants,
                "failed_merchants": failed_merchants,
                "total_categories": len(unique_categories),
                "categories": unique_categories
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving merchant categories: {str(e)}")
        return error_response(
            message="Failed to retrieve merchant categories",
            data={"error": str(e)},
            status_code=500
        )


@router.get("/{merchant_id}/categories")
async def get_merchant_categories(
    merchant_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of categories")
):
    """
    Retrieve categories for a specific merchant

    Args:
        merchant_id: Clover merchant ID
        db: Database session
        limit: Maximum number of categories to fetch

    Returns:
        Categories for the specified merchant
    """
    try:
        # Get merchant token
        access_token = MerchantHelper.get_merchant_token(db, merchant_id)
        if not access_token:
            return error_response(
                message=f"Merchant token not found for merchant {merchant_id}",
                status_code=404
            )

        # Fetch categories
        result = await _fetch_merchant_categories(merchant_id, access_token, limit)

        if not result["success"]:
            return error_response(
                message=f"Failed to fetch categories for merchant {merchant_id}",
                data={"error": result.get("error", "Unknown error")},
                status_code=400
            )

        return success_response(
            message=f"Categories retrieved successfully for merchant {merchant_id}",
            data={
                "merchant_id": merchant_id,
                "total_categories": result["total_categories"],
                "categories": result["categories"]
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving categories for merchant {merchant_id}: {str(e)}")
        return error_response(
            message="Failed to retrieve merchant categories",
            data={"error": str(e)},
            status_code=500
        )
