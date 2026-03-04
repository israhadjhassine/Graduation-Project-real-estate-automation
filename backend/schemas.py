from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

# --- Authentication ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "visitor"
    manager_id: Optional[int] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserCreateAdmin(UserBase):
    password: str
    role: str
    manager_id: Optional[int] = None

class User(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None

# --- Property ---
class FeatureBase(BaseModel):
    name: str

class Feature(FeatureBase):
    id: int
    class Config:
        from_attributes = True

class PropertyImageBase(BaseModel):
    image_url: str
    is_primary: bool

class PropertyImage(PropertyImageBase):
    id: int
    class Config:
        from_attributes = True

class PropertyType(str, Enum):
    apartment = "apartment"
    house = "house"
    villa = "villa"

class ListingType(str, Enum):
    sale = "sale"
    rent = "rent"

class PropertyBase(BaseModel):
    title: str
    slug: str
    description: str
    property_type: PropertyType
    listing_type: ListingType
    price: Decimal
    currency: str = "TND"
    area: Optional[Decimal] = None
    bedrooms: int = 0
    bathrooms: int = 0
    city: str
    country: str = "Tunisia"

class PropertyCreate(PropertyBase):
    agent_id: Optional[int] = None
    owner_id: Optional[int] = None
    feature_ids: List[int] = []

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[PropertyType] = None
    listing_type: Optional[ListingType] = None
    price: Optional[Decimal] = None
    area: Optional[Decimal] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    agent_id: Optional[int] = None
    owner_id: Optional[int] = None
    feature_ids: Optional[List[int]] = None

class Property(PropertyBase):
    id: int
    status: str
    is_featured: Optional[bool] = None
    created_at: datetime
    owner_id: int
    agent_id: Optional[int] = None
    images: List[PropertyImage] = []
    features: List[Feature] = []

    class Config:
        from_attributes = True

# --- AI Inquiries ---
class PropertyQuestion(BaseModel):
    question: str

class AIResponse(BaseModel):
    answer: str
    source_confidence: float

# --- Interactions ---
class InquiryCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str
    source: Optional[str] = "web"

class InquiryResponse(InquiryCreate):
    id: int
    property_id: Optional[int] = None
    user_id: Optional[int] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class VisitResponse(BaseModel):
    id: int
    property_id: int
    client_id: int
    agent_id: Optional[int] = None
    visit_date: datetime
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True