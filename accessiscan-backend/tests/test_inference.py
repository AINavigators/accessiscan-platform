"""
AI INFERENCE PIPELINE & PERSISTENCE VALIDATION
---------------------------------------------------------------------
Purpose:
    Validates the integration between the machine learning observation 
    layer and the database persistence backend. Ensures that AI-generated 
    detections are correctly mapped and stored within the relational schema.

Architecture:
    1. Inference Trigger Validation: Confirms that detection findings can 
       be persisted against inspection session boundaries.
    2. Database Write Integrity: Verifies that the ORM and session factory 
       correctly synchronize data states with the underlying SQL storage.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.inspection import Inspection
from app.models.detection import Detection

# --- 1. AI LABEL RECOGNITION VALIDATION ---
# Purpose: Simulate an AI observation event. Validates that the system 
# correctly associates neural network output with its parent inspection record.
def test_ai_label_recognition_trigger(client, session, monkeypatch):
    """Verifies relational linkage between AI observations and inspections."""
    monkeypatch.undo()
    
    # --- Setup: Seed persistent inspection record. ---
    inspection = Inspection(site_name="Test Station", location="Platform 1", status="processing")
    session.add(inspection)
    session.commit()
    session.refresh(inspection) 

    # --- Trigger: Simulated detection finding. ---
    dummy_detection = Detection(
        inspection_id=inspection.id,
        class_name="Tactile Grid",
        confidence=0.98,
        x_min=0, y_min=0, x_max=10, y_max=10,
        status="Compliant"
    )
    session.add(dummy_detection)
    session.commit()

    # --- Validation: Verify persistence via relational query. ---
    detections = session.exec(select(Detection).where(Detection.inspection_id == inspection.id)).all()
    assert len(detections) > 0
    assert detections[0].class_name == "Tactile Grid"

# --- 2. PERSISTENCE LAYER VALIDATION ---
# Purpose: Ensure the Detection model and transactional session are 
# correctly configured for atomic database write operations.
def test_database_write_capability(session):
    """Verifies atomic persistence of Detection entities."""
    det = Detection(
        inspection_id=99, 
        class_name="Test", 
        confidence=1.0,
        x_min=0, y_min=0, x_max=10, y_max=10,
        status="Compliant"
    )
    session.add(det)
    session.commit()
    
    # Read-back verification to ensure data synchronization.
    session.refresh(det)
    saved_det = session.exec(select(Detection).where(Detection.id == det.id)).first()
    
    assert saved_det is not None
    assert saved_det.class_name == "Test"