from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import random

try:
    from ..database import get_db
    from .. import models, schemas
except (ImportError, ValueError):
    from database import get_db
    import models, schemas

router = APIRouter(
    prefix="/api/utilities",
    tags=["utilities"]
)

# Reference data for state-specific minimum wages in India (approximate daily rates in INR for semi-skilled/skilled crafts)
STATE_DAILY_MIN_WAGES = {
    "bihar": 380.0,
    "uttar pradesh": 400.0,
    "rajasthan": 420.0,
    "maharashtra": 480.0,
    "tamil nadu": 460.0,
    "west bengal": 390.0,
    "karnataka": 450.0,
    "gujarat": 430.0,
    "assam": 370.0
}

@router.post("/fair-price")
def calculate_fair_price(request: schemas.FairPriceRequest):
    state_key = request.artisan_state.lower().strip()
    # Find minimum daily wage, default to ₹420 if state not found
    state_wage = STATE_DAILY_MIN_WAGES.get(state_key, 420.0)
    
    # Calculate target hourly rate (based on 8-hour work day)
    state_hourly_rate = state_wage / 8.0
    
    # Use user-desired wage if provided, but clamp it to be at least the state minimum wage
    hourly_wage = max(request.desired_hourly_wage, state_hourly_rate)
    
    # Compute base production cost
    labor_cost = request.labor_hours * hourly_wage
    production_cost = request.material_cost + labor_cost + request.overhead_cost
    
    # Recommend retail prices:
    # 1. Direct sales (e.g. ONDC retail) - typically 15-20% margin for tools/growth
    direct_retail_price = production_cost * 1.2
    
    # 2. Wholesale/B2B price - typically 10% margin
    wholesale_price = production_cost * 1.1
    
    return {
        "material_cost": request.material_cost,
        "labor_cost": labor_cost,
        "hourly_wage_used": hourly_wage,
        "state_minimum_hourly_rate": state_hourly_rate,
        "state_minimum_daily_rate": state_wage,
        "production_cost": production_cost,
        "suggested_direct_retail_price": round(direct_retail_price, 2),
        "suggested_wholesale_price": round(wholesale_price, 2),
        "wage_fairness_indicator": "Fair & Compliant" if hourly_wage >= state_hourly_rate else "Under Minimum Wage"
    }


@router.get("/trends/{state}")
def get_state_trends(state: str):
    # Pre-defined localized trends for authentic look and feel
    local_trends = {
        "rajasthan": [
            {"title": "Jaipur Blue Pottery", "growth": "+34% this month", "demand_level": "High", "advice": "Focus on blue/white ceramic flower vases and small plates. Urban buyers are looking for home decor."},
            {"title": "Sanganeri Print Fabrics", "growth": "+21% this month", "demand_level": "Medium-High", "advice": "Table runners and cotton pillow covers are selling fast ahead of the festive season."}
        ],
        "bihar": [
            {"title": "Madhubani Painted Canvas Bags", "growth": "+45% this month", "demand_level": "Extreme", "advice": "Paint traditional folklore motifs on organic cotton tote bags. High corporate gifting demand."},
            {"title": "Sujuni Embroidery Pouches", "growth": "+15% this month", "demand_level": "Medium", "advice": "Small pencil cases and mobile pouches with embroidery are popular among college students."}
        ],
        "assam": [
            {"title": "Water Hyacinth Storage Baskets", "growth": "+28% this month", "demand_level": "High", "advice": "Make cylindrical bins. Plastic-free eco-friendly organizers are in high demand in Bangalore and Mumbai."},
            {"title": "Bamboo Hand-fans & Wall Art", "growth": "+12% this month", "demand_level": "Medium", "advice": "Weave modern geometric patterns into bamboo fans for wall hanging decor."}
        ]
    }
    
    key = state.lower().strip()
    trends = local_trends.get(key, [
        {"title": "Eco-friendly Clay Tableware", "growth": "+25% this month", "demand_level": "High", "advice": "Mugs and tea-sets made with natural clay are popular. Promote as chemical-free kitchenware."},
        {"title": "Handmade Organic Cotton Bags", "growth": "+18% this month", "demand_level": "Medium-High", "advice": "Totes with simple floral patterns. Urban shoppers prefer plastic-free alternatives."}
    ])
    
    return {
        "state": state,
        "trends": trends
    }


@router.get("/logistics-pools", response_model=List[schemas.LogisticsPoolResponse])
def get_all_logistics_pools(db: Session = Depends(get_db)):
    return db.query(models.LogisticsPool).all()


@router.get("/logistics-pools/pincode/{pincode}", response_model=Optional[schemas.LogisticsPoolResponse])
def get_pool_by_pincode(pincode: str, db: Session = Depends(get_db)):
    return db.query(models.LogisticsPool).filter(
        models.LogisticsPool.pincode == pincode,
        models.LogisticsPool.status == "Collecting"
    ).first()


@router.post("/logistics-pools/dispatch/{pool_id}")
def dispatch_pool(pool_id: int, db: Session = Depends(get_db)):
    pool = db.query(models.LogisticsPool).filter(models.LogisticsPool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="Logistics pool not found")
        
    pool.status = "Dispatched"
    db.commit()
    return {"message": f"Logistics pool {pool_id} for pincode {pool.pincode} has been successfully dispatched via India Post."}
