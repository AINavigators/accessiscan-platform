"""
INSPECTION ENDPOINT INTEGRATION & SUITE VALIDATION
---------------------------------------------------------------------
Purpose:
    Validates transactional lifecycle state switches, boundary schema checks, 
    and multi-part form validation guards within the inspection routing tree.

Architecture:
    1. Integration Validation: Executes API request vectors against an 
       isolated in-memory transactional database.
    2. Boundary Security: Verifies that form validation guards correctly 
       reject malformed or unauthorized asset types.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.inspection import Inspection

# --- 1. INSPECTION WORKFLOW VALIDATION ---
# Purpose: Simulate the full multi-part form ingestion process. Ensures the 
# system correctly handles file streams and transitions inspection states.
def test_create_inspection_success(client: TestClient):
    """Verifies successful ingestion of site inspection assets."""
    fake_image_payload = ("test_station.jpg", b"fake binary image matrix stream bytes", "image/jpeg")
    form_payload = {"site_name": "Reservoir Station", "location": "Platform 1"}
    
    # Executes POST request to the inspection ingestion gateway
    response = client.post(
        "/api/v1/inspections/process-asset", 
        data=form_payload, 
        files={"file": fake_image_payload}
    )
    
    assert response.status_code == 202
    assert response.json()["status"] == "Accepted"

# --- 2. VALIDATION GATE SECURITY ---
# Purpose: Test the resilience of the ingestion pipeline against malformed 
# inputs, confirming the API enforces strict media type compliance.
def test_create_inspection_invalid_file_type(client: TestClient):
    """Verifies rejection of non-compliant file media types."""
    bad_file_payload = ("test.txt", b"malicious", "text/plain")
    form_payload = {"site_name": "Station", "location": "Platform 1"}
    
    # Executes request with disallowed mime-type to verify defensive gatekeeper
    response = client.post(
        "/api/v1/inspections/process-asset", 
        data=form_payload, 
        files={"file": bad_file_payload}
    )
    
    assert response.status_code == 415
    assert "Invalid media type" in response.json()["detail"]

# --- 3. RELATIONAL QUERY VALIDATION ---
# Purpose: Ensure the GET interface correctly serializes stored 
# inspection nodes to verify database-API connectivity.
def test_get_inspections_list(client: TestClient, session: Session):
    """Verifies retrieval of registered inspection nodes."""
    # Seed test node directly into the session
    test_node = Inspection(site_name="Test Station", location="Ramp 1", status="completed")
    session.add(test_node)
    session.commit()
    
    # Executes GET request to verify relational mapping
    response = client.get("/api/v1/inspections/")
    assert response.status_code == 200
    assert len(response.json()) >= 1