"""
Database models for the Text-to-SQL Assistant
Sample e-commerce schema: customers, products, orders, order_items
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.connection import Base


class Customer(Base):
    """Customer table"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(50))
    state = Column(String(50))
    zip_code = Column(String(10))
    country = Column(String(50), default="USA")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"


class Product(Base):
    """Product table"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    sku = Column(String(50), unique=True, nullable=False, index=True)
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class Order(Base):
    """Order table"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="pending")  # pending, processing, shipped, delivered, cancelled
    total_amount = Column(Numeric(10, 2), nullable=False)
    shipping_address = Column(Text)
    shipping_city = Column(String(50))
    shipping_state = Column(String(50))
    shipping_zip = Column(String(10))
    shipping_country = Column(String(50), default="USA")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, customer_id={self.customer_id}, total={self.total_amount}, status='{self.status}')>"


class OrderItem(Base):
    """Order items table"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"


# Export all models for easy imports
__all__ = ["Customer", "Product", "Order", "OrderItem", "Base"]
