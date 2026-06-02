# AccessiScan-AI Platform

AccessiScan-AI is a dual-workspace proof-of-concept platform for automated DSAPT 2026 compliance auditing. It combines a FastAPI backend and a YOLO-based computer vision inference workspace to process transit infrastructure images, generate detection metadata, and archive compliance audit artifacts.

## Repository layout

- `accessiscan-backend/` — FastAPI backend, database models, and audit report generation.
- `accessiscan-ai-1/` — AI inference workspace, YOLO training/inference code, and local audit ledger generation.
- `README-project.md` — Detailed architecture, data flow, storage strategy, and university project documentation.

## Quick start

1. Open a terminal and change to the backend folder:
   ```powershell
   cd accessiscan-backend
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Update packaging tools:
   ```powershell
   pip install --upgrade pip setuptools wheel
   ```
4. Install backend dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Start the API server:
   ```powershell
   uvicorn main:app --reload
   ```
6. Open the Swagger UI in your browser:
   ```text
   http://127.0.0.1:8000/docs
   ```

## Main API endpoints

- `POST /api/v1/inspections/process-asset`
  - Uploads an asset image and starts background inference.
- `GET /api/v1/reports/generate/{inspection_id}`
  - Generates a report record for a completed inspection.
- `GET /api/v1/reports/download-json/{report_id}`
  - Downloads the stored JSON audit ledger.
- `GET /api/v1/reports/download-pdf/{report_id}`
  - Downloads the generated PDF certificate.
- `GET /api/v1/reports/diagnostics`
  - Returns backend storage path diagnostics.

## Storage locations

- Temporary upload and detection workspace:
  - `accessiscan-backend/data/images/uploads/`
  - `accessiscan-backend/data/images/detections/`
- Permanent backend audit archive:
  - `accessiscan-backend/runs/detect/audit_results/`
- AI workspace audit ledger archive:
  - `accessiscan-ai-1/runs/detect/audit_results/`
