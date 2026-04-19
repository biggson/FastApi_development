from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database.connection import get_db
from src.database.models import Transaction, Inventory, Product, User
from src.routers.schemas.transaction import TransactionCreate, TransactionResponse, TransactionDetailResponse
from src.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _apply_stock_change(inv: Inventory, transaction_type: str, quantity: int):
    """Apply stock movement to an inventory record based on transaction type."""
    if transaction_type == "IN":
        inv.quantity_on_hand += quantity
    elif transaction_type == "OUT":
        if inv.quantity_on_hand < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {inv.quantity_on_hand}, Requested: {quantity}"
            )
        inv.quantity_on_hand -= quantity
    elif transaction_type == "RETURN":
        inv.quantity_on_hand += quantity
    elif transaction_type == "ADJUSTMENT":
        # ADJUSTMENT sets quantity_on_hand directly to the given quantity
        inv.quantity_on_hand = quantity


# ── Create transaction ────────────────────────────────────────────────────────

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a stock movement. Automatically updates inventory quantity.

    Transaction types:
    - IN        : Stock received (purchase / restock) — increases quantity
    - OUT       : Stock consumed / sold — decreases quantity (validates stock availability)
    - RETURN    : Returned goods — increases quantity
    - ADJUSTMENT: Manual stock correction (admin only) — sets quantity directly
    """

    # ADJUSTMENT is restricted to admins
    if payload.transaction_type == "ADJUSTMENT" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create ADJUSTMENT transactions"
        )

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if not product.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is inactive")

    # Non-admins can only transact on their own products
    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this product")

    inv = db.query(Inventory).filter(Inventory.product_id == payload.product_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found")

    # Apply stock change (raises 400 if OUT has insufficient stock)
    _apply_stock_change(inv, payload.transaction_type, payload.quantity)

    transaction = Transaction(
        product_id=payload.product_id,
        user_id=current_user.id,
        transaction_type=payload.transaction_type,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_amount=round(payload.quantity * payload.unit_price, 2),
        reference_number=payload.reference_number,
        notes=payload.notes,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


# ── Get all transactions ──────────────────────────────────────────────────────

@router.get("/", response_model=List[TransactionDetailResponse])
def get_all_transactions(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    product_id: Optional[int] = Query(default=None),
    transaction_type: Optional[str] = Query(default=None, description="IN | OUT | ADJUSTMENT | RETURN"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return transactions with optional filters. Non-admins see only their own product transactions."""
    query = db.query(Transaction).join(Product, Transaction.product_id == Product.id)

    if current_user.role != "admin":
        query = query.filter(Product.owner_id == current_user.id)
    if product_id:
        query = query.filter(Transaction.product_id == product_id)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type.upper())

    records = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for t in records:
        data = TransactionDetailResponse.model_validate(t)
        data.product_name = t.product.name if t.product else None
        data.product_sku = t.product.sku if t.product else None
        data.performed_by = t.user.username if t.user else None
        result.append(data)
    return result


# ── Get transaction by ID ─────────────────────────────────────────────────────

@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single transaction by ID."""
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if current_user.role != "admin" and t.product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    data = TransactionDetailResponse.model_validate(t)
    data.product_name = t.product.name if t.product else None
    data.product_sku = t.product.sku if t.product else None
    data.performed_by = t.user.username if t.user else None
    return data


# ── Get transactions by product ───────────────────────────────────────────────

@router.get("/product/{product_id}", response_model=List[TransactionDetailResponse])
def get_transactions_by_product(
    product_id: int,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the full transaction history for a specific product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    records = (
        db.query(Transaction)
        .filter(Transaction.product_id == product_id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = []
    for t in records:
        data = TransactionDetailResponse.model_validate(t)
        data.product_name = t.product.name if t.product else None
        data.product_sku = t.product.sku if t.product else None
        data.performed_by = t.user.username if t.user else None
        result.append(data)
    return result
