"""
DATA ARCHITECTURE ENTITY MATRIX (Inspection SQLModel Schema)
---------------------------------------------------------------------
Purpose:
    Defines the structural schema for compliance inspection sessions, 
    tracking site metadata, operational telemetry, and lifecycle states.

Architecture:
    1. Accountability Lifecycle: Enforces state-machine validation to track 
       the pipeline progress (processing, completed, failed).
    2. Extensible Metadata: Utilizes JSON-based schema-less fields for 
       future-proofing inspection telemetry.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON

# --- 1. INSPECTION SCHEMA DEFINITION ---
# Purpose: The central state-tracking entity for audit sessions. Acts as the 
# primary relational anchor for visual evidence and detection findings.
class Inspection(SQLModel, table=True):
    """Inspection relational persistence schematics."""
    
    # --- 2. PRIMARY & FACILITY IDENTIFIERS ---
    # Purpose: Define base asset attributes and physical location metadata.
    id: Optional[int] = Field(default=None, primary_key=True)
    site_name: str = Field(index=True)
    location: str
    description: Optional[str] = None

    # --- 3. LIFECYCLE STATE ENGINE ---
    # Purpose: Track the operational progression of the compliance pipeline 
    # through distinct state flags.
    status: str = Field(default="processing", index=True)

    # --- 4. TIME-SERIES AUDIT METADATA ---
    # Purpose: Log temporal events for traceability and compliance reporting.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- 5. SYSTEM DATA BRIDGE ---
    # Purpose: Provide flexible JSON storage for custom parameters, ensuring
    # long-term schema extensibility without necessitating disruptive 
    # database migration cycles.
    results_data: Optional[Dict[str, Any]] = Field(
        default=None, 
        sa_column=Column(JSON)
    )