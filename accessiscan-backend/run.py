"""
APPLICATION EXECUTION HARNESS
---------------------------------------------------------------------
Purpose:
    Serves as the primary entry point for the AccessiScan API service. 
    Configures the Uvicorn ASGI server to orchestrate runtime lifecycle, 
    host binding, and development hot-reload features.

Architecture:
    1. ASGI Orchestration: Initializes the Uvicorn server to manage 
       high-concurrency network I/O.
    2. Development Lifecycle: Enables hot-reloading to ensure rapid 
       feedback loops during feature iteration.
"""

import uvicorn

# --- 1. SERVICE BOOTSTRAP ---
# Purpose: Initialize the Uvicorn ASGI server using the 'main:app' 
# entry point. Configured for network accessibility and rapid iteration.
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )