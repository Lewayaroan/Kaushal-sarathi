from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
import datetime

try:
    from .database import Base
except (ImportError, ValueError):
    from database import Base

# ==========================================================
# KAUSHAL SARATHI - MoSJE PM-AJAY GIA MODELS
# ==========================================================

class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    kaushal_id = Column(String, unique=True, index=True)  # e.g., KS-2026-RAJ-0942
    name = Column(String, index=True)
    contact_number = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    category = Column(String, default="SC")  # SC / PM-AJAY target group
    village = Column(String)
    block = Column(String)
    district = Column(String)
    state = Column(String)
    pincode = Column(String)
    education_level = Column(String)  # e.g., "8th Standard", "10th Standard", "No Formal Education"
    preferred_language = Column(String, default="hi")  # hi, ta, te, bn, bho, en
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)

    assessments = relationship("SkillAssessment", back_populates="beneficiary")
    entitlements = relationship("GIAEntitlement", back_populates="beneficiary")


class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    voice_transcript = Column(Text)  # Speech-to-text recorded dialect input
    detected_trade = Column(String)  # e.g., "Solar Water Pump & Motor Technician"
    qp_nos_code = Column(String)  # Official NSDC Code e.g., "QP-ELE/Q5801"
    nsqf_level = Column(Integer)  # 1 to 5
    sector = Column(String)  # e.g., "Green Energy & Electronics"
    rpl_prior_years = Column(Float, default=1.0)  # Recognition of Prior Learning experience
    rpl_hours_credited = Column(Integer, default=160)
    aspiration_type = Column(String, default="Wage Employment")  # Wage Employment vs Self-Employment
    mobility_constraint_km = Column(Integer, default=15)
    confidence_score = Column(Float, default=0.92)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    beneficiary = relationship("Beneficiary", back_populates="assessments")


class GIAEntitlement(Base):
    __tablename__ = "gia_entitlements"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    scheme_name = Column(String, default="PM-AJAY GIA Component")
    tuition_fee_waiver = Column(Float, default=14500.0)  # 100% Free Government Grant
    monthly_dbt_stipend = Column(Float, default=2500.0)  # Direct Benefit Transfer
    stipend_duration_months = Column(Integer, default=3)
    free_toolkit_value = Column(Float, default=10000.0)  # Free Equipment / Toolkit Grant
    toolkit_items = Column(String, default="Digital Multimeter, Heavy Toolbag, Insulated Plier Set, Safety Helmet")
    boarding_allowance = Column(Float, default=0.0)
    total_grant_value = Column(Float, default=24500.0)
    status = Column(String, default="Sanctioned / Pre-Approved")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    beneficiary = relationship("Beneficiary", back_populates="entitlements")


class TrainingCenter(Base):
    __tablename__ = "training_centers"

    id = Column(Integer, primary_key=True, index=True)
    center_name = Column(String)
    district = Column(String)
    state = Column(String)
    pincode = Column(String)
    trade_name = Column(String)
    qp_nos_code = Column(String)
    nsqf_level = Column(Integer)
    distance_km = Column(Float, default=8.0)
    next_batch_date = Column(String)
    total_seats = Column(Integer, default=30)
    available_seats = Column(Integer, default=12)
    accreditation = Column(String, default="MoSJE / NSDC Accredited Center")
    contact_phone = Column(String)


class DistrictLivelihoodDemand(Base):
    __tablename__ = "district_livelihood_demands"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String)
    block_name = Column(String)
    state = Column(String)
    trade_name = Column(String)
    nsqf_level = Column(Integer)
    current_vacancies = Column(Integer, default=45)
    unskilled_labor_pool = Column(Integer, default=320)
    local_infrastructure_link = Column(String)  # e.g., "45 Solar Water Pumps under PM-KUSUM"
    hiring_index_pct = Column(Integer, default=94)
    priority_level = Column(String, default="Critical Deficit")  # Critical Deficit, High Demand, Balanced
