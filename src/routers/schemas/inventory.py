from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


# ── Request Schemas ──────────────────────────────────────────────────────────

class InventoryUpdate(BaseModel):
    """Only reorder settings are directly editable.
    quantity_on_hand is managed exclusively via transactions."""
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None

    @field_validator("reorder_level", "reorder_quantity")
    @classmethod
    def must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Value cannot be negative")
        return v


# ── Response Schemas ─────────────────────────────────────────────────────────

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity_on_hand: int
    reorder_level: int
    reorder_quantity: int
    last_updated: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InventoryWithProductResponse(InventoryResponse):
    """Extended response that includes product name and SKU."""
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    is_low_stock: Optional[bool] = None    # True when quantity_on_hand <= reorder_level
