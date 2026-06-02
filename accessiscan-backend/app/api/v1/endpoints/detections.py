"""
DETECTION OBSERVATION COMPLIANCE EDGE INTERFACE
---------------------------------------------------------------------
Purpose:
    Exposes granular resource management endpoints for individual computer 
    vision observations. Acts as the network gateway for isolating, 
    persisting, and auditing micro-level asset findings.

Architecture:
    1. Routing Encapsulation: Isolates detection metrics from session scopes.
    2. Data Integrity: Enforces schema validation at the application boundary 
       to prevent corrupt telemetry from entering the persistent layer.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.detection import Detection

# --- 1. ROUTER INITIALIZATION ---
# Purpose: Registers the detection-specific API router.
router = APIRouter()

# --- 2. RELATIONAL PERSISTENCE ENGINE (CREATE) ---
# Purpose: Handles the ingestion of validated telemetry records. Implements 
# rollback protection to maintain absolute relational database integrity.
@router.post("/", response_model=Detection, status_code=201)
def create_detection_entry(detection_data: Detection, session: Session = Depends(get_session)):
    """Accepts and persists a validated computer vision telemetry record."""
    try:
        session.add(detection_data)
        session.commit()
        session.refresh(detection_data)
        return detection_data
    except Exception as db_error:
        # Rollback ensures atomic transaction consistency in case of failure.
        session.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Database Integrity Violation: Failure writing detection node. {str(db_error)}"
        )

# --- 3. RELATIONAL RETRIEVAL COMPLEX (READ) ---
# Purpose: Facilitates the extraction of historical observation data, 
# providing the audit trail required for global platform reporting.
@router.get("/", response_model=List[Detection])
def get_detections_list(session: Session = Depends(get_session)):
    """Extracts a global registry of object metrics tracked across all inspection runs."""
    detections = session.exec(select(Detection)).all()
    return detections