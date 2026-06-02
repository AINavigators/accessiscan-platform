"""
AI INFERENCE & COMPLIANCE METROLOGY ENGINE
---------------------------------------------------------------------
Purpose:
    Orchestrates the AI inference pipeline, translates geometric telemetry 
    into engineering measurements, and persists compliance findings 
    into the relational database.

Architecture:
    1. Compliance Logic: Implements DSAPT-specific heuristics to evaluate 
       the safety status of transit infrastructure based on detection coordinates.
    2. Atomic Persistence: Ensures CV inference results are synchronized 
       with relational audit logs in an all-or-nothing transaction.
"""

import logging
import math
from pathlib import Path
from ultralytics import YOLO
from sqlmodel import Session
from app.models.detection import Detection
from app.db.session import engine

# --- 1. COMPLIANCE EVALUATION ENGINE ---
# Purpose: Process raw bounding box coordinates into formal DSAPT 
# compliance statuses using hard-coded regulatory heuristics.
def calculate_compliance(label: str, x_min: float, y_min: float, x_max: float, y_max: float):
    """Applies regulatory heuristic thresholds to infrastructure measurements."""
    width = x_max - x_min
    height = y_max - y_min
    status = "Compliant"
    
    # Heuristic thresholds for infrastructure compliance
    if label == "platform_gap" and width > 60:
        status = "Non-Compliant"
    elif label == "ramp" and (height / width) > 0.08:
        status = "Non-Compliant"
        
    return status

# --- 2. WORKER CONFIGURATION HELPER ---
# Purpose: Dynamically resolve the absolute path to the pre-trained 
# neural network weights file.
def get_model_path() -> Path:
    """Finds the model relative to the current file location."""
    return Path(__file__).resolve().parents[3] / "accessiscan-ai-1" / "models" / "train" / "weights" / "best.pt"

# --- 3. BACKGROUND INFERENCE WORKER ---
# Purpose: Execute detached CV inference, manage geometric mapping, and 
# commit detection findings to the relational database.
def background_inference_worker(inspection_id: int, image_path: str):
    """
    Orchestrates the model inference lifecycle and persists results 
    to the SQLModel-based persistence layer.
    """
    model_path = get_model_path()
    
    if not model_path.exists():
        logging.error(f"CRITICAL: Model not found at {model_path}")
        return

    # Initialize neural network and execute inference
    model = YOLO(str(model_path))
    results = model.predict(image_path)

    # Persist inference results within a unified database transaction
    with Session(engine) as session:
        for r in results:
            for box in r.boxes:
                coords = box.xyxy[0].tolist()
                x1, y1, x2, y2 = coords
                class_id = int(box.cls[0])
                label_name = model.names[class_id]
                conf = float(box.conf[0])
                
                # Execute heuristic compliance validation
                status = calculate_compliance(label_name, x1, y1, x2, y2)
                
                # Map findings to persistence schema
                detection = Detection(
                    inspection_id=inspection_id,
                    class_name=label_name,
                    confidence=conf,
                    x_min=int(x1), y_min=int(y1),
                    x_max=int(x2), y_max=int(y2),
                    status=status
                )
                session.add(detection)
        session.commit()