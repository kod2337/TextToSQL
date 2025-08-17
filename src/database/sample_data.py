"""
Database initialization and sample data insertion
"""
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.connection import init_database, get_db, test_connection
from src.database.models import Customer, Product, Order, OrderItem
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_sample_customers(db: Session) -> list[Customer]:
    """Create sample customers"""
    customers_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0101",
            "address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@email.com",
            "phone": "+1-555-0102",
            "address": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90210"
        },
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@email.com",
            "phone": "+1-555-0103",
            "address": "789 Pine Rd",
            "city": "Chicago",
            "state": "IL",
            "zip_code": "60601"
        },
        {
            "first_name": "Alice",
            "last_name": "Williams",
            "email": "alice.williams@email.com",
            "phone": "+1-555-0104",
            "address": "321 Elm St",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        },
        {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@email.com",
            "phone": "+1-555-0105",
            "address": "654 Maple Dr",
            "city": "Phoenix",
            "state": "AZ",
            "zip_code": "85001"
        }
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        db.add(customer)
        customers.append(customer)
    
    db.commit()
    db.refresh(customers[0])  # Refresh to get IDs
    logger.info(f"Created {len(customers)} sample customers")
    return customers


def create_sample_products(db: Session) -> list[Product]:
    """Create sample products"""
    products_data = [
        {
            "name": "Laptop Computer",
            "description": "High-performance laptop for work and gaming",
            "category": "Electronics",
            "price": Decimal("1299.99"),
            "cost": Decimal("800.00"),
            "sku": "LAP-001",
            "stock_quantity": 25
        },
        {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse with long battery life",
            "category": "Electronics",
            "price": Decimal("29.99"),
            "cost": Decimal("15.00"),
            "sku": "MOU-001",
            "stock_quantity": 150
        },
        {
            "name": "Office Chair",
            "description": "Comfortable ergonomic office chair",
            "category": "Furniture",
            "price": Decimal("199.99"),
            "cost": Decimal("120.00"),
            "sku": "CHR-001",
            "stock_quantity": 45
        },
        {
            "name": "Smartphone",
            "description": "Latest model smartphone with advanced features",
            "category": "Electronics",
            "price": Decimal("699.99"),
            "cost": Decimal("400.00"),
            "sku": "PHN-001",
            "stock_quantity": 75
        },
        {
            "name": "Desk Lamp",
            "description": "LED desk lamp with adjustable brightness",
            "category": "Furniture",
            "price": Decimal("39.99"),
            "cost": Decimal("20.00"),
            "sku": "LMP-001",
            "stock_quantity": 100
        },
        {
            "name": "Bluetooth Headphones",
            "description": "Noise-cancelling wireless headphones",
            "category": "Electronics",
            "price": Decimal("149.99"),
            "cost": Decimal("80.00"),
            "sku": "HDP-001",
            "stock_quantity": 60
        },
        {
            "name": "Standing Desk",
            "description": "Height-adjustable standing desk",
            "category": "Furniture",
            "price": Decimal("399.99"),
            "cost": Decimal("250.00"),
            "sku": "DSK-001",
            "stock_quantity": 20
        },
        {
            "name": "Webcam",
            "description": "HD webcam for video conferencing",
            "category": "Electronics",
            "price": Decimal("79.99"),
            "cost": Decimal("45.00"),
            "sku": "CAM-001",
            "stock_quantity": 80
        }
    ]
    
    products = []
    for product_data in products_data:
        product = Product(**product_data)
        db.add(product)
        products.append(product)
    
    db.commit()
    db.refresh(products[0])  # Refresh to get IDs
    logger.info(f"Created {len(products)} sample products")
    return products


