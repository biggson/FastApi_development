from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from src.database.connection import get_db
from src.database.models import Product, Inventory, User
from src.routers.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductWithStockResponse
from src.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/products", tags=["Products"])


# ── Create product ────────────────────────────────────────────────────────────

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new product. Automatically creates an inventory record for it."""

    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise HTTPException(status_code=400, detail=f"SKU '{payload.sku}' already exists")

    product = Product(
        name=payload.name,
        sku=payload.sku,
        description=payload.description,
        price=payload.price,
        category=payload.category,
        unit_of_measure=payload.unit_of_measure,
        owner_id=current_user.id,
    )
    db.add(product)
    db.flush()   # get product.id before committing

    # Auto-create inventory record for the new product
    inventory = Inventory(
        product_id=product.id,
        quantity_on_hand=payload.initial_stock,
        reorder_level=payload.reorder_level,
        reorder_quantity=payload.reorder_quantity,
    )
    db.add(inventory)
    db.commit()
    db.refresh(product)
    return product


# ── Get all products ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[ProductWithStockResponse])
def get_products(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    category: str = Query(default=None),
    search: str = Query(default=None, description="Search by product name"),
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all products with current stock levels. Supports filtering and search."""
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active == True)
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # Non-admins only see their own products
    if current_user.role != "admin":
        query = query.filter(Product.owner_id == current_user.id)

    products = query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for p in products:
        data = ProductWithStockResponse.model_validate(p)
        if p.inventory:
            data.quantity_on_hand = p.inventory.quantity_on_hand
            data.reorder_level = p.inventory.reorder_level
            data.reorder_quantity = p.inventory.reorder_quantity
        result.append(data)
    return result


# ── Get product by ID ─────────────────────────────────────────────────────────

@router.get("/{product_id}", response_model=ProductWithStockResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single product with its current stock level."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Non-admins can only view their own products
    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    data = ProductWithStockResponse.model_validate(product)
    if product.inventory:
        data.quantity_on_hand = product.inventory.quantity_on_hand
        data.reorder_level = product.inventory.reorder_level
        data.reorder_quantity = product.inventory.reorder_quantity
    return data


# ── Update product ────────────────────────────────────────────────────────────

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update product details. Owner or admin only."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


# ── Deactivate product ────────────────────────────────────────────────────────

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a product by marking it inactive. Owner or admin only."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    product.is_active = False
    db.commit()
    return {"message": f"Product '{product.name}' has been deactivated"}
