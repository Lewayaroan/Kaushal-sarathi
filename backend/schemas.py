from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Artisan schemas
class ArtisanBase(BaseModel):
    name: str
    contact_number: str
    state: str
    language: str
    pin_code: str

class ArtisanCreate(ArtisanBase):
    pass

class ArtisanResponse(ArtisanBase):
    id: int
    class Config:
        orm_mode = True

# Product schemas
class ProductBase(BaseModel):
    title: str
    description: str
    raw_description: Optional[str] = None
    base_price: float
    dynamic_price: Optional[float] = None
    category: str
    hsn_code: Optional[str] = None
    image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    status: str = "Draft"
    artisan_id: int

class ProductCreate(BaseModel):
    title: str
    description: str
    raw_description: Optional[str] = None
    base_price: float
    dynamic_price: Optional[float] = None
    category: str
    hsn_code: Optional[str] = None
    image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    artisan_id: int

class ProductResponse(ProductBase):
    id: int
    class Config:
        orm_mode = True

# Khata Transaction schemas
class KhataBase(BaseModel):
    type: str  # SALE or EXPENSE
    amount: float
    details: str
    sync_status: str = "Synced"
    artisan_id: int

class KhataCreate(KhataBase):
    pass

class KhataResponse(KhataBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True

# Custom request schemas for AI processing
class VoiceCatalogRequest(BaseModel):
    audio_base64: str  # Mocking audio file transfer
    language: str
    artisan_id: int

class VoiceCatalogResponse(BaseModel):
    transcription: str
    translated_text: str
    title: str
    description: str
    category: str
    hsn_code: str
    suggested_price: float

class ImageEnhanceRequest(BaseModel):
    original_image_url: str
    theme: str  # e.g., "studio", "wooden_table", "festival_lights"

class ImageEnhanceResponse(BaseModel):
    original_image_url: str
    enhanced_image_url: str

class FairPriceRequest(BaseModel):
    material_cost: float
    labor_hours: float
    overhead_cost: float
    desired_hourly_wage: Optional[float] = 60.0  # Default ~₹480/day for 8 hours (higher than typical rural min wage)
    artisan_state: str

# Logistics Pool schemas
class LogisticsPoolBase(BaseModel):
    village_name: str
    pincode: str
    status: str = "Collecting"
    total_weight: float = 0.0
    orders_count: int = 0

class LogisticsPoolResponse(LogisticsPoolBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True
