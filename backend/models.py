from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Numeric, 
    TIMESTAMP, ForeignKey, Table, Enum, BigInteger, func
)
from sqlalchemy.orm import relationship
from database import Base
import datetime

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
    role = Column(String(20), default="visitor") # visitor, agent, head_agent, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    manager_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    manager = relationship("User", remote_side=[id], backref="team_members")
    owned_properties = relationship("Property", back_populates="owner", foreign_keys="Property.owner_id")
    assigned_properties = relationship("Property", back_populates="agent", foreign_keys="Property.agent_id")
    favorites = relationship("PropertyFavorite", back_populates="user")

class Property(Base):
    __tablename__ = "properties"

    id = Column(BigInteger, primary_key=True, index=True)
    
    # Basic Info
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    property_type = Column(String(50), nullable=False)  # apartment, house, villa, land
    listing_type = Column(String(20), nullable=False)   # sale, rent
    status = Column(String(20), default='available')    # available, sold, rented, pending
    
    # Pricing
    price = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default='TND')
    
    # Size & Structure
    area = Column(Numeric(10, 2))
    built_area = Column(Numeric(10, 2))
    land_area = Column(Numeric(10, 2))
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Integer, default=0)
    kitchens = Column(Integer, default=0)
    living_rooms = Column(Integer, default=0)
    floors = Column(Integer)
    floor_number = Column(Integer)
    
    # Features (Legacy checkboxes, keeping for compatibility with existing UI)
    has_garage = Column(Boolean, default=False)
    has_garden = Column(Boolean, default=False)
    has_pool = Column(Boolean, default=False)
    has_elevator = Column(Boolean, default=False)
    has_furnished = Column(Boolean, default=False)
    has_balcony = Column(Boolean, default=False)
    
    # Location
    country = Column(String(100), nullable=False)
    state = Column(String(100))
    city = Column(String(100), nullable=False)
    neighborhood = Column(String(150))
    address = Column(Text)
    postal_code = Column(String(20))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    
    # SEO & Metadata
    meta_title = Column(String(255))
    meta_description = Column(Text)
    
    # Analytics
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)
    
    # System Fields
    is_featured = Column(Boolean, default=False)
    published_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # AI SEARCH: Store Gemini Embedding
    # Removed temporarily to avoid pgvector requirement

    # Relationships
    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    agent_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))

    owner = relationship("User", back_populates="owned_properties", foreign_keys=[owner_id])
    agent = relationship("User", back_populates="assigned_properties", foreign_keys=[agent_id])
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    features = relationship("Feature", secondary=property_features, back_populates="properties")

class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(BigInteger, primary_key=True, index=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="CASCADE"))
    image_url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    property = relationship("Property", back_populates="images")

class Feature(Base):
    __tablename__ = "features"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    properties = relationship("Property", secondary=property_features, back_populates="features")

class Inquiry(Base):
    __tablename__ = "inquiries"
    
    id = Column(BigInteger, primary_key=True, index=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # If logged in
    name = Column(String(150))
    email = Column(String(255))
    phone = Column(String(50))
    subject = Column(String(200))
    message = Column(Text, nullable=False)
    status = Column(String(50), default="new") # new, replied, closed
    source = Column(String(50), default="web") # web, telegram
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    property = relationship("Property")
    user = relationship("User")

class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(BigInteger, primary_key=True, index=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="CASCADE"))
    client_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    agent_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    visit_date = Column(TIMESTAMP, nullable=False)
    status = Column(String(50), default="scheduled") # scheduled, finished, cancelled
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    property = relationship("Property")
    client = relationship("User", foreign_keys=[client_id])
    agent = relationship("User", foreign_keys=[agent_id])

class PropertyFavorite(Base):
    __tablename__ = "property_favorites"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    property_id = Column(BigInteger, ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="favorites")
