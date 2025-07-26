from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Chat-related schemas
class ChatMessageRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    message_type: str
    content: str
    timestamp: datetime

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    created_at: datetime
    is_active: bool
    messages: List[ChatMessageResponse] = []

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: int

# User schemas
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    street_address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    traffic_source: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    cost: float
    category: str
    name: str
    brand: str
    retail_price: float
    department: str
    sku: str
    distribution_center_id: int

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    user_id: int
    status: str
    gender: Optional[str] = None
    num_of_item: int

class OrderResponse(OrderBase):
    order_id: int
    created_at: datetime
    returned_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Inventory schemas
class InventoryItemBase(BaseModel):
    product_id: int
    cost: float
    product_category: str
    product_name: str
    product_brand: str
    product_retail_price: float
    product_department: str
    product_sku: str
    product_distribution_center_id: int

class InventoryItemResponse(InventoryItemBase):
    id: int
    created_at: datetime
    sold_at: Optional[datetime] = None

    class Config:
        from_attributes = True 