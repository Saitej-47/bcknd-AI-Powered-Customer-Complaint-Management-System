"""
FastAPI routes for Complaint Management
backend/app/routes/complaint.py
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.agents.complaint_agent import process_complaint_text
from app.services.document_extractor import extract_text_from_document

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

# ========== PYDANTIC SCHEMAS ==========

class ComplaintCreateRequest(BaseModel):
    """Request to create/process a complaint from text"""
    text: str
    source: Optional[str] = "Chat"

class ComplaintRefineRequest(BaseModel):
    """Request to refine an existing complaint"""
    complaint_id: int
    refinement_message: str

class ComplaintCommitRequest(BaseModel):
    """Request to commit a complaint to QMS"""
    complaint_id: int

class ComplaintResponse(BaseModel):
    """Response with complaint data"""
    id: Optional[int]
    complaint_source: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    product_name: Optional[str]
    product_strength_grade: Optional[str]
    batch_number: Optional[str]
    manufacturing_date: Optional[str]
    expiry_date: Optional[str]
    affected_quantity: Optional[str]
    complaint_category: Optional[str]
    complaint_description: Optional[str]
    detailed_complaint_description: Optional[str]
    structured_defect_summary: Optional[str]
    severity_level: Optional[str]
    priority: Optional[str]
    initial_risk_assessment: Optional[str]
    suggested_next_action: Optional[str]
    status: Optional[str]
    conversation_history: Optional[List[Dict]]
    extracted_document_name: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

# ========== ENDPOINTS ==========

@router.post("/process-text", response_model=ComplaintResponse)
async def process_complaint_from_text(
    request: ComplaintCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Process a complaint from plain text input
    
    Example:
    {
        "text": "Apollo Pharmacy reported discolored capsules...",
        "source": "Email"
    }
    """
    try:
        # Run LangGraph agent
        result = process_complaint_text(request.text)
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        complaint_data = result.get("final_complaint", {})
        
        # Create database record
        complaint = Complaint(
            complaint_source=request.source or complaint_data.get("complaint_source"),
            customer_name=complaint_data.get("customer_name"),
            customer_email=complaint_data.get("customer_email"),
            customer_phone=complaint_data.get("customer_phone"),
            product_name=complaint_data.get("product_name"),
            product_strength_grade=complaint_data.get("product_strength_grade"),
            batch_number=complaint_data.get("batch_number"),
            manufacturing_date=complaint_data.get("manufacturing_date"),
            expiry_date=complaint_data.get("expiry_date"),
            affected_quantity=complaint_data.get("affected_quantity"),
            originating_site_block=complaint_data.get("originating_site_block"),
            impacted_non_product_materials=complaint_data.get("impacted_non_product_materials"),
            complaint_category=complaint_data.get("complaint_category"),
            complaint_description=complaint_data.get("complaint_description"),
            detailed_complaint_description=complaint_data.get("detailed_complaint_description"),
            structured_defect_summary=complaint_data.get("structured_defect_summary"),
            severity_level=complaint_data.get("severity_level", "Minor"),
            priority=complaint_data.get("priority"),
            initial_risk_assessment=complaint_data.get("initial_risk_assessment"),
            suggested_next_action=complaint_data.get("suggested_next_action"),
            status=ComplaintStatus.READY_TO_COMMIT,
            conversation_history=[
                {"role": "user", "content": request.text, "timestamp": datetime.utcnow().isoformat()}
            ]
        )
        
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        
        return complaint.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing complaint: {str(e)}")

