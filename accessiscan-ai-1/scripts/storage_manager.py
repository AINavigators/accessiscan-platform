"""
COMPLIANCE DATA PERSISTENCE & ARCHIVAL MANAGER (Storage_Manager: The Archivist)
--------------------------------------------------------------------------------
Purpose:
    Handles data persistence, file system verification, and technical 
    reporting. Maps raw inference lists into immutable compliance ledgers.

Architecture:
    1. Automated File Registry: Validates and instantiates storage layers 
       ('runs/detect/audit_results') on initialization.
    2. Statutory Matrix Enforcement: Evaluates metrology against DSAPT 2026 
       legal thresholds to determine structural compliance.
    3. Business Intelligence Schemas: Produces timestamped JSON payloads 
       optimized for downstream analytics and public agency reporting.
"""

import datetime
import json
import os

class AuditStorage:
    """
    DATA PERSISTENCE & COMPLIANCE ARCHIVE
    Centralizes storage of audit logs and maps AI findings to legal standards.
    """

    def __init__(self, storage_dir=None):
        # --- 1. ARCHITECTURAL INITIALIZATION ---
        # Purpose: Instantiate target directories with deterministic pathing 
        # to ensure environment-agnostic execution.
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        if storage_dir:
            self.storage_dir = os.path.abspath(storage_dir)
        else:
            self.storage_dir = os.path.normpath(os.path.join(
                base_path, "..", "runs", "detect", "audit_results"
            ))
            
        os.makedirs(self.storage_dir, exist_ok=True)

    def _generate_dsapt_summary(self, detections) -> dict:
        # --- 2. STATUTORY COMPLIANCE EVALUATION ---
        # Purpose: Perform logical validation against DSAPT 2026 threshold 
        # matrices to flag engineering non-compliances.
        has_ramp, has_tactile = False, False
        MAX_ALLOWED_SLOPE_DEG = 2.0
        MAX_ALLOWED_GAP_MM = 50.0
        structural_failures = []

        for det in detections:
            class_name = det.get("class_name", "")
            if class_name == "ramp":
                has_ramp = True
                slope = det.get("angulation_deg", 0.0)
                if slope > MAX_ALLOWED_SLOPE_DEG:
                    structural_failures.append(f"Ramp slope ({slope}°) exceeds {MAX_ALLOWED_SLOPE_DEG}°.")
            elif class_name == "tactile_indicators":
                has_tactile = True
            elif class_name == "platform_edge":
                gap = det.get("measurement_mm", 0.0)
                if gap > MAX_ALLOWED_GAP_MM:
                    structural_failures.append(f"Gap ({int(gap)}mm) exceeds {int(MAX_ALLOWED_GAP_MM)}mm limit.")

        # Determine overall status based on engineering constraints
        if not has_ramp: overall_status = "Non-Compliant (Missing Ramp)"
        elif not has_tactile: overall_status = "Non-Compliant (Missing Tactile Indicators)"
        elif structural_failures: overall_status = f"Non-Compliant ({'; '.join(structural_failures)})"
        else: overall_status = "Compliant"

        return {
            "overall_status": overall_status,
            "engineering_exceptions": structural_failures
        }

    def save_audit_result(self, station_name, detections) -> str:
        # --- 3. AUDIT DATA PERSISTENCE ---
        # Purpose: Serialize the findings into an immutable JSON artifact 
        # with full audit metadata.
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "metadata": {
                "station": station_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "audit_framework": "DSAPT_2026_COMPLIANCE_STANDARD"
            },
            "executive_summary": self._generate_dsapt_summary(detections),
            "detailed_findings": detections
        }
        
        file_path = os.path.join(self.storage_dir, f"report_{timestamp}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
            
        return file_path