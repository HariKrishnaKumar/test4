from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from models.merchant_detail import MerchantDetail
from utils.response_formatter import success_response, error_response, not_found_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.get("/all")
async def get_all_merchants(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """
    Retrieve all merchants with their full details from the merchant_detail table

    Args:
        db: Database session
        limit: Optional limit for number of results
        offset: Optional offset for pagination

    Returns:
        List of all merchants with complete details
    """
    try:
        # Build query
        query = db.query(MerchantDetail)

        # Apply pagination if specified
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        # Execute query
        merchants = query.all()

        # Convert to list of dictionaries
        merchants_data = []
        for merchant in merchants:
            merchant_dict = {
                "id": merchant.id,
                "clover_merchant_id": merchant.clover_merchant_id,
                "name": merchant.name,
                "currency": merchant.currency,
                "timezone": merchant.timezone,
                "email": merchant.email,
                "address": merchant.address,
                "city": merchant.city,
                "state": merchant.state,
                "country": merchant.country,
                "postal_code": merchant.postal_code,
                "longitude": merchant.longitude,
                "latitude": merchant.latitude,
                "created_at": merchant.created_at.isoformat() if merchant.created_at else None,
                "updated_at": merchant.updated_at.isoformat() if merchant.updated_at else None
            }
            merchants_data.append(merchant_dict)

        # Get total count for pagination info
        total_count = db.query(MerchantDetail).count()

        return success_response(
            message="Merchants retrieved successfully",
            data={
                "merchants": merchants_data,
                "total_count": total_count,
                "returned_count": len(merchants_data),
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset or 0) + len(merchants_data) < total_count if limit else False
                }
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving merchants: {str(e)}")
        return error_response(
            message="Failed to retrieve merchants",
            data={"error": str(e)},
            status_code=500
        )


@router.get("/{merchant_id}")
async def get_merchant_by_id(
    merchant_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific merchant by ID from the merchant_detail table

    Args:
        merchant_id: The ID of the merchant to retrieve
        db: Database session

    Returns:
        Merchant details
    """
    try:
        merchant = db.query(MerchantDetail).filter(MerchantDetail.id == merchant_id).first()

        if not merchant:
            return not_found_response(
                message=f"Merchant with ID {merchant_id} not found"
            )

        merchant_data = {
            "id": merchant.id,
            "clover_merchant_id": merchant.clover_merchant_id,
            "name": merchant.name,
            "currency": merchant.currency,
            "timezone": merchant.timezone,
            "email": merchant.email,
            "address": merchant.address,
            "city": merchant.city,
            "state": merchant.state,
            "country": merchant.country,
            "postal_code": merchant.postal_code,
            "longitude": merchant.longitude,
            "latitude": merchant.latitude,
            "created_at": merchant.created_at.isoformat() if merchant.created_at else None,
            "updated_at": merchant.updated_at.isoformat() if merchant.updated_at else None
        }

        return success_response(
            message="Merchant retrieved successfully",
            data=merchant_data
        )

    except Exception as e:
        logger.error(f"Error retrieving merchant {merchant_id}: {str(e)}")
        return error_response(
            message="Failed to retrieve merchant",
            data={"error": str(e)},
            status_code=500
        )


@router.get("/clover/{clover_merchant_id}")
async def get_merchant_by_clover_id(
    clover_merchant_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific merchant by Clover merchant ID from the merchant_detail table

    Args:
        clover_merchant_id: The Clover merchant ID to search for
        db: Database session

    Returns:
        Merchant details
    """
    try:
        merchant = db.query(MerchantDetail).filter(
            MerchantDetail.clover_merchant_id == clover_merchant_id
        ).first()

        if not merchant:
            return not_found_response(
                message=f"Merchant with Clover ID {clover_merchant_id} not found"
            )

        merchant_data = {
            "id": merchant.id,
            "clover_merchant_id": merchant.clover_merchant_id,
            "name": merchant.name,
            "currency": merchant.currency,
            "timezone": merchant.timezone,
            "email": merchant.email,
            "address": merchant.address,
            "city": merchant.city,
            "state": merchant.state,
            "country": merchant.country,
            "postal_code": merchant.postal_code,
            "longitude": merchant.longitude,
            "latitude": merchant.latitude,
            "created_at": merchant.created_at.isoformat() if merchant.created_at else None,
            "updated_at": merchant.updated_at.isoformat() if merchant.updated_at else None
        }

        return success_response(
            message="Merchant retrieved successfully",
            data=merchant_data
        )

    except Exception as e:
        logger.error(f"Error retrieving merchant {clover_merchant_id}: {str(e)}")
        return error_response(
            message="Failed to retrieve merchant",
            data={"error": str(e)},
            status_code=500
        )
