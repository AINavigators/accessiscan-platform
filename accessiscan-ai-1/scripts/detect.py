"""
GEOMETRIC METROLOGY & COMPUTER VISION INFERENCE ENGINE (Detector: The Specialist)
---------------------------------------------------------------------
Purpose:
    Handles computer vision inference and keypoint metrology extraction. 
    Encapsulates YOLOv8-Pose to identify accessibility features, 
    map structural skeletons, and perform precise compliance measurements.

Architecture:
    1. Stateless CV Pass: Pure functional processing; returns in-memory 
       arrays to maintain disk-layer integrity.
    2. Keypoint Vector Metrology: Uses custom landmark geometry to 
       calculate clearance gaps and surface slopes.
    3. Gaussian Privacy Filter: Applies 15x15 kernel blurs to protect PII.
    4. Graceful Degradation: Implements automatic fallback to standard 
       topology if custom weights are missing.
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO

class AccesiScanDetector:
    def __init__(self, model_path=None):
        """
        Initializes the inference engine with localized weight resolution 
        and defensive fallback protocols.
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # --- 1. MODEL ARCHITECTURE MAPPING ---
        # Purpose: Resolve target weights, prioritizing production-trained 
        # checkpoints with a fallback to native YOLO topologies.
        if model_path:
            self.model_path = model_path
        else:
            self.model_path = os.normpath(os.path.join(
                base_path, "..", "models", "train", "weights", "best.pt"
            ))

        self.class_names = {
            0: "accessibility_signage", 1: "handrail", 2: "kerb_ramp",
            3: "platform_edge", 4: "ramp", 5: "stairs", 6: "tactile_indicators"
        }

        # Initialize neural engine
        if os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
        else:
            self.model = YOLO("yolov8n-pose.pt")

    def _apply_privacy_mask(self, img: np.ndarray, boxes) -> np.ndarray:
        # --- 2. PRIVACY COMPLIANCE LAYER ---
        # Purpose: Destructively redact background PII using Gaussian blurs, 
        # isolating infrastructure for regulatory compliance.
        masked_img = img.copy()
        h, w, _ = img.shape
        infrastructure_mask = np.zeros((h, w), dtype=np.uint8)

        has_targets = False
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                cls_id = int(box.cls[0].item()) if hasattr(box, 'cls') else 0
                if cls_id in [1, 2, 3, 4, 5, 6]:
                    has_targets = True
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    cv2.rectangle(infrastructure_mask, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), 255, -1)

        if has_targets:
            blurred_entire_image = cv2.GaussianBlur(masked_img, (15, 15), 0)
            inverse_mask = cv2.bitwise_not(infrastructure_mask)
            sharp_infrastructure = cv2.bitwise_and(masked_img, masked_img, mask=infrastructure_mask)
            blurred_background = cv2.bitwise_and(blurred_entire_image, blurred_entire_image, mask=inverse_mask)
            masked_img = cv2.add(sharp_infrastructure, blurred_background)
            
        return masked_img

    def _calculate_ramp_angulation(self, keypoints) -> float:
        # --- 3. METROLOGY: SLOPE COMPUTATION ---
        # Purpose: Calculate surface slope relative to the ground plane using 
        # dot product vector geometry for DSAPT compliance validation.
        if len(keypoints) < 3: return 0.0
        p1, p2, p3 = keypoints[0][:2], keypoints[1][:2], keypoints[2][:2]

        if np.all(p1 == 0) or np.all(p2 == 0): return 0.0
        
        ramp_vector = p2 - p1
        ground_vector = (p3 - p1) if not np.all(p3 == 0) else np.array([1.0, 0.0])

        dot = np.dot(ramp_vector, ground_vector)
        norm = np.linalg.norm(ramp_vector) * np.linalg.norm(ground_vector)
        
        if norm == 0: return 0.0
        angle_deg = np.degrees(np.arccos(np.clip(dot / norm, -1.0, 1.0)))
        return float(round(min(angle_deg, 180 - angle_deg), 2))

    def run_detection(self, image_path: str):
        # --- 4. INFERENCE & COMPLIANCE LOOP ---
        # Purpose: Execute forward-pass inference, apply metrology, and 
        # produce a validated compliance readout.
        img = cv2.imread(image_path)
        if img is None: raise FileNotFoundError("Asset unreadable.")

        results = self.model(img, verbose=False)
        raw_detections = []
        
        # ... [Logic for processing boxes/compliance thresholds] ...

        # Apply privacy safeguards
        protected_img = self._apply_privacy_mask(img, results[0].boxes)
        
        # ... [Drawing logic] ...
        return raw_detections, protected_img