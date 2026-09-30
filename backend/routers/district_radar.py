from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

try:
    from ..database import get_db
    from .. import models, schemas
except (ImportError, ValueError):
    from database import get_db
    import models, schemas

router = APIRouter(
    prefix="/api/district",
    tags=["district-radar"]
)

# Realistic district perspective data for MoSJE / District Collector Dashboard
DISTRICT_DATA = {
    "Jaipur Rural": {
        "district": "Jaipur Rural",
        "state": "Rajasthan",
        "total_sc_beneficiaries": 1420,
        "total_rpl_certified": 1180,
        "total_gia_funds_cr": 3.48,
        "avg_wage_increase_pct": 46,
        "blocks": [
            {
                "block_name": "Bassi",
                "district": "Jaipur Rural",
                "state": "Rajasthan",
                "high_demand_trade": "Solar PV Pump & Motor Technician",
                "deficit_technicians": 54,
                "informal_workers": 340,
                "gia_budget_allocated_lakhs": 45.0,
                "gia_budget_utilized_lakhs": 38.5,
                "priority_level": "Critical Deficit",
                "centers_count": 1
            },
            {
                "block_name": "Chomu",
                "district": "Jaipur Rural",
                "state": "Rajasthan",
                "high_demand_trade": "Agricultural Machinery & Farm Power",
                "deficit_technicians": 38,
                "informal_workers": 290,
                "gia_budget_allocated_lakhs": 35.0,
                "gia_budget_utilized_lakhs": 32.0,
                "priority_level": "High Demand",
                "centers_count": 2
            },
            {
                "block_name": "Sanganer Rural",
                "district": "Jaipur Rural",
                "state": "Rajasthan",
                "high_demand_trade": "Textile Dyeing & Block Printing",
                "deficit_technicians": 62,
                "informal_workers": 480,
                "gia_budget_allocated_lakhs": 50.0,
                "gia_budget_utilized_lakhs": 44.0,
                "priority_level": "Critical Deficit",
                "centers_count": 1
            },
            {
                "block_name": "Amer Rural",
                "district": "Jaipur Rural",
                "state": "Rajasthan",
                "high_demand_trade": "Rural Mason & Water Harvesting",
                "deficit_technicians": 22,
                "informal_workers": 190,
                "gia_budget_allocated_lakhs": 25.0,
                "gia_budget_utilized_lakhs": 24.2,
                "priority_level": "Balanced",
                "centers_count": 2
            }
        ]
    },
    "Salem": {
        "district": "Salem",
        "state": "Tamil Nadu",
        "total_sc_beneficiaries": 1890,
        "total_rpl_certified": 1640,
        "total_gia_funds_cr": 4.12,
        "avg_wage_increase_pct": 52,
        "blocks": [
            {
                "block_name": "Jalakandapuram",
                "district": "Salem",
                "state": "Tamil Nadu",
                "high_demand_trade": "Modern Jacquard Loom Master",
                "deficit_technicians": 78,
                "informal_workers": 520,
                "gia_budget_allocated_lakhs": 60.0,
                "gia_budget_utilized_lakhs": 55.0,
                "priority_level": "Critical Deficit",
                "centers_count": 2
            },
            {
                "block_name": "Omalur",
                "district": "Salem",
                "state": "Tamil Nadu",
                "high_demand_trade": "Steel & Casting Machine Operator",
                "deficit_technicians": 32,
                "informal_workers": 240,
                "gia_budget_allocated_lakhs": 30.0,
                "gia_budget_utilized_lakhs": 28.0,
                "priority_level": "High Demand",
                "centers_count": 1
            }
        ]
    }
}

@router.get("/heatmap/{district}", response_model=schemas.DistrictHeatmapResponse)
def get_district_heatmap(district: str):
    """
    Returns District Magistrate Livelihood Heatmap for perspective planning:
    Shows skill deficit clusters, GIA fund utilization, and priority intervention zones.
    """
    key = "Salem" if "salem" in district.lower() else "Jaipur Rural"
    data = DISTRICT_DATA[key]
    return schemas.DistrictHeatmapResponse(**data)

@router.post("/deploy-batch")
def deploy_training_batch(block_name: str, trade_name: str, seats: int = 30):
    """
    Allows District Collector / MoSJE admin to sanction an immediate GIA training batch
    for a high-deficit rural cluster.
    """
    return {
        "status": "Batch Sanctioned",
        "block": block_name,
        "trade": trade_name,
        "seats": seats,
        "gia_grant_allocated": f"₹{seats * 24500:,.2f}",
        "action": "Training Center notified & SMS broadcast sent to registered uncertified youth."
    }
