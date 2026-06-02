"""
DATA ARCHITECTURE ENTITY MATRIX (Detection SQLModel Schema)
---------------------------------------------------------------------
Purpose:
    Defines the relational structural entity and validation schema for 
    computer vision observations within the AccessiScan-AI platform.

Architecture:
    1. Type-Safe Persistence: Maps AI findings to indexed, typed database columns.
    2. Metrology Alignment: Tracks physical measurements to satisfy 
       DSAPT statutory compliance metrics.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# --- 1. DETECTION SCHEMA DEFINITION ---
# Purpose: Define the relational structure for persistent storage of 
# AI-detected objects. Maps neural network inference telemetry to 
# indexed relational columns for efficient audit querying.
class Detection(SQLModel, table=True):
    """Detection relational persistence schematics."""
    
    # --- 2. PRIMARY & FOREIGN KEY ANCHORS ---
    # Purpose: Establish relational integrity between detections, 
    # inspections, and source imagery.
    id: Optional[int] = Field(default=None, primary_key=True)
    inspection_id: int = Field(foreign_key="inspection.id", ondelete="CASCADE")
    image_id: Optional[int] = Field(default=None, foreign_key="image.id", ondelete="SET NULL")

    # --- 3. NEURAL NETWORK TELEMETRY ---
    # Purpose: Capture core classification data and confidence scores 
    # derived from model inference.
    class_name: str = Field(index=True)
    confidence: float

    # --- 4. BOUNDING BOX GEOMETRY ---
    # Purpose: Persist the normalized pixel matrix coordinates 
    # representing the localized asset anomaly.
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    # --- 5. METROLOGY QUANTIFIERS ---
    # Purpose: Store quantitative analysis data required for 
    # DSAPT statutory compliance verification.
    measurement_mm: float = Field(default=0.0)
    angulation_deg: float = Field(default=0.0)
    status: str = Field(default="Compliant", index=True)

    # --- 6. TIME-SERIES AUDIT METADATA ---
    # Purpose: Log the temporal context of each detection for 
    # sequence-based reporting.
    created_at: datetime = Field(default_factory=datetime.utcnow)