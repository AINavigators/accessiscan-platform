"""
CENTRAL ROUTING MATRIX (API Router Aggregator Complex)
---------------------------------------------------------------------
Purpose:
    Aggregates and orchestrates all individual sub-domain endpoint routers 
    into a unified API routing graph structure for the AccessiScan platform.

Architecture:
    1. Namespacing: Enforces separation of concerns via explicit domain prefixes.
    2. Modularity: Provides a decoupled boundary for appending new 
       resource nodes without impacting core system operations.
"""

from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.inspections import router as inspections_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.detections import router as detections_router

# --- 1. ROUTER AGGREGATION ---
# Purpose: Initialize the root router to serve as the primary gateway 
# for all v1-compliant network requests.
api_router = APIRouter(redirect_slashes=True)

# --- 2. ENDPOINT NAMESPACING ---
# Purpose: Map domain-specific routers to explicit URL namespaces to 
# ensure architectural separation and team-based scalability.
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication Layer"])
api_router.include_router(users_router, prefix="/users", tags=["User Profile Registry"])
api_router.include_router(inspections_router, prefix="/inspections", tags=["Field Inspection Logs"])
api_router.include_router(reports_router, prefix="/reports", tags=["DSAPT Compliance Reports"])
api_router.include_router(detections_router, prefix="/detections", tags=["AI Vision Metrics"])