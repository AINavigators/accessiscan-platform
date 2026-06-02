"""
INSPECTION PROMOTION, VALIDATION, AND ASYNC PROCESSING ROUTER
------------------------------------------------------------------------
Purpose:
    Manages the lifecycle of transit asset inspections. Acts as a secure 
    gatekeeper for the AI inference pipeline, ensuring incoming payloads 
    comply with DSAPT evaluation criteria.

Architecture:
    1. Validation: Filters payloads via file-extension whitelisting.
    2. Audit: Provisions relational database anchors for tracking.
    3. Asynchronous Execution: Offloads CV inference via background workers 
       to maintain high API throughput.
"""

import os
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlmodel import Session, select
from ultralytics import YOLO
from app.db.session import get_session, engine
from app.models.inspection import Inspection
from app.models.detection import Detection

# --- 1. CONFIGURATION & GATEWAYS ---
# Purpose: Initialize the router and storage layout. Ensures the file 
# system is prepared for image ingestion.
router = APIRouter()
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
os.makedirs("data/images/uploads/", exist_ok=True)
os.makedirs("data/images/detections/", exist_ok=True)

# --- 2. VALIDATION LOGIC ---
# Purpose: Implements a defensive gatekeeper to enforce network boundary 
# integrity through strict file-extension whitelisting.
def validate_file_extension(filename: str) -> None:
    """Enforces strict media type validation for incoming uploads."""
    ext = filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Invalid media type.")
    
# --- 3. BACKGROUND INFERENCE WORKER ---
# Purpose: Executes detached CV tasks. This keeps the API responsive 
# by offloading model inference from the main request/response cycle.
def background_inference_worker(inspection_id: int, image_path: str):
    """
    Handles asynchronous neural network inference and relational 
    persistence of detection artifacts.
    """
    # 1. Resolve path dynamically but safely
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../accessiscan-ai-1/models/train/weights"))
    model_path = os.path.join(model_dir, "best.pt")

    # 2. Defensive Check: Prevent crashes during tests or if training isn't finished
    if not os.path.exists(model_path):
        logging.error(f"CRITICAL: Model file not found at {model_path}. Inference aborted.")
        return 

    try:
        model = YOLO(model_path)
        results = model.predict(image_path)

        with Session(engine) as session:
            for r in results:
                # Ensure detection directory exists
                os.makedirs("data/images/detections/", exist_ok=True)
                r.save(filename=f"data/images/detections/result_{inspection_id}.jpg")
                
                # Extract and persist neural network findings
                for box in r.boxes:
                    new_det = Detection(
                        inspection_id=inspection_id,
                        label=model.names[int(box.cls[0])],
                        confidence=float(box.conf[0])
                    )
                    session.add(new_det)
            session.commit()
            
    except Exception as e:
        logging.error(f"Inference processing error for inspection {inspection_id}: {str(e)}")

# --- 4. API ENDPOINTS ---
# Purpose: Manage the primary inspection lifecycle, from initial asset 
# registration to asynchronous task delegation.
@router.post("/process-asset", status_code=202)
async def process_asset(
    background_tasks: BackgroundTasks,
    site_name: str = Form(...),
    location: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Registers a new inspection and triggers background inference."""
    validate_file_extension(file.filename)
    
    # Store binary asset
    target_path = f"data/images/uploads/{file.filename}"
    with open(target_path, "wb") as buffer:
        buffer.write(await file.read())

    # Initialize relational inspection record
    inspection = Inspection(site_name=site_name, location=location, status="processing")
    session.add(inspection)
    session.commit()
    session.refresh(inspection)

    # Delegate compute-intensive task to background worker
    background_tasks.add_task(background_inference_worker, inspection.id, target_path)
    return {"status": "Accepted", "inspection_id": inspection.id}

@router.get("/", status_code=200)
def list_inspections(session: Session = Depends(get_session)) -> List[Inspection]:
    """Retrieves the full registry of asset inspections."""
    return session.exec(select(Inspection)).all()

@router.get("/{inspection_id}/detections")
def get_detections(inspection_id: int, session: Session = Depends(get_session)):
    """Queries detection metrics for a specific inspection ID."""
    statement = select(Detection).where(Detection.inspection_id == inspection_id)
    return session.exec(statement).all()