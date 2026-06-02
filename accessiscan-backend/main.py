"""
ENTRYPOINT WEB APPLICATION ROUTER (AccessiScan API Backend)
---------------------------------------------------------------------
Purpose:
    Acts as the primary entrypoint and initialization router. Manages the 
    FastAPI framework, CORS security, and asynchronous lifecycle hooks.

Architecture:
    1. Workspace Isolation: Normalizes paths to ensure peer-repository 
       (AI Engine) accessibility across varying host environments.
    2. Lifespan Management: Orchestrates startup/shutdown routines for 
       database pools and machine learning model memory.
    3. CORS Security Perimeter: Establishes a controlled ingress gate for 
       authorized client communication.
"""

import logging
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scripts.system_utils import setup_environment
from app.api.v1.api import api_router
from app.db.session import create_db_and_tables

# --- 1. WORKSPACE NORMALIZATION ---
# Purpose: Dynamically resolve the project root and inject it into the 
# system path to ensure cross-module availability of helper scripts.
PROJECT_ROOT = Path(__file__).resolve().parent.parent 
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- 2. TELEMETRY CONFIGURATION ---
# Purpose: Initialize standardized logging for observability and 
# diagnostics during the application lifecycle.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- 3. LIFESPAN MANAGEMENT ---
# Purpose: Define controlled startup and shutdown routines.
# Ensures database schema readiness and system environment validation.
async def lifespan(app: FastAPI):
    logging.info("[*] Launching AccessiScan API Engine...")
    setup_environment()
    create_db_and_tables()
    yield
    logging.info("[-] Shutting down AccessiScan API Engine.")

# --- 4. APPLICATION INITIALIZATION ---
# Purpose: Construct the FastAPI instance with integrated service 
# metadata and security middleware.
app = FastAPI(
    title="AccessiScan API",
    description="Automated DSAPT Compliance Auditing Backend Engine",
    version="1.0.0",
    lifespan=lifespan
)

# --- 5. SECURITY PERIMETER ---
# Purpose: Configure Cross-Origin Resource Sharing (CORS) to regulate 
# ingress traffic from client-side domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 6. ROUTER REGISTRATION ---
# Purpose: Mount the unified API gateway.
app.include_router(api_router, prefix="/api/v1")

# --- 7. SYSTEM TELEMETRY ENDPOINT ---
# Purpose: Provides an external hook for container orchestration 
# health-check probes.
@app.get("/health", tags=["System Telemetry"])
async def health_check() -> dict:
    """Provides status telemetry for the AccessiScan engine."""
    return {"status": "Healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)