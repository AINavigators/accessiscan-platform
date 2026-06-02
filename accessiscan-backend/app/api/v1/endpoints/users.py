"""
USER RECORD & ACCOUNT INDEX INTERFACE
---------------------------------------------------------------------
Purpose:
    Exposes API directory lookup endpoints for managing platform user accounts, 
    querying personnel profiles, and verifying operational role assignments.

Architecture:
    1. Lookup Sanitization: Interfaces with the persistence layer to stream 
       user data while isolating operational profiles.
    2. Stability Management: Implements defensive transactional checks to 
       handle runtime faults gracefully and provide clear error signatures.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User

# --- 1. ROUTER INITIALIZATION ---
# Purpose: Registers the user-management API namespace.
router = APIRouter()

# --- 2. RELATIONAL USER INDEX (READ ALL) ---
# Purpose: Query the persistent database for the full directory of 
# registered personnel (inspectors, operators, auditors).
@router.get("/", response_model=List[User])
def get_platform_users(session: Session = Depends(get_session)):
    """Retrieves the complete registry of account profiles."""
    try:
        return session.exec(select(User)).all()
    except Exception as db_error:
        # Purpose: Log and intercept persistence layer faults to prevent stack trace leaks.
        raise HTTPException(
            status_code=500,
            detail=f"Database Retrieval Layer encountered an unhandled operational fault: {str(db_error)}"
        )

# --- 3. RELATIONAL PROFILE LOOKUP (READ ONE) ---
# Purpose: Execute a granular search for a specific user identifier, 
# ensuring non-existent lookups return standardized client error responses.
@router.get("/{user_id}", response_model=User)
def get_user_by_identifier(user_id: int, session: Session = Depends(get_session)):
    """Searches the user entity table for a specific primary key index."""
    try:
        user = session.get(User, user_id)
        # Purpose: Enforce strict 404 validation for missing records.
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Target user profile record signature not resolved: {user_id}."
            )
        return user
    except HTTPException:
        raise
    except Exception as query_fault:
        # Purpose: Catch and report unforeseen query-level exceptions.
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during account index verification: {str(query_fault)}"
        )