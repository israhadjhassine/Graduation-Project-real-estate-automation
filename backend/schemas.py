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
    role: Optional[str] = "client"
    manager_id: Optional[int] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None

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
    telegram_chat_id: Optional[str] = None

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
    file_id: Optional[str] = None
    is_primary: bool

class PropertyImage(PropertyImageBase):
    id: int
    class Config:
        from_attributes = True

class PropertyType(str, Enum):
    apartment = "apartment"
    house = "house"
    villa = "villa"
    studio = "studio"
    office = "office"

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
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

class PropertyCreate(PropertyBase):
    agent_id: Optional[int] = None
    owner_id: Optional[int] = None
    feature_ids: List[int] = []
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

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
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

class Property(PropertyBase):
    id: int
    status: str
    is_featured: Optional[bool] = None
    created_at: datetime
    rent_start_date: Optional[datetime] = None
    rent_end_date: Optional[datetime] = None
    owner_id: int
    agent_id: Optional[int] = None
    buyer_id: Optional[int] = None
    images: List[PropertyImage] = []
    features: List[Feature] = []

    class Config:
        from_attributes = True

class PropertyMinimal(BaseModel):
    id: int
    title: str
    city: str
    price: Decimal
    currency: str
    status: str
    listing_type: ListingType

    class Config:
        from_attributes = True

# --- AI Inquiries ---
class PropertyQuestion(BaseModel):
    question: str

class AIResponse(BaseModel):
    answer: str
    source_confidence: float

# --- Interactions ---

class VisitResponse(BaseModel):
    id: int
    property_id: int
    client_id: Optional[int] = None
    agent_id: Optional[int] = None
    visit_date: datetime
    status: str
    reminder_sent: bool = False
    telegram_chat_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class VisitDetailResponse(VisitResponse):
    property: Optional[Property] = None
    client: Optional[User] = None
    agent: Optional[User] = None

class VisitCreate(BaseModel):
    property_id: int
    client_telegram_id: str
    client_email: Optional[str] = None
    agent_id: Optional[int] = None
    visit_date: datetime

class SemanticSearchQuery(BaseModel):
    query: Optional[str] = None
    feature_ids: Optional[List[int]] = None

class RAGProperty(BaseModel):
    id: int
    agent_id: Optional[int] = None
    agent_name: Optional[str] = None 
    title: str
    property_type: str
    listing_type: str
    price: Decimal
    currency: str
    city: str
    area: Optional[Decimal] = None
    bedrooms: int
    bathrooms: int
    features: List[str]
    description: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    google_maps_url: Optional[str] = None

class RAGSearchResponse(BaseModel):
    context: str
    properties: List[RAGProperty]

# --- Transaction Requests ---
class TransactionRequestBase(BaseModel):
    type: str # Sale, Rent
    price: Decimal
    client_id: int
    rent_start_date: Optional[datetime] = None
    rent_end_date: Optional[datetime] = None

class TransactionRequestCreate(TransactionRequestBase):
    pass

class TransactionRequest(TransactionRequestBase):
    id: int
    property_id: int
    agent_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    # We might want nested details for the UI
    property: Optional[PropertyMinimal] = None
    agent: Optional[User] = None
    client: Optional[User] = None

    class Config:
        from_attributes = True

class TransactionFinalize(BaseModel):
    action: str # "complete" or "cancel"

# --- Telegram Pairing ---
class TelegramCodeResponse(BaseModel):
    code: str
    expires_in_seconds: int

class TelegramPairRequest(BaseModel):
    code: str
    telegram_chat_id: str

class TelegramPairingSuccessResponse(BaseModel):
    status: str
    user_name: str
    email: str

class VisitUpdateDB (BaseModel):
    client_telegram_id:str
    property_id:int
    original_visit_date:datetime
    new_visit_date:datetime

class VisitCancelDB (BaseModel):
    client_telegram_id:str
    property_id:int
    visit_date:datetime