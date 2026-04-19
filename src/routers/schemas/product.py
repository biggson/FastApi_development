from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


# ── Request Schemas ──────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    unit_of_measure: Optional[str] = "pcs"
    initial_stock: Optional[int] = 0       # seeds inventory.quantity_on_hand on creation
    reorder_level: Optional[int] = 10
    reorder_quantity: Optional[int] = 50

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("initial_stock")
    @classmethod
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Initial stock cannot be negative")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


# ── Response Schemas ─────────────────────────────────────────────────────────

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    unit_of_measure: str
    is_active: bool
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProductWithStockResponse(ProductResponse):
    """Extended response that includes current stock level."""
    quantity_on_hand: Optional[int] = None
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None
