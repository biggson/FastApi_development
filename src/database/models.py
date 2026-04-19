from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "boarder"}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(50), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default="user")          # "admin" or "user"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "boarder"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, index=True, nullable=False)  # stock-keeping unit
    description = Column(String(500))
    price = Column(Float, nullable=False)
    category = Column(String(100))
    unit_of_measure = Column(String(50), default="pcs")  # pcs, kg, liter, box, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("boarder.users.id"), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    transactions = relationship("Transaction", back_populates="product")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = {"schema": "boarder"}

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("boarder.products.id"), unique=True, nullable=False)
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=10)       # alert threshold
    reorder_quantity = Column(Integer, default=50)    # suggested restock amount
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "boarder"}

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("boarder.products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("boarder.users.id"), nullable=False)
    # transaction_type: IN (restock), OUT (sold/consumed), ADJUSTMENT (manual correction), RETURN
    transaction_type = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)          # always positive
    unit_price = Column(Float, nullable=False)          # price at time of transaction
    total_amount = Column(Float, nullable=False)        # quantity * unit_price
    reference_number = Column(String(100))              # PO number, invoice, etc.
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
