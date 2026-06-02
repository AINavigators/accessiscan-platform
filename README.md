# AccessiScan-AI Platform

This repository contains two primary workspaces:

- `accessiscan-backend/` — the FastAPI backend service and API gateway
- `accessiscan-ai-1/` — the computer vision inference engine and metrology pipeline

The platform is designed to process uploaded inspection images, run YOLO-based detections, and store audit results for DSAPT compliance analysis.

---

## Repository structure

### `accessiscan-backend/`

This is the backend API workspace.

- `main.py`
  - Entry point for the backend application.
  - Creates the FastAPI app, registers routes under `/api/v1`, and starts Uvicorn.

- `app/api/v1/api.py`
  - Aggregates FastAPI routers and defines API namespaces.

- `app/api/v1/endpoints/inspections.py`
  - Upload endpoint for inspection images.
  - Validates file extensions and stores uploaded images in `data/images/uploads/`.
  - Launches a background task that loads the YOLO model from `accessiscan-ai-1/models/train/weights/best.pt` and saves inference outputs to `data/images/detections/`.

- `app/db/session.py`
  - Database engine and session factory using SQLModel.
  - Creates tables for `User`, `Inspection`, `Detection`, `Report`, and `Image` models.

- `app/models/`
  - SQLModel entity definitions for audit records and metadata.

- `app/core/config.py`
  - Environment and database configuration settings.

- `app/utils/` and subfolders
  - Utility components such as PDF generation and service logic.

- `runs/detect/audit_results/`
  - Intended archive location for detection outputs, but the current implementation saves image outputs under `data/images/detections/`.

- `tests/`
  - Backend test suite for inspections, inference routing, and detections.

- `requirements.txt`
  - Backend dependencies for FastAPI, SQLModel, Uvicorn, and test tooling.

---

### `accessiscan-ai-1/`

This is the AI engine workspace.

- `ai_engine.py`
  - Main controller for AI pipeline execution.
  - Validates model files and image paths.
  - Uses `scripts.detect.AccesiScanDetector` and `scripts.storage_manager.AuditStorage`.

- `scripts/detect.py`
  - Performs object detection and annotation.
  - Contains the vision inference and metrology logic.

- `scripts/storage_manager.py`
  - Saves audit metadata and image evidence.

- `scripts/system_utils.py`
  - Applies environment setup and runtime compatibility patches.

- `models/train/weights/best.pt`
  - Primary YOLO model weights used by both the backend and AI engine.

- `models/train/weights/best.onnx`
  - Optional ONNX model artifact for accelerated inference.

- `data/`
  - Contains the YOLO-formatted dataset used for training and validation.

- `requirements.txt`
  - AI workspace dependencies for computer vision, OpenCV, and YOLO.

---

## How to run

### Backend service

1. Open a terminal in `accessiscan-backend/`.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
 ### Installation & System Execution Guide

Follow these sequential steps to initialize your isolated local environment, resolve dependencies, and launch the platform:
1. **Navigate to the Backend Subdirectory**
The application gateway handles dependency mapping and pipeline orchestration. If you are in the repository root folder, enter the backend directory:
```bash
cd accessiscan-backend
```
2. ***Instantiate the Isolated Python Virtual Environment**
Create your isolated environment workspace directly within the backend directory:
```bash
python -m venv venv
```
3. **Activate the Virtual Environment Context**
Select and run the activation sequence corresponding to your host operating system architecture:

**Windows (PowerShell):** 
```bash
.\venv\Scripts\Activate.ps1`

```
**Windows (Command Prompt):**
 ```bash
 .\venv\Scripts\activate.bat`
```
**macOS / Linux (Terminal):** `
```bash
source venv/bin/activate`
```

4. **Bootstrap Package Management Utilities**
Ensure the system wheel builders and installation tools are updated to guarantee stable package dependency resolution:
```bash
pip install --upgrade pip setuptools wheel
```
5. **Install the Comprehensive Dependency Tree**
Install the complete framework suite—including FastAPI, SQLModel, Pytest, OpenCV, and Ultralytics—via the backend requirements catalog:
```bash
pip install -r requirements.txt

```
6. **Launch the Application & Verify via Swagger UI**
Start the local application gateway using the Uvicorn deployment server:
```bash
uvicorn main:app --reload
``` 
7. **Visit `http://127.0.0.1:8000/docs` to explore the API.**

### AI engine

1. Open a terminal in `accessiscan-ai-1/`.
2. Create and activate a separate virtual environment if needed.
3. Install AI dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the AI controller directly:
   ```bash
   python ai_engine.py
   ```

---

## Notes on current implementation

- The backend entrypoint is `accessiscan-backend/main.py`.
- The backend inspection route currently loads the YOLO model directly and saves detection results in `data/images/detections/`.
- The `accessiscan-ai-1/` workspace contains the pipeline used for standalone AI audits.
- This repo uses two separate local workspaces rather than a single combined Python package.

---
