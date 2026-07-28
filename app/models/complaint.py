"""
Database Models for Complaint Management System
backend/app/models/complaint.py
All long text fields changed from String(255) to Text
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class SeverityLevel(str, enum.Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"

class ComplaintStatus(str, enum.Enum):
    DRAFT = "Draft"
    READY_TO_COMMIT = "Ready to Commit"
    COMMITTED = "Committed"
    INVESTIGATION_IN_PROGRESS = "Investigation In Progress"
    RESOLVED = "Resolved"

class Complaint(Base):
    __tablename__ = "complaints"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # ====== ORIGIN & CUSTOMER DETAILS ======
    complaint_source = Column(String(100), nullable=True)
    customer_name = Column(String(255), nullable=True)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(20), nullable=True)

    # ====== PRODUCT & BATCH IDENTIFICATION ======
    product_name = Column(String(255), nullable=True)
    product_strength_grade = Column(String(100), nullable=True)
    batch_number = Column(String(100), nullable=True)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    affected_quantity = Column(String(100), nullable=True)

    # ====== FACILITY & MATERIAL IMPACT ======
    originating_site_block = Column(String(255), nullable=True)
    impacted_non_product_materials = Column(String(255), nullable=True)

    # ====== COMPLAINT DETAILS ======
    complaint_category = Column(String(255), nullable=True)
    complaint_description = Column(Text, nullable=True)  # Changed to Text
    detailed_complaint_description = Column(Text, nullable=True)  # Already Text

    # ====== DEFECT ANALYSIS & RISK ASSESSMENT ======
    structured_defect_summary = Column(Text, nullable=True)  # Changed to Text
    severity_level = Column(Enum(SeverityLevel), default=SeverityLevel.MINOR)
    priority = Column(String(50), nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)  # Changed to Text
    suggested_next_action = Column(Text, nullable=True)  # Changed to Text

    # ====== CONVERSATION HISTORY & METADATA ======
    conversation_history = Column(JSON, default=list)
    extracted_document_name = Column(String(255), nullable=True)
    
    # Status tracking
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.DRAFT)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    committed_at = Column(DateTime, nullable=True)

    # AI confidence scores
    extraction_confidence = Column(JSON, default=dict)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "complaint_source": self.complaint_source,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "product_name": self.product_name,
            "product_strength_grade": self.product_strength_grade,
            "batch_number": self.batch_number,
            "manufacturing_date": self.manufacturing_date,
            "expiry_date": self.expiry_date,
            "affected_quantity": self.affected_quantity,
            "originating_site_block": self.originating_site_block,
            "impacted_non_product_materials": self.impacted_non_product_materials,
            "complaint_category": self.complaint_category,
            "complaint_description": self.complaint_description,
            "detailed_complaint_description": self.detailed_complaint_description,
            "structured_defect_summary": self.structured_defect_summary,
            "severity_level": self.severity_level,
            "priority": self.priority,
            "initial_risk_assessment": self.initial_risk_assessment,
            "suggested_next_action": self.suggested_next_action,
            "status": self.status,
            "conversation_history": self.conversation_history,
            "extracted_document_name": self.extracted_document_name,
            "extraction_confidence": self.extraction_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }