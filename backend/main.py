import os
import sys

# Ensure backend directory is in sys.path for direct imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

try:
    from .database import engine, Base, get_db
    from . import models, schemas
    from .routers import catalog, khata, utilities
except (ImportError, ValueError):
    from database import engine, Base, get_db
    import models, schemas
    from routers import catalog, khata, utilities

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Driven Market Linkage & Smart Cataloging Platform for Artisans",
    description="SIH 2026 Project (Problem Statement SIH26090)",
    version="1.0.0"
)

# Configure CORS so our local frontend SPA can call the API endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development and ease of running locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(catalog.router)
app.include_router(khata.router)
app.include_router(utilities.router)

@app.get("/")
def health_check():
    return {
        "status": "Healthy",
        "project": "SIH 2026 - AI-Driven Market Linkage for Marginalized Artisans",
        "api_documentation": "/docs"
    }

# Artisan Authentication / Profile management
@app.post("/api/artisan/register", response_model=schemas.ArtisanResponse)
def register_artisan(artisan: schemas.ArtisanCreate, db: Session = Depends(get_db)):
    db_artisan = db.query(models.Artisan).filter(models.Artisan.contact_number == artisan.contact_number).first()
    if db_artisan:
        raise HTTPException(
            status_code=400,
            detail="Contact number already registered. Please login."
        )
    new_artisan = models.Artisan(**artisan.dict())
    db.add(new_artisan)
    db.commit()
    db.refresh(new_artisan)
    return new_artisan


@app.post("/api/artisan/login", response_model=schemas.ArtisanResponse)
def login_artisan(contact_number: str, db: Session = Depends(get_db)):
    artisan = db.query(models.Artisan).filter(models.Artisan.contact_number == contact_number).first()
    if not artisan:
        raise HTTPException(
            status_code=404,
            detail="Artisan profile not found. Please register."
        )
    return artisan


@app.get("/api/artisan/{artisan_id}", response_model=schemas.ArtisanResponse)
def get_artisan_profile(artisan_id: int, db: Session = Depends(get_db)):
    artisan = db.query(models.Artisan).filter(models.Artisan.id == artisan_id).first()
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan profile not found")
    return artisan


@app.get("/api/artisans", response_model=List[schemas.ArtisanResponse])
def list_all_artisans(db: Session = Depends(get_db)):
    return db.query(models.Artisan).all()


# Seeding demo data or resetting to fresh demo state
@app.post("/api/system/seed")
def seed_demo_data(force: bool = False, db: Session = Depends(get_db)):
    # If not forcing and data exists, skip
    if not force and db.query(models.Artisan).count() > 0:
        return {"message": "Database already has data. Use force=True to reset."}

    # Clear existing demo products, transactions, and pools if force is requested
    if force:
        db.query(models.KhataTransaction).delete()
        db.query(models.Product).delete()
        db.query(models.LogisticsPool).delete()
        db.commit()

    # Get or create dummy artisan
    artisan1 = db.query(models.Artisan).filter(models.Artisan.contact_number == "9876543210").first()
    if not artisan1:
        artisan1 = models.Artisan(
            name="Ramesh Prasad",
            contact_number="9876543210",
            state="Rajasthan",
            language="Hindi",
            pin_code="302001"
        )
        db.add(artisan1)
        db.commit()
        db.refresh(artisan1)

    # Add mock products: One already listed, others in Draft ready for "List ONDC" action
    p1 = models.Product(
        title="Handcrafted Jaipur Ceramic Pot",
        description="Beautiful blue pottery ceramic pot painted by hand. Direct from Jaipur craftsmen. Eco-friendly organic paint.",
        raw_description="मैंने जयपुर में अपने हाथों से नीली मिट्टी का मटका बनाया है, इस पर सुंदर कलाकारी की है।",
        base_price=300.0,
        dynamic_price=350.0,
        category="Handcrafted Pottery & Earthenware",
        hsn_code="69120010",
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Blue_pottery_from_Jaipur_2.jpg/800px-Blue_pottery_from_Jaipur_2.jpg",
        original_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Potter_at_work%2C_Jaura%2C_India.jpg/800px-Potter_at_work%2C_Jaura%2C_India.jpg",
        status="Listed_ONDC",
        artisan_id=artisan1.id
    )
    p2 = models.Product(
        title="Organic Bamboo Basket",
        description="Premium quality storage container made of natural splits. Fully recyclable and organic storage solution.",
        raw_description="बांस की टोकरी हाथ से बुनी गई है, घर के सामान रखने के लिए बहुत मजबूत है।",
        base_price=200.0,
        dynamic_price=240.0,
        category="Bamboo & Cane Crafts",
        hsn_code="46021100",
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Bamboo_basket%2C_Lakhimpur.jpg/800px-Bamboo_basket%2C_Lakhimpur.jpg",
        original_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Bamboo_basket%2C_Lakhimpur.jpg/800px-Bamboo_basket%2C_Lakhimpur.jpg",
        status="Draft",  # Ready for "List ONDC" demonstration
        artisan_id=artisan1.id
    )
    p3 = models.Product(
        title="Traditional Hand-Cast Brass Ganesha Idol",
        description="A magnificent hand-cast brass Ganesha idol, crafted using the lost-wax casting technique. Features detailed traditional engravings.",
        raw_description="पारंपरिक पीतल की गणेश जी की मूर्ति, हाथ से ढलाई और नक्काशी की गई।",
        base_price=1100.0,
        dynamic_price=1250.0,
        category="Metal Art & Brassware",
        hsn_code="83062920",
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Four-armed_Ganesha_-_Brass_-_Circa_20th_Century_CE_-_Madhya_Pradesh_-_ACCN_2000-53_-_Indian_Museum_-_Kolkata_2015-09-26_3997.JPG/800px-Four-armed_Ganesha_-_Brass_-_Circa_20th_Century_CE_-_Madhya_Pradesh_-_ACCN_2000-53_-_Indian_Museum_-_Kolkata_2015-09-26_3997.JPG",
        original_image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Four-armed_Ganesha_-_Brass_-_Circa_20th_Century_CE_-_Madhya_Pradesh_-_ACCN_2000-53_-_Indian_Museum_-_Kolkata_2015-09-26_3997.JPG/800px-Four-armed_Ganesha_-_Brass_-_Circa_20th_Century_CE_-_Madhya_Pradesh_-_ACCN_2000-53_-_Indian_Museum_-_Kolkata_2015-09-26_3997.JPG",
        status="Draft",  # Ready for "List ONDC" demonstration
        artisan_id=artisan1.id
    )
    db.add_all([p1, p2, p3])

    # Add mock khata transactions
    tx1 = models.KhataTransaction(
        type="SALE",
        amount=350.0,
        details="Sold Ceramic Pot on ONDC",
        artisan_id=artisan1.id
    )
    tx2 = models.KhataTransaction(
        type="EXPENSE",
        amount=80.0,
        details="Bought clay raw materials",
        artisan_id=artisan1.id
    )
    db.add_all([tx1, tx2])

    # Seed mock logistics pools
    pool1 = models.LogisticsPool(
        village_name="Jaipur Artisan Cluster",
        pincode="302001",
        status="Collecting",
        total_weight=4.5,
        orders_count=3
    )
    db.add(pool1)
    
    db.commit()
    return {"message": "Demo data successfully initialized with ready-to-list Draft products."}
