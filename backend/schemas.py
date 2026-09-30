from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==========================================================
# KAUSHAL SARATHI SCHEMAS
# ==========================================================

class VoiceCounselingRequest(BaseModel):
    voice_text: str  # Transcribed voice speech
    language: str = "hi"  # hi, ta, te, bn, bho, en
    beneficiary_name: Optional[str] = "Beneficiary"
    district: Optional[str] = "Jaipur Rural"
    state: Optional[str] = "Rajasthan"
    pincode: Optional[str] = "303007"
    age: Optional[int] = 21
    education: Optional[str] = "8th Standard"
    preferred_mode: Optional[str] = "Wage Employment"  # Wage Employment or Self-Employment

class SkillExtractionResult(BaseModel):
    extracted_skills: List[str]
    detected_trade: str
    qp_nos_code: str
    nsqf_level: int
    sector: str
    rpl_prior_years: float
    rpl_hours_credited: int
    confidence_score: float

class GIAEntitlementResult(BaseModel):
    scheme_name: str
    tuition_fee_waiver: float
    monthly_dbt_stipend: float
    stipend_duration_months: int
    free_toolkit_value: float
    toolkit_items: List[str]
    boarding_allowance: float
    total_grant_value: float
    status: str

class NearestTrainingCenter(BaseModel):
    center_name: str
    district: str
    distance_km: float
    trade_name: str
    qp_nos_code: str
    next_batch_date: str
    available_seats: int
    total_seats: int
    contact_phone: str

class LocalDemandSummary(BaseModel):
    district: str
    block_name: str
    trade_name: str
    hiring_index_pct: int
    local_vacancies: int
    unskilled_labor_pool: int
    infrastructure_drivers: str
    distance_radius_km: int = 15

class VoiceCounselingResponse(BaseModel):
    kaushal_id: str
    candidate_name: str
    input_transcript: str
    detected_language: str
    skill_assessment: SkillExtractionResult
    gia_entitlement: GIAEntitlementResult
    nearest_center: NearestTrainingCenter
    demand_radar: LocalDemandSummary
    audio_readout_text_hi: str  # Spoken response in Hindi
    audio_readout_text_en: str  # Spoken response in English
    qr_verification_hash: str
    whatsapp_share_text: str

class BeneficiaryCreate(BaseModel):
    name: str
    contact_number: str
    age: int
    gender: str
    category: str = "SC"
    village: str
    block: str
    district: str
    state: str
    pincode: str
    education_level: str
    preferred_language: str = "hi"

class BeneficiaryResponse(BeneficiaryCreate):
    id: int
    kaushal_id: str
    registered_at: datetime
    class Config:
        orm_mode = True

class DistrictHeatmapBlock(BaseModel):
    block_name: str
    district: str
    state: str
    high_demand_trade: str
    deficit_technicians: int
    informal_workers: int
    gia_budget_allocated_lakhs: float
    gia_budget_utilized_lakhs: float
    priority_level: str  # Critical Deficit, High Demand, Balanced
    centers_count: int

class DistrictHeatmapResponse(BaseModel):
    district: str
    state: str
    total_sc_beneficiaries: int
    total_rpl_certified: int
    total_gia_funds_cr: float
    avg_wage_increase_pct: int
    blocks: List[DistrictHeatmapBlock]


