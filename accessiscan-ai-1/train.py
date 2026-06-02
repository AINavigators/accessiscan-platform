"""
TRAINING PIPELINE & HYPERPARAMETER OPTIMIZATION ENGINE (AccessiScan Trainer)
---------------------------------------------------------------------
Purpose:
    Handles the automated acquisition, training, and validation of 
    the YOLOv8-Pose vision models. Encapsulates training, hyperparameter 
    management, and dataset synchronization.

Architecture:
    1. Automated Experiment Tracking: Integrates Weights & Biases (wandb) 
       for immutable, verifiable training logs.
    2. Weight Archival Automation: Extracts optimal weight graphs ('best.pt', 
       'best.onnx') and migrates them to a static deployment repository.
    3. Threading Stability Guardrail: Constraints workers=0 to prevent 
       OS-level memory leaks and socket lockouts.
"""

import os
import shutil
import argparse
import wandb
from roboflow import Roboflow
from ultralytics import YOLO

def main():
    # --- 1. CONFIGURATION & CLI MAPPING ---
    # Purpose: Sets the workspace environment and parses user inputs for 
    # hyperparameter tuning, ensuring consistent training reproducibility.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR) 

    parser = argparse.ArgumentParser(description="AccessiScan-AI Training Pipeline")
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--project', default='models/train')
    parser.add_argument('--name', default='accessiscan_pose_run')
    args = parser.parse_args()

    # --- 2. DATASET SYNCHRONIZATION ---
    # Purpose: Connects to the Roboflow cloud API to pull the latest 
    # infrastructure keypoint data. Acts as the first gate of the pipeline.
    # NOTE: Ensure ROBOFLOW_API_KEY is defined in environment for security.
    rf = Roboflow(api_key=os.getenv("ROBOFLOW_API_KEY", "your-key-here"))
    project = rf.workspace("fatimabus-workspace").project("accessiscan-ai-project1")
    dataset = project.version(1).download("yolov8")
    config_path = os.path.normpath(os.path.join(dataset.location, "data.yaml"))

    # --- 3. TRAINING LOOP EXECUTION ---
    # Purpose: Orchestrates the YOLOv8-Pose training loop with stability 
    # constraints (workers=0) to prevent cross-platform resource contention.
    wandb.init(project="AccessiScan-AI-Inference", name=args.name, config=vars(args))
    model = YOLO("yolov8n-pose.pt")

    model.train(
        data=config_path,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        device="cpu",
        workers=0, # Stability constraint
        plots=True
    )

    # --- 4. OPTIMIZATION & ASSET MIGRATION ---
    # Purpose: Automates the conversion of PyTorch models to ONNX and 
    # synchronizes the static repository, ensuring the AI Engine always 
    # maintains access to the most performant weight matrix.
    src_weights = os.path.join(args.project, args.name, 'weights')
    dest_dir = os.path.join(args.project, 'weights')
    os.makedirs(dest_dir, exist_ok=True)

    # Export to ONNX for cross-platform inference optimization
    exported_model = YOLO(os.path.join(src_weights, 'best.pt'))
    exported_model.export(format='onnx')

    # Migrate assets for the AI Engine (Single Source of Truth)
    for model_file in ['best.pt', 'best.onnx']:
        src = os.path.join(src_weights, model_file)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest_dir, model_file))

    wandb.finish()

if __name__ == '__main__':
    main()