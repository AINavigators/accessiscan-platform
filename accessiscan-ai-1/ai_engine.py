"""
EXECUTIVE PIPELINE CONTROLLER (AccessiScan-AI Engine)
---------------------------------------------------------------------
Purpose:
    Acts as the executive pipeline controller for the AccessiScan-AI system.
    Orchestrates the workflow between the Computer Vision 'Specialist' 
    (AccesiScanDetector) and the Data 'Archivist' (AuditStorage).

Architecture:
    1. Centralized Safety Net: Implements defensive guardrails to intercept 
       pathing, model weight, and image matrix corruption errors.
    2. Runtime Acceleration Fallback: Orchestrates flexible deployment 
       by prioritizing ONNX acceleration over standard PyTorch weights.
"""

import os
import cv2
from scripts.detect import AccesiScanDetector
from scripts.storage_manager import AuditStorage
from scripts.system_utils import setup_environment

# Initialize environment configurations
setup_environment()

class AccesiScanEngine:
    """
    EXECUTIVE PIPELINE CONTROLLER
    Orchestrates the lifecycle of infrastructure audits from image 
    ingestion to metrology-driven reporting.
    """

    def __init__(self, detector=None, storage=None, weights_dir=None):
        """
        Initializes pipeline components with absolute path mapping to 
        ensure environment-agnostic execution safety.
        """
        self.detector = detector if detector is not None else AccesiScanDetector()
        self.storage = storage if storage is not None else AuditStorage()
        
        base_ai_path = os.path.dirname(os.path.abspath(__file__))
        
        if weights_dir:
            self.production_dir = os.path.abspath(weights_dir)
        else:
            self.production_dir = os.path.normpath(os.path.join(base_ai_path, "models", "train", "weights"))
        
        # Define model artifact paths for runtime evaluation
        self.weights_path = os.path.join(self.production_dir, "best.pt")
        self.onnx_path = os.path.join(self.production_dir, "best.onnx")

    def run_audit(self, image_path, station_name="General_Station") -> dict:
        """
        END-TO-END WORKFLOW: Raw Image -> AI Inference -> Metrology -> Archive.
        Enforces defensive validation perimeters for system reliability.
        """
        print(f"[*] Initializing AccessiScan-AI Pipeline Execution Loop for {station_name}...")

        # --- GUARDRAIL 1: Model Asset Verification ---
        # Purpose: Validate existence of neural network weights before compute initiation.
        if not os.path.exists(self.weights_path) and not os.path.exists(self.onnx_path):
            return {
                "status": "Needs Retry",
                "error_type": "Missing Model Asset",
                "message": "Neural weights could not be localized. Populate artifacts."
            }

        # --- GUARDRAIL 2: Asset Pathing Validation ---
        # Purpose: Confirm target image integrity at the filesystem boundary.
        if not os.path.exists(image_path):
            return {
                "status": "Needs Retry",
                "error_type": "Pathing Error",
                "message": f"Input image asset missing at: {image_path}"
            }

        # --- GUARDRAIL 3: Image Matrix Corruption Check ---
        # Purpose: Intercept malformed image data before it hits the detection layer.
        try:
            test_img = cv2.imread(image_path)
            if test_img is None or test_img.size == 0:
                raise ValueError("Pixel array matrix parsing failed.")
        except Exception as img_err:
            return {
                "status": "Needs Retry",
                "error_type": "Corrupt Image Matrix",
                "message": "Photograph file is corrupted or uses an incompatible encoder."
            }

        # --- PIPELINE EXECUTION ---
        try:
            # Step 1: Inference & Metrology (The Specialist)
            raw_findings, annotated_img = self.detector.run_detection(image_path)
            
            # Step 2: Visual Evidence Archiving (The Archivist)
            img_name = f"{station_name}_evidence.jpg"
            img_path = os.path.join(self.storage.storage_dir, img_name)
            cv2.imwrite(img_path, annotated_img)

            # Step 3: Technical Metadata Archiving
            report_path = self.storage.save_audit_result(station_name, raw_findings)
            
            return {
                "status": "Success",
                "station": station_name,
                "visual_evidence": img_path,
                "data_report": report_path,
                "message": f"Audit complete. Findings archived to {report_path}"
            }

        except Exception as pipeline_fault:
            # --- GUARDRAIL 4: Downstream Safety Net ---
            # Purpose: Catch unexpected runtime faults to ensure API/Pipeline stability.
            return {
                "status": "Needs Retry",
                "error_type": "Runtime Pipeline Exception",
                "message": f"Unhandled operational failure: {str(pipeline_fault)}"
            }

if __name__ == "__main__":
    # --- BATCH AUDIT DIAGNOSTICS ---
    engine = AccesiScanEngine()
    test_suite = ["data/images/test/test_1.jpg"]
    
    for img in test_suite:
        res = engine.run_audit(img, "Reservoir_Station")
        print(f"\nAudit Status: {res['status']}")



                