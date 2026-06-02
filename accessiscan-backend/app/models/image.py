"""
DATA ARCHITECTURE ENTITY MATRIX (Image SQLModel Schema)
---------------------------------------------------------------------
Purpose:
    Defines the structural schema mapping for infrastructure photographs, 
    bridging physical file storage with relational vision inspection data.

Architecture:
    1. Transactional Enforcement: Establishes rigid hierarchy through 
       enforced foreign key relationships.
    2. Compliance Chain of Custody: Maintains immutable audit trails linking 
       visual assets to user identities and creation timelines.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# --- 1. IMAGE SCHEMA DEFINITION ---
# Purpose: Define the relational metadata for stored visual assets, 
# mapping storage locations to their respective inspection sessions and users.
class Image(SQLModel, table=True):
    """Image relational persistence schematics."""
    
    # --- 2. PRIMARY & FOREIGN KEY ANCHORS ---
    # Purpose: Identify the asset and establish relational integrity.
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Purpose: Maintain lifecycle synchronization; CASCADE ensures child 
    # metadata is pruned when the associated inspection is deleted.
    inspection_id: int = Field(foreign_key="inspection.id", ondelete="CASCADE")
    
    # --- 3. ASSET INGRESS DATA ---
    # Purpose: Map physical file locations and identifiers within the storage layer.
    image_url: str
    image_name: Optional[str] = None

    # --- 4. AUDIT TRAIL TELEMETRY ---
    # Purpose: Link imagery to the originating user. 
    # Note: SET NULL preserves the visual record history despite any 
    # potential changes to user account status.
    uploaded_by: Optional[int] = Field(default=None, foreign_key="user.id", ondelete="SET NULL")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)