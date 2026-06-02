"""
APPLICATION ARCHITECTURE CONFIGURATION MATRIX (AccessiScan Backend)
---------------------------------------------------------------------
Purpose:
    Parses environment files, tracks runtime modes, and houses global 
    settings definitions safely across workspace scopes.

Architecture:
    1. Runtime Configuration: Standardizes project metadata and debug modes.
    2. Connection Management: Encapsulates database connectivity parameters 
       using type-safe schema validation.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

def get_project_root() -> Path:
    """Finds the project root by searching for the repo folder name."""
    # Start at this file
    path = Path(__file__).resolve()
    # Move up until we find the root folder (accessiscan-ai-platform)
    while path.name != "accessiscan-ai-platform" and path != path.parent:
        path = path.parent
    return path

REPO_ROOT = get_project_root()
MODEL_PATH = REPO_ROOT / "accessiscan-ai-1" / "models" / "train" / "weights" / "best.pt"

# --- 1. SETTINGS SCHEMA DEFINITION ---
# Purpose: Define the structural blueprint for application settings. 
# Utilizing Pydantic ensures configuration is type-safe and validated.
class Settings(BaseSettings):
    PROJECT_NAME: str = "AccessiScan API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./app.db"

class Config:
        model_config = SettingsConfigDict(env_file=".env")

# --- 2. CONFIGURATION SINGLETON INSTANTIATION ---
# Purpose: Export a globally accessible singleton of the settings object 
# to ensure configuration state consistency across the lifecycle.
settings = Settings()