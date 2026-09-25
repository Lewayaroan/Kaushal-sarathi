from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
try:
    from .database import Base
except (ImportError, ValueError):
    from database import Base

class Artisan(Base):
    __tablename__ = "artisans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_number = Column(String, unique=True, index=True)
    state = Column(String)
    language = Column(String)
    pin_code = Column(String)

    products = relationship("Product", back_populates="artisan")
    khata_transactions = relationship("KhataTransaction", back_populates="artisan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    raw_description = Column(String)  # Original voice transcription
    base_price = Column(Float)
    dynamic_price = Column(Float)  # Calculated fair price
    category = Column(String)
    hsn_code = Column(String)
    image_url = Column(String)  # Enhanced studio photo url
    original_image_url = Column(String)  # Cluttered photo url
    status = Column(String, default="Draft")  # Draft, Listed_ONDC, Sold
    artisan_id = Column(Integer, ForeignKey("artisans.id"))

    artisan = relationship("Artisan", back_populates="products")


class KhataTransaction(Base):
    __tablename__ = "khata_transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # SALE or EXPENSE
    amount = Column(Float)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    sync_status = Column(String, default="Synced")  # Synced, Pending
    artisan_id = Column(Integer, ForeignKey("artisans.id"))

    artisan = relationship("Artisan", back_populates="khata_transactions")


class LogisticsPool(Base):
    __tablename__ = "logistics_pools"

    id = Column(Integer, primary_key=True, index=True)
    village_name = Column(String)
    pincode = Column(String)
    status = Column(String, default="Collecting")  # Collecting, Dispatched
    total_weight = Column(Float, default=0.0)
    orders_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
