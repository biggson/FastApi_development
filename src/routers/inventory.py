from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from src.database.connection import get_db
from src.database.models import Inventory, Product, User
from src.routers.schemas.inventory import InventoryUpdate, InventoryResponse, InventoryWithProductResponse
from src.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ── Get all inventory ─────────────────────────────────────────────────────────

@router.get("/", response_model=List[InventoryWithProductResponse])
def get_all_inventory(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all inventory records with product info."""
    query = db.query(Inventory).join(Product, Inventory.product_id == Product.id)

    # Non-admins only see inventory for their own products
    if current_user.role != "admin":
        query = query.filter(Product.owner_id == current_user.id)

    records = query.order_by(Inventory.id).offset(offset).limit(limit).all()

    result = []
    for inv in records:
        data = InventoryWithProductResponse.model_validate(inv)
        data.product_name = inv.product.name if inv.product else None
        data.product_sku = inv.product.sku if inv.product else None
        data.is_low_stock = inv.quantity_on_hand <= inv.reorder_level
        result.append(data)
    return result


# ── Get low stock items ───────────────────────────────────────────────────────

@router.get("/low-stock", response_model=List[InventoryWithProductResponse])
def get_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all products where quantity_on_hand is at or below the reorder level."""
    query = (
        db.query(Inventory)
        .join(Product, Inventory.product_id == Product.id)
        .filter(Inventory.quantity_on_hand <= Inventory.reorder_level)
        .filter(Product.is_active == True)
    )

    if current_user.role != "admin":
        query = query.filter(Product.owner_id == current_user.id)

    records = query.all()

    result = []
    for inv in records:
        data = InventoryWithProductResponse.model_validate(inv)
        data.product_name = inv.product.name if inv.product else None
        data.product_sku = inv.product.sku if inv.product else None
        data.is_low_stock = True
        result.append(data)
    return result


# ── Get inventory by product ID ───────────────────────────────────────────────

@router.get("/{product_id}", response_model=InventoryWithProductResponse)
def get_inventory_by_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the inventory record for a specific product."""
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()

    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found")

    # Non-admins can only view inventory for their own products
    if current_user.role != "admin" and inv.product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    data = InventoryWithProductResponse.model_validate(inv)
    data.product_name = inv.product.name if inv.product else None
    data.product_sku = inv.product.sku if inv.product else None
    data.is_low_stock = inv.quantity_on_hand <= inv.reorder_level
    return data


# ── Update reorder settings (admin only) ─────────────────────────────────────

@router.put("/{product_id}", response_model=InventoryResponse)
def update_inventory_settings(
    product_id: int,
    payload: InventoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Update reorder level and reorder quantity for a product. Admin only.
    Note: quantity_on_hand can only be changed via transactions."""
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()

    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(inv, field, value)

    db.commit()
    db.refresh(inv)
    return inv
