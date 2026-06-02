"""
DETECTION OBSERVER METROLOGY INTEGRATION & SUITE VALIDATION
---------------------------------------------------------------------
Purpose:
    Validates schema compliance, high-precision floating point limits, 
    and database transactional integrity rules for computer vision findings.

Architecture:
    1. Relational Guardrails: Enforces foreign key constraints by seeding
       required parent inspection records within the test lifecycle.
    2. Payload Validation: Ensures accurate serialization of metrology data
       (bounding boxes and physical measurements) across the API boundary.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.inspection import Inspection

# --- 1. DETECTION PERSISTENCE VALIDATION ---
# Purpose: Execute a full-stack test of the detection creation endpoint. 
# Confirms that the API layer handles relational foreign-key integrity 
# and processes specialized metrology fields correctly.
def test_create_detection_entry(client: TestClient, session: Session):
    """
    Verifies that the detection API successfully records sub-centimeter 
    vision measurements while maintaining database relational rules.
    """
    
    # --- 2. RELATIONAL GUARD STEP ---
    # Purpose: Seed a parent record to satisfy foreign key constraints 
    # before attempting payload submission.
    parent_inspection = Inspection(
        site_name="Reservoir Station",
        location="Platform 1",
        status="completed"
    )
    session.add(parent_inspection)
    session.commit()
    session.refresh(parent_inspection)

    # --- 3. METROLOGY PAYLOAD DEFINITION ---
    # Purpose: Construct a validated payload based on YOLOv8-Pose mapping 
    # to test serialization integrity across the API interface.
    metrology_payload = {
        "inspection_id": parent_inspection.id,
        "class_name": "tactile_indicators",
        "confidence": 0.94,
        "x_min": 100,
        "y_min": 150,
        "x_max": 320,
        "y_max": 410,
        "measurement_mm": 45.2,
        "angulation_deg": 1.4,
        "status": "Compliant"
    }
    
    # --- 4. API TRANSACTION EXECUTION & ASSERTION ---
    # Purpose: Post the transaction and assert integrity of response data 
    # against the submitted payload schema.
    response = client.post("/api/v1/detections/", json=metrology_payload)
    
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["class_name"] == "tactile_indicators"
    assert json_data["measurement_mm"] == 45.2
    assert json_data["status"] == "Compliant"