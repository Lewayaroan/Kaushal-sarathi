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
    from .routers import counseling, district_radar
except (ImportError, ValueError):
    from database import engine, Base, get_db
    import models, schemas
    from routers import counseling, district_radar

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kaushal Sarathi: AI Voice Assistant for Rural Skilling & PM-AJAY Livelihood Mapping",
    description="Ministry of Social Justice and Empowerment (MoSJE) - PM-AJAY Grant-in-Aid (GIA) Component",
    version="2.0.0"
)

# Configure CORS for local frontend SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(counseling.router)
app.include_router(district_radar.router)

@app.get("/")
def health_check():
    return {
        "status": "Healthy",
        "project": "Kaushal Sarathi",
        "ministry": "Ministry of Social Justice and Empowerment (MoSJE)",
        "scheme": "PM-AJAY Grant-in-Aid (GIA) Component",
        "api_documentation": "/docs"
    }

# Seeding demo data or resetting to fresh demo state
@app.post("/api/system/seed")
def seed_demo_data(force: bool = False, db: Session = Depends(get_db)):
    """Seeds both Kaushal Sarathi and legacy data if requested"""
    try:
        # Check if already seeded
        if not force and db.query(models.Beneficiary).count() > 0:
            return {"message": "Database already seeded. Use force=True to reset."}

        # Clear existing beneficiaries if force
        if force:
            db.query(models.SkillAssessment).delete()
            db.query(models.GIAEntitlement).delete()
            db.query(models.Beneficiary).delete()
            db.query(models.TrainingCenter).delete()
            db.query(models.DistrictLivelihoodDemand).delete()
            db.commit()

        # Seed sample beneficiary
        sample_ben = models.Beneficiary(
            kaushal_id="KS-2026-RAJ-0942",
            name="Ravi Kumar",
            contact_number="+91-9876543210",
            age=20,
            gender="Male",
            category="SC",
            village="Bassi",
            block="Bassi",
            district="Jaipur Rural",
            state="Rajasthan",
            pincode="303301",
            education_level="8th Standard",
            preferred_language="hi"
        )
        db.add(sample_ben)
        db.commit()
        db.refresh(sample_ben)

        # Seed skill assessment
        sample_assessment = models.SkillAssessment(
            beneficiary_id=sample_ben.id,
            voice_transcript="मैंने 8वीं तक पढ़ाई की है। मेरे गांव में मैं पानी के मोटर और बिजली के तार ठीक करने में चाचा की मदद करता हूँ।",
            detected_trade="Solar PV Water Pump & Motor Technician",
            qp_nos_code="QP-ELE/Q5801",
            nsqf_level=3,
            sector="Green Energy & Electrical",
            rpl_prior_years=2.0,
            rpl_hours_credited=160,
            aspiration_type="Wage Employment",
            mobility_constraint_km=15,
            confidence_score=0.94
        )
        db.add(sample_assessment)

        # Seed GIA Entitlement
        sample_entitlement = models.GIAEntitlement(
            beneficiary_id=sample_ben.id,
            scheme_name="PM-AJAY GIA Component",
            tuition_fee_waiver=14500.0,
            monthly_dbt_stipend=2500.0,
            stipend_duration_months=3,
            free_toolkit_value=10000.0,
            toolkit_items="Digital Multimeter, Heavy Toolbag, Insulated Plier Set, Safety Helmet",
            total_grant_value=24500.0,
            status="Sanctioned / Pre-Approved"
        )
        db.add(sample_entitlement)

        # Seed Training Center
        sample_center = models.TrainingCenter(
            center_name="Jaipur Rural PM-AJAY Skill Development Center",
            district="Jaipur Rural",
            state="Rajasthan",
            pincode="303301",
            trade_name="Solar PV Water Pump & Motor Technician",
            qp_nos_code="QP-ELE/Q5801",
            nsqf_level=3,
            distance_km=7.8,
            next_batch_date="October 15, 2026",
            total_seats=30,
            available_seats=12,
            contact_phone="+91-1800-180-2026"
        )
        db.add(sample_center)

        # Seed District Demand
        sample_demand = models.DistrictLivelihoodDemand(
            district="Jaipur Rural",
            block_name="Bassi",
            state="Rajasthan",
            trade_name="Solar PV Water Pump & Motor Technician",
            nsqf_level=3,
            current_vacancies=54,
            unskilled_labor_pool=340,
            local_infrastructure_link="45 Solar Water Pumps under PM-KUSUM; 0 certified technicians nearby.",
            hiring_index_pct=94,
            priority_level="Critical Deficit"
        )
        db.add(sample_demand)
        db.commit()

        return {
            "status": "Success",
            "message": "Kaushal Sarathi demo data seeded successfully!",
            "demo_candidate": "Ravi Kumar (KS-2026-RAJ-0942)",
            "trade": "Solar PV Water Pump & Motor Technician (NSQF Level 3)",
            "grant_value": "₹24,500"
        }
    except Exception as e:
        db.rollback()
        return {"status": "Error", "message": str(e)}
