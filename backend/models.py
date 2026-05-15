from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Numeric, 
    TIMESTAMP, ForeignKey, Table, Enum, BigInteger, func, JSON
)
from sqlalchemy.orm import relationship
from database import Base
import datetime
from pgvector.sqlalchemy import Vector

# Association Table for Many-to-Many relationship between Properties and Features
# This allows one property to have many features (Pool, Wifi) 
# and one feature to be linked to many properties.
property_features = Table(
    'property_features',
    Base.metadata,
    Column('property_id', BigInteger, ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True),
    Column('feature_id', BigInteger, ForeignKey('features.id', ondelete='CASCADE'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="visitor") # visitor, client, agent, head_agent, admin
    is_active = Column(Boolean, default=True)
    google_calendar_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    manager_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    manager = relationship("User", remote_side=[id], backref="team_members")
    owned_properties = relationship("Property", back_populates="owner", foreign_keys="Property.owner_id")
    assigned_properties = relationship("Property", back_populates="agent", foreign_keys="Property.agent_id")

class Property(Base):
    __tablename__ = "properties"

    id = Column(BigInteger, primary_key=True, index=True)
    
    # Basic Info
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    property_type = Column(String(50), nullable=False)  # apartment, house, villa, studio, office
    listing_type = Column(String(20), nullable=False)   # sale, rent
    status = Column(String(20), default='available')    # available, sold, rented, pending
    
    # Pricing
    price = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default='TND')
    
    # Size & Structure
    area = Column(Numeric(10, 2))
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Integer, default=0)
    kitchens = Column(Integer, default=0)
    living_rooms = Column(Integer, default=0)
    floors = Column(Integer)
    floor_number = Column(Integer)
    
    
    # Location
    country = Column(String(100), nullable=False)
    state = Column(String(100))
    city = Column(String(100), nullable=False)
    neighborhood = Column(String(150))
    address = Column(Text)
    postal_code = Column(String(20))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))

    # System Fields
    is_featured = Column(Boolean, default=False)
    published_at = Column(TIMESTAMP)
    rent_start_date = Column(TIMESTAMP, nullable=True)
    rent_end_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # AI SEARCH: Store Ollama Embedding
    description_vector = Column(Vector(768), nullable=True)

    # Relationships
    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    agent_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    buyer_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))

    owner = relationship("User", back_populates="owned_properties", foreign_keys=[owner_id])
    agent = relationship("User", back_populates="assigned_properties", foreign_keys=[agent_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    features = relationship("Feature", secondary=property_features, back_populates="properties")

class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(BigInteger, primary_key=True, index=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="CASCADE"))
    image_url = Column(String, nullable=False)
    file_id = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    property = relationship("Property", back_populates="images")

class Feature(Base):
    __tablename__ = "features"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    properties = relationship("Property", secondary=property_features, back_populates="features")


class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(BigInteger, primary_key=True, index=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="CASCADE"))
    client_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"),nullable=True) #am going to remove nullable after testing with n8n
    agent_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    visit_date = Column(TIMESTAMP, nullable=False)
    status = Column(String(50), default="scheduled") # scheduled, finished, cancelled
    reminder_sent = Column(Boolean, default=False)
    telegram_chat_id = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    property = relationship("Property")
    client = relationship("User", foreign_keys=[client_id])
    agent = relationship("User", foreign_keys=[agent_id])

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(BigInteger, primary_key=True, index=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="CASCADE"))
    transaction_type = Column(String(50), nullable=False) # Sale, Rent
    buyer_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    agent_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    price_at_time = Column(Numeric(15, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    property = relationship("Property")
    buyer = relationship("User", foreign_keys=[buyer_id])
    agent = relationship("User", foreign_keys=[agent_id])

class TransactionRequest(Base):
    __tablename__ = "transaction_requests"
    
    id = Column(BigInteger, primary_key=True, index=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="CASCADE"))
    agent_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    client_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    type = Column(String(50), nullable=False) # Sale, Rent
    status = Column(String(50), default="pending") # pending, approved, rejected
    price = Column(Numeric(15, 2))
    rent_start_date = Column(TIMESTAMP, nullable=True)
    rent_end_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    property = relationship("Property")
    agent = relationship("User", foreign_keys=[agent_id])
    client = relationship("User", foreign_keys=[client_id])


