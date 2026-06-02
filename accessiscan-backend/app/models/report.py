"""
DATA ARCHITECTURE ENTITY MATRIX (Report SQLModel Schema)
---------------------------------------------------------------------
Purpose:
    Defines the relational structural entity and validation schema for 
    compliance reports, recording final evaluations and metadata.

Architecture:
    1. Relational Decoupling: Maintains explicit foreign key linkages to 
       parent inspection records to ensure referential data integrity.
    2. Lifecycle Auditing: Tracks report generation timelines and regulatory 
       compliance metrics for certification.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# --- 1. REPORT SCHEMA DEFINITION ---
# Purpose: The final persistence schema for regulatory audit results. 
# Provides a structured summary of compliance status and evaluation metadata.
class Report(SQLModel, table=True):
    """Report relational persistence schematics."""
    
    # --- 2. PRIMARY & FOREIGN KEY ANCHORS ---
    # Purpose: Identify the report instance and establish relational 
    # integrity with the originating inspection session.
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Purpose: Ensure referential alignment; CASCADE ensures reports 
    # are pruned if the parent inspection is removed.
    inspection_id: int = Field(foreign_key="inspection.id", ondelete="CASCADE")
    
    # --- 3. CORE AUDIT EVALUATION ATTRIBUTES ---
    # Purpose: Store formal documentation headers and generated findings.
    title: str = Field(default="DSAPT Accessibility Compliance Audit Certificate")
    summary: Optional[str] = Field(default="No summary text generated.")
    
    # --- 4. OPERATIONAL COMPLIANCE STATUS ---
    # Purpose: Record the final regulatory certification outcome.
    status: str = Field(default="Compliant", index=True)  
    
    # --- 5. REGULATORY AUDIT TIMESTAMP ---
    # Purpose: Capture the exact temporal coordinate of report generation 
    # for audit-trail verification.
    generated_at: datetime = Field(default_factory=datetime.utcnow)