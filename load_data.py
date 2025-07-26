import pandas as pd
import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base, DistributionCenter, Product, InventoryItem, User, Order, OrderItem

def load_distribution_centers(db: Session, csv_path: str):
    """Load distribution centers from CSV"""
    print("Loading distribution centers...")
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        dc = DistributionCenter(
            id=row['id'],
            name=row['name'],
            latitude=row['latitude'],
            longitude=row['longitude']
        )
        db.add(dc)
    
    db.commit()
    print(f"Loaded {len(df)} distribution centers")

def load_products(db: Session, csv_path: str):
    """Load products from CSV"""
    print("Loading products...")
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        product = Product(
            id=row['id'],
            cost=row['cost'],
            category=row['category'],
            name=row['name'],
            brand=row['brand'],
            retail_price=row['retail_price'],
            department=row['department'],
            sku=row['sku'],
            distribution_center_id=row['distribution_center_id']
        )
        db.add(product)
    
    db.commit()
    print(f"Loaded {len(df)} products")

def load_inventory_items(db: Session, csv_path: str):
    """Load inventory items from CSV"""
    print("Loading inventory items...")
    df = pd.read_csv(csv_path)
    
    # Process in chunks to avoid memory issues
    chunk_size = 1000
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        
        for _, row in chunk.iterrows():
            # Convert timestamp strings to datetime objects
            created_at = pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else None
            sold_at = pd.to_datetime(row['sold_at']) if pd.notna(row['sold_at']) else None
            
            inventory_item = InventoryItem(
                id=row['id'],
                product_id=row['product_id'],
                created_at=created_at,
                sold_at=sold_at,
                cost=row['cost'],
                product_category=row['product_category'],
                product_name=row['product_name'],
                product_brand=row['product_brand'],
                product_retail_price=row['product_retail_price'],
                product_department=row['product_department'],
                product_sku=row['product_sku'],
                product_distribution_center_id=row['product_distribution_center_id']
            )
            db.add(inventory_item)
        
        db.commit()
        print(f"Processed {min(i+chunk_size, len(df))}/{len(df)} inventory items")

def load_users(db: Session, csv_path: str):
    """Load users from CSV"""
    print("Loading users...")
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        created_at = pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else None
        
        user = User(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            age=row['age'] if pd.notna(row['age']) else None,
            gender=row['gender'],
            state=row['state'],
            street_address=row['street_address'],
            postal_code=row['postal_code'],
            city=row['city'],
            country=row['country'],
            latitude=row['latitude'] if pd.notna(row['latitude']) else None,
            longitude=row['longitude'] if pd.notna(row['longitude']) else None,
            traffic_source=row['traffic_source'],
            created_at=created_at
        )
        db.add(user)
    
    db.commit()
    print(f"Loaded {len(df)} users")

def load_orders(db: Session, csv_path: str):
    """Load orders from CSV"""
    print("Loading orders...")
    df = pd.read_csv(csv_path)
    
    for _, row in df.iterrows():
        created_at = pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else None
        returned_at = pd.to_datetime(row['returned_at']) if pd.notna(row['returned_at']) else None
        shipped_at = pd.to_datetime(row['shipped_at']) if pd.notna(row['shipped_at']) else None
        delivered_at = pd.to_datetime(row['delivered_at']) if pd.notna(row['delivered_at']) else None
        
        order = Order(
            order_id=row['order_id'],
            user_id=row['user_id'],
            status=row['status'],
            gender=row['gender'],
            created_at=created_at,
            returned_at=returned_at,
            shipped_at=shipped_at,
            delivered_at=delivered_at,
            num_of_item=row['num_of_item']
        )
        db.add(order)
    
    db.commit()
    print(f"Loaded {len(df)} orders")

def load_order_items(db: Session, csv_path: str):
    """Load order items from CSV"""
    print("Loading order items...")
    df = pd.read_csv(csv_path)
    
    # Process in chunks to avoid memory issues
    chunk_size = 1000
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        
        for _, row in chunk.iterrows():
            created_at = pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else None
            shipped_at = pd.to_datetime(row['shipped_at']) if pd.notna(row['shipped_at']) else None
            delivered_at = pd.to_datetime(row['delivered_at']) if pd.notna(row['delivered_at']) else None
            returned_at = pd.to_datetime(row['returned_at']) if pd.notna(row['returned_at']) else None
            
            order_item = OrderItem(
                id=row['id'],
                order_id=row['order_id'],
                user_id=row['user_id'],
                product_id=row['product_id'],
                inventory_item_id=row['inventory_item_id'],
                status=row['status'],
                created_at=created_at,
                shipped_at=shipped_at,
                delivered_at=delivered_at,
                returned_at=returned_at
            )
            db.add(order_item)
        
        db.commit()
        print(f"Processed {min(i+chunk_size, len(df))}/{len(df)} order items")

def main():
    """Main function to load all data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Define CSV file paths
        csv_dir = r"C:\Users\rohan\Downloads\archive\archive"
        
        # Load data in order (respecting foreign key constraints)
        load_distribution_centers(db, os.path.join(csv_dir, "distribution_centers.csv"))
        load_products(db, os.path.join(csv_dir, "products.csv"))
        load_inventory_items(db, os.path.join(csv_dir, "inventory_items.csv"))
        load_users(db, os.path.join(csv_dir, "users.csv"))
        load_orders(db, os.path.join(csv_dir, "orders.csv"))
        load_order_items(db, os.path.join(csv_dir, "order_items.csv"))
        
        print("Data loading completed successfully!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 