def create_sample_orders(db: Session, customers: list[Customer], products: list[Product]) -> list[Order]:
    """Create sample orders with order items"""
    orders = []
    
    # Create orders for the last 3 months
    base_date = datetime.now()
    
    # Order 1: John Doe - Recent order
    order1 = Order(
        customer_id=customers[0].id,
        order_date=base_date - timedelta(days=5),
        status="delivered",
        total_amount=Decimal("1379.97"),
        shipping_address="123 Main St",
        shipping_city="New York",
        shipping_state="NY",
        shipping_zip="10001"
    )
    db.add(order1)
    db.commit()
    db.refresh(order1)
    
    # Order items for order 1
    order1_items = [
        OrderItem(
            order_id=order1.id,
            product_id=products[0].id,  # Laptop
            quantity=1,
            unit_price=products[0].price,
            total_price=products[0].price
        ),
        OrderItem(
            order_id=order1.id,
            product_id=products[1].id,  # Mouse
            quantity=2,
            unit_price=products[1].price,
            total_price=products[1].price * 2
        ),
        OrderItem(
            order_id=order1.id,
            product_id=products[4].id,  # Desk Lamp
            quantity=1,
            unit_price=products[4].price,
            total_price=products[4].price
        )
    ]
    
    for item in order1_items:
        db.add(item)
    
    orders.append(order1)
    
    # Order 2: Jane Smith - Last month
    order2 = Order(
        customer_id=customers[1].id,
        order_date=base_date - timedelta(days=25),
        status="delivered",
        total_amount=Decimal("649.97"),
        shipping_address="456 Oak Ave",
        shipping_city="Los Angeles",
        shipping_state="CA",
        shipping_zip="90210"
    )
    db.add(order2)
    db.commit()
    db.refresh(order2)
    
    # Order items for order 2
    order2_items = [
        OrderItem(
            order_id=order2.id,
            product_id=products[6].id,  # Standing Desk
            quantity=1,
            unit_price=products[6].price,
            total_price=products[6].price
        ),
        OrderItem(
            order_id=order2.id,
            product_id=products[5].id,  # Headphones
            quantity=1,
            unit_price=products[5].price,
            total_price=products[5].price
        ),
        OrderItem(
            order_id=order2.id,
            product_id=products[1].id,  # Mouse
            quantity=1,
            unit_price=products[1].price,
            total_price=products[1].price
        )
    ]
    
    for item in order2_items:
        db.add(item)
    
    orders.append(order2)
    
    # Order 3: Bob Johnson - Processing
    order3 = Order(
        customer_id=customers[2].id,
        order_date=base_date - timedelta(days=2),
        status="processing",
        total_amount=Decimal("929.97"),
        shipping_address="789 Pine Rd",
        shipping_city="Chicago",
        shipping_state="IL",
        shipping_zip="60601"
    )
    db.add(order3)
    db.commit()
    db.refresh(order3)
    
    # Order items for order 3
    order3_items = [
        OrderItem(
            order_id=order3.id,
            product_id=products[3].id,  # Smartphone
            quantity=1,
            unit_price=products[3].price,
            total_price=products[3].price
        ),
        OrderItem(
            order_id=order3.id,
            product_id=products[2].id,  # Office Chair
            quantity=1,
            unit_price=products[2].price,
            total_price=products[2].price
        ),
        OrderItem(
            order_id=order3.id,
            product_id=products[1].id,  # Mouse
            quantity=1,
            unit_price=products[1].price,
            total_price=products[1].price
        )
    ]
    
    for item in order3_items:
        db.add(item)
    
    orders.append(order3)
    
    db.commit()
    logger.info(f"Created {len(orders)} sample orders with order items")
    return orders


def setup_sample_data() -> bool:
    """Set up all sample data"""
    try:
        # Test connection first
        if not test_connection():
            logger.error("Database connection failed")
            return False
        
        # Initialize database (create tables)
        init_database()
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Check if data already exists
            existing_customers = db.query(Customer).count()
            if existing_customers > 0:
                logger.info("Sample data already exists, skipping creation")
                return True
            
            # Create sample data
            logger.info("Creating sample data...")
            customers = create_sample_customers(db)
            products = create_sample_products(db)
            orders = create_sample_orders(db, customers, products)
            
            logger.info("Sample data created successfully")
            logger.info(f"Created: {len(customers)} customers, {len(products)} products, {len(orders)} orders")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to set up sample data: {e}")
        return False


if __name__ == "__main__":
    """Run this script to set up sample data"""
    success = setup_sample_data()
    if success:
        print("✅ Sample data setup completed successfully!")
    else:
        print("❌ Sample data setup failed!")
        exit(1)
