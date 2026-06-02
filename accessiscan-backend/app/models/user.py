"""
DATA ARCHITECTURE ENTITY MATRIX (User SQLModel Schema)
---------------------------------------------------------------------
Purpose:
    Defines the structural schema mapping and data constraints for platform 
    user accounts and field personnel within the central database.

Architecture:
    1. Lookup Optimization: Enforces strict indexing on high-frequency 
       identification strings to minimize query latency.
    2. Secure Credential Handling: Isolates sensitive authentication hashes 
       within non-public attributes to maintain security best practices.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# --- 1. USER SCHEMA DEFINITION ---
# Purpose: The primary identity entity for platform users. Provides the 
# relational base for authentication, access control, and audit logging.
class User(SQLModel, table=True):
    """User profile relational persistence schematics."""
    
    # --- 2. PRIMARY & IDENTITY ANCHORS ---
    # Purpose: Assign unique database identifiers and store base personnel 
    # identification data.
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    
    # Purpose: Ensure high-performance identity retrieval and data integrity 
    # via unique indexing.
    email: str = Field(index=True, unique=True)

    # --- 3. SECURITY LAYER ---
    # Purpose: House secure, encrypted credential representations. 
    # Note: Plaintext storage is strictly prohibited to maintain security compliance.
    password_hash: Optional[str] = None

    # --- 4. ACCESS CONTROL ---
    # Purpose: Manage authorization levels and role-based access for 
    # internal compliance auditing.
    role: str = Field(default="inspector", index=True)  
    
    # --- 5. AUDIT TRAIL TELEMETRY ---
    # Purpose: Capture user account lifecycle metadata for operational auditing.
    created_at: datetime = Field(default_factory=datetime.utcnow)
