from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

VALID_TRANSACTION_TYPES = {"IN", "OUT", "ADJUSTMENT", "RETURN"}


# ── Request Schemas ──────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    product_id: int
    transaction_type: str              # IN | OUT | ADJUSTMENT | RETURN
    quantity: int
    unit_price: float
    reference_number: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("transaction_type")
    @classmethod
    def validate_type(cls, v):
        v = v.upper()
        if v not in VALID_TRANSACTION_TYPES:
            raise ValueError(f"transaction_type must be one of {VALID_TRANSACTION_TYPES}")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    @field_validator("unit_price")
    @classmethod
    def price_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Unit price cannot be negative")
        return v


# ── Response Schemas ─────────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    transaction_type: str
    quantity: int
    unit_price: float
    total_amount: float
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionDetailResponse(TransactionResponse):
    """Extended response with product and user info."""
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    performed_by: Optional[str] = None    # username