@router.post("/process-document", response_model=ComplaintResponse)
async def process_complaint_from_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a complaint from PDF, DOCX, TXT, or EML file
    """
    try:
        # Read file
        file_content = await file.read()
        
        # Extract text
        text, success = extract_text_from_document(file_content, file.filename)
        
        if not success:
            raise HTTPException(status_code=400, detail=text)
        
        # Process through agent
        result = process_complaint_text(text)
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        complaint_data = result.get("final_complaint", {})
        
        # Create database record
        complaint = Complaint(
            complaint_source="Document Upload",
            customer_name=complaint_data.get("customer_name"),
            customer_email=complaint_data.get("customer_email"),
            customer_phone=complaint_data.get("customer_phone"),
            product_name=complaint_data.get("product_name"),
            product_strength_grade=complaint_data.get("product_strength_grade"),
            batch_number=complaint_data.get("batch_number"),
            manufacturing_date=complaint_data.get("manufacturing_date"),
            expiry_date=complaint_data.get("expiry_date"),
            affected_quantity=complaint_data.get("affected_quantity"),
            originating_site_block=complaint_data.get("originating_site_block"),
            impacted_non_product_materials=complaint_data.get("impacted_non_product_materials"),
            complaint_category=complaint_data.get("complaint_category"),
            complaint_description=complaint_data.get("complaint_description"),
            detailed_complaint_description=complaint_data.get("detailed_complaint_description"),
            structured_defect_summary=complaint_data.get("structured_defect_summary"),
            severity_level=complaint_data.get("severity_level", "Minor"),
            priority=complaint_data.get("priority"),
            initial_risk_assessment=complaint_data.get("initial_risk_assessment"),
            suggested_next_action=complaint_data.get("suggested_next_action"),
            status=ComplaintStatus.READY_TO_COMMIT,
            extracted_document_name=file.filename,
            conversation_history=[
                {
                    "role": "system",
                    "content": f"Document uploaded: {file.filename}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        )
        
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        
        return complaint.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/refine", response_model=ComplaintResponse)
async def refine_complaint(
    request: ComplaintRefineRequest,
    db: Session = Depends(get_db)
):
    """
    Refine an existing complaint with user feedback
    
    Example:
    {
        "complaint_id": 1,
        "refinement_message": "ah sorry the batch number is BMX240602 and affected quantity is 48 capsules"
    }
    """
    try:
        # Fetch complaint from DB
        complaint = db.query(Complaint).filter(Complaint.id == request.complaint_id).first()
        
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Add refinement to conversation history
        if not complaint.conversation_history:
            complaint.conversation_history = []
        
        complaint.conversation_history.append({
            "role": "user",
            "content": request.refinement_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Prepare current data as JSON
        current_state_str = complaint.to_dict()
        
        # Re-run agent with refinement
        result = process_complaint_text(
            text=request.refinement_message,
            refinements=complaint.conversation_history
        )
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        refined_data = result.get("final_complaint", {})
        
        # Update complaint with refined data
        for key, value in refined_data.items():
            if hasattr(complaint, key):
                setattr(complaint, key, value)
        
        complaint.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(complaint)
        
        return complaint.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error refining complaint: {str(e)}")

@router.post("/commit")
async def commit_complaint(
    request: ComplaintCommitRequest,
    db: Session = Depends(get_db)
):
    """
    Commit a complaint to QMS Ledger
    """
    try:
        complaint = db.query(Complaint).filter(Complaint.id == request.complaint_id).first()
        
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        complaint.status = ComplaintStatus.COMMITTED
        complaint.committed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Complaint {request.complaint_id} committed to QMS",
            "committed_at": complaint.committed_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error committing complaint: {str(e)}")

@router.get("/list")
async def list_complaints(db: Session = Depends(get_db)):
    """
    Get list of all complaints
    """
    try:
        complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
        return [c.to_dict() for c in complaints]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching complaints: {str(e)}")

@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """
    Get a specific complaint by ID
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return complaint.to_dict()

@router.delete("/{complaint_id}")
async def delete_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """
    Delete a complaint (draft only)
    """
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        if complaint.status != ComplaintStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Can only delete draft complaints")
        
        db.delete(complaint)
        db.commit()
        
        return {"success": True, "message": f"Complaint {complaint_id} deleted"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting complaint: {str(e)}")