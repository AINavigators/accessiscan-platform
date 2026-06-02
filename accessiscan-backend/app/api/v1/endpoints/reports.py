"""
COMPLIANCE REPORT DELIVERY, COMPILATION & GENERATION ROUTER
------------------------------------------------------------
Purpose:
    Exposes API interfaces for querying compliance records, streaming JSON 
    ledgers, and programmatically generating print-ready PDF certificates.

Architecture:
    1. Metadata Layer: Fetches and validates report states via SQLModel.
    2. Artifact Transport: Streams raw JSON ledgers directly from AI storage.
    3. Document Engine: Translates database relations into formal PDF reports 
       with defensive fallback capabilities.
"""

import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.report import Report
from app.models.inspection import Inspection
from app.models.detection import Detection

# --- 1. CONFIGURATION & PATH COMPUTATION ---
# Purpose: Define absolute filesystem anchors for the application, ensuring 
# reliable access to AI storage arrays regardless of the host environment.
router = APIRouter()
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
AI_ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, "..", "accessiscan-ai-1"))
AUDIT_RESULTS_DIR = os.path.normpath(os.path.join(AI_ROOT, "runs", "detect", "audit_results"))

# --- 2. DOCUMENT COMPILATION ENGINE ---
# Purpose: Execute the conversion of relational data into audit documentation. 
# Implements a defensive fallback mechanism to ensure documentation delivery 
# if specialized compilers are unavailable.
def compile_pdf_document(output_path: str, report_node: Report, inspection_node: Inspection):
    """Orchestrates PDF generation with graceful fallback to plaintext."""
    try:
        from app.utils.pdf_generator import generate_pdf_report
        generate_pdf_report(output_path, report_node, inspection_node)
    except ImportError:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"--- DSAPT COMPLIANCE CERTIFICATE: {report_node.id} ---\n")
            f.write(f"Station: {inspection_node.site_name}\n")
            f.write(f"Status: {report_node.status}\n")

# --- 3. COMPLIANCE REPORT GENERATION ---
# Purpose: Validate inspection status and generate a unified report, 
# ensuring record integrity before committing to the compliance registry.
@router.post("/generate/{inspection_id}", response_model=Report, status_code=201)
def generate_compliance_report(inspection_id: int, session: Session = Depends(get_session)):
    """Registers a new report entity based on validated inspection outcomes."""
    inspection = session.get(Inspection, inspection_id)
    if not inspection or inspection.status != "completed":
        raise HTTPException(status_code=400, detail="Invalid inspection status.")

    detections = session.exec(select(Detection).where(Detection.inspection_id == inspection_id)).all()
    status = "Non-Compliant" if any(d.status != "Compliant" for d in detections) else "Compliant"

    new_report = Report(
        inspection_id=inspection_id,
        generated_at=datetime.utcnow(),
        status=status,
        summary=f"Audit completed with {len([d for d in detections if d.status != 'Compliant'])} exceptions."
    )
    
    session.add(new_report)
    session.commit()
    session.refresh(new_report)
    return new_report

# --- 4. DATA ARTIFACT TRANSPORT ---
# Purpose: Provide a secure channel for streaming computational JSON ledgers 
# while abstracting physical storage paths from the end client.
@router.get("/download-json/{report_id}")
def download_json_report(report_id: int, session: Session = Depends(get_session)):
    """Streams the raw AI JSON audit ledger."""
    report = session.get(Report, report_id)
    if not report or not os.path.exists(AUDIT_RESULTS_DIR):
        raise HTTPException(status_code=404, detail="Resource not found.")

    target_file = next((f for f in os.listdir(AUDIT_RESULTS_DIR) if f.startswith("report_")), None)
    if not target_file:
        raise HTTPException(status_code=404, detail="Physical ledger missing.")
        
    return FileResponse(path=os.path.join(AUDIT_RESULTS_DIR, target_file), media_type="application/json")

# --- 5. PDF CERTIFICATE EXPORT ---
# Purpose: Reconcile relational metadata with structural templates for 
# just-in-time compilation of print-ready audit certificates.
@router.get("/download-pdf/{report_id}")
def download_pdf_report(report_id: int, session: Session = Depends(get_session)):
    """Compiles and transmits a print-ready PDF certificate for the user."""
    report = session.get(Report, report_id)
    inspection = session.get(Inspection, report.inspection_id)
    
    pdf_path = os.path.normpath(os.path.join(AUDIT_RESULTS_DIR, f"DSAPT_Report_{report_id}.pdf"))
    compile_pdf_document(pdf_path, report, inspection)
    
    return FileResponse(path=pdf_path, media_type="application/pdf")