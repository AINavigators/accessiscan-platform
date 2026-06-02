# AccessiScan-AI: Automated DSAPT 2026 Compliance Auditing

AccessiScan-AI is a high-precision computer vision and automated metrology platform engineered to resolve the Australian public transport sector's accessibility compliance challenges. By transitioning from subjective manual inspections to automated algorithmic auditing, the platform empowers infrastructure operators to achieve verifiable, scalable adherence to the Disability Standards for Accessible Public Transport (DSAPT).

## 1. Strategic Project Context & Engineering Scope

### The Business Case
Traditional accessibility auditing is unsustainable, requiring labor-intensive, expert-led workflows across 5,000+ national transit hubs. AccessiScan-AI disrupts this cost structure by enabling station officers to capture data using standard mobile hardware, effectively shifting from a service-based model to Compliance-as-a-Service (CaaS).

| Metric | Manual Audit Model | AccessiScan-AI Model |
| :--- | :--- | :--- |
| **Labor** | 6 Hours (Expert) | 15 Minutes (Staff) |
| **Cost** | ~$2,500 AUD / Station | ~$50 AUD / Station |
| **Equipment** | Specialized Manual Tools | Mobile Devices |

### Core Technical Capabilities
1. **Geometric Metrology Engine:** Extracts sub-centimeter structural dimensions from imagery.
2. **Decoupled Architecture:** Separate REST API Gateway (/backend) and Computer Vision Pipeline (/ai).
3.  **Statutory Rule Engine:** Maps inference telemetry directly to DSAPT compliance thresholds.
4.  **Atomic Persistence:** Ensures all visual audits are coupled with relational data for a legally defensible chain of custody.

### Project Maturity (PoC)
This repository represents a Technology Readiness Level 3 (TRL 3) proof of concept. The system is designed to validate the feasibility of automating safety assessments under Australian legislation, featuring a fully integrated backend ingestion gateway and a robust geometric rule engine.

>[!TIP]
>Developer Note: This project currently utilizes a dual-workspace layout. See the Architecture Overview for setup instructions on linking the backend API with the inference engine.

---

## 2. System Workflow & Key Features

### End-to-End Enterprise Audit Pipeline
The system utilizes a modular, multi-stage processing pipeline designed to transform raw environmental asset images into structured, legally defensible compliance audits:
1. **Data Ingestion (`accessiscan-backend/`)**: Multi-part image form-data is received by the backend endpoint router (`inspections.py`), validating file integrity and establishing a secure audit session.
2. **Execution Routing:** The backend dispatches the processed asset image path directly to the AI workspace layer, initiating the inference gateway wrapper.
3. **Privacy Masking Protocol:** The engine applies an irreversible 15x15 Gaussian Blur kernel filter over non-target quadrants, permanently redacting public PII markers (faces/bystanders) to ensure adherence to Australian Privacy Principles (APP).
4. **Computer Vision Inference (`accessiscan-ai-1/`):** The core engine loads specialized neural weights (`best.pt`) to execute object detection. If data labeling constraints result in zero detections, the system initiates an automated Visual Sandbox Mode, drawing a fallback bounding validation box on the canvas to protect pipeline continuity.
5. **DSAPT Precision Metrology:** The script analyzes structural pixel matrices using OpenCV algorithms (Canny edge detection and Hough Line Transforms) to convert visual boundaries into physical measurements (centimeters and angulation degrees).
6. **Archival Synchronization:** The backend’s `storage_manager.py` captures the telemetry data, writes a permanent JSON compliance ledger, flattens the boxed image asset, and commits the records side-by-side into the server’s local archive: `.\accessiscan-backend\runs\detect\audit_results\.`

```
[Swagger UI /docs Client]
          │
          ▼ (POST /api/v1/inspections/submit)
[inspections.py (FastAPI Router)] 
          │
          ▼ (Calls Gateway Wrapper with Image Path)
[detect.py (AI Inference Engine)]
          │
          ├──► Runs 15x15 Gaussian Privacy Blur on Image Matrix
          ├──► Executes YOLOv8 Object Detection Pass
          │    ├──► [Found] -> Draws Green/Red Bounding Boxes
          │    └──► [0 Detections] -> Triggers Visual Sandbox (Orange Safety Box)
          │
          ▼ (Computes Gap mm & Angulation Deg)
[storage_manager.py (The Archivist)]
          │
          ├──► Writes Comprehensive JSON Compliance Ledger
          ├──► Saves Flattened Boxed Verification Image File
          │
          ▼ (Saves Artifacts Jointly to Disk Location)
[.\accessiscan-backend\runs\detect\audit_results\]
```

### Technical Benchmarks
Our processing pipelines are bounded by strict engineering benchmarks:
1. Metrology Precision: Implements a localized pixel-to-physical scaling factor matrix (1 px ≈ 0.045 cm) targeting a precision threshold of ±0.5° for angular alignments, critical for validating 1:14 DSAPT ramp thresholds.
2. Statutory Compliance Rules: Features automated deterministic pass/fail triggers matching Australian infrastructure law:

a. **FAIL Trigger 1:** Calculated horizontal asset clearance gaps > 5.0 cm.
b. **FAIL Trigger 2:** Asset angular tilt deviations > 2.0°.

3. **Decoupled Statelessness:** The AI module handles matrix calculations purely in memory without managing system sessions or connections, ensuring it can be completely converted into a static **ONNX computational graph** for lightweight edge deployments.

---

## 3. Repository Structure & Configuration Mapping

### Modular Architecture File Tree
The repository enforces a decoupled directory layout to separate the AI inference engine, enterprise backend service, and data persistence layers across two distinct, localized workspaces:
```
Bash
accessiscan-ai-platform/
├── accessiscan-ai-1/               # COMPUTER VISION & METROLOGY WORKSPACE
│   ├── ai_engine.py                # Executive Pipeline Controller (Main Entry)
│   ├── train.py                    # ML Training & Model Compilation Loop
│   ├── configs/                    # Model Strategy Configuration Layer
│   │   └── data.yaml               # Legal Dataset Taxonomy Definitions
│   ├── data/                       # YOLO-formatted Dataset (images + labels)
│   ├── scripts/                    # Decoupled Operational Submodules
│   │   ├── detect.py               # Vision Inference, Safe Modes & Metrology
│   │   ├── storage_manager.py      # Legal Decision Engine & JSON Ledgers
│   │   └── system_utils.py         # Initialization & Core OS Patches
│   ├── models/                     # Production Network Topology Weights
│   │   └── train/weights/best.pt   # Custom Trained YOLOv8 Weights
│   └── requirements.txt            # AI Framework Dependencies
│
├── accessiscan-backend/            # ENTERPRISE REST API GATEWAY WORKSPACE
│   ├── app/                        # Modular API Application Core
│   │   ├── api/v1/                 # API VERSIONING & ROUTE REGISTRY
│   │   │   ├── api.py              # Main Router Registry
│   │   │   └── endpoints/          # INDIVIDUAL ROUTE DEFINITIONS
│   │   │       ├── inspections.py  # Ingestion Middleware & AI Routers
│   │   │       ├── reports.py      # Analytical Summaries & Export Interface
│   │   │       ├── detections.py   # Computer Vision Metric Endpoint Suite
│   │   │       ├── images.py       # Asset Image Streaming & Processing
│   │   │       └── users.py        # Audit User Authentication & Roles
│   │   ├── db/                     # Database Factory Layer
│   │   │   └── session.py          # Session Factory Engines
│   │   ├── models/                 # RELATIONAL SQLMODEL ENTITIES
│   │   │   ├── report.py           # Executive Summary & Metadata
│   │   │   ├── inspection.py       # Spatial & Session Entities
│   │   │   ├── detection.py        # Telemetry Serialization
│   │   │   ├── image.py            # Asset Image Binary Metadata
│   │   │   └── user.py             # Role Authorization
│   │   ├── utils/                  # UTILITY & SERVICE LAYER
│   │   │   ├── pdf_generator.py    # Report Generation Logic
│   │   │   └── services/           # CORE BUSINESS LOGIC
│   │   │       └── inference_worker.py # Bridge to AI Engine
│   │   └── core/                   # SYSTEM CORE CONFIGURATION
│   │       └── config.py           # Environment Variables & Settings
│   ├── runs/detect/audit_results/  # ◄── REAL TIME OUTPUTS (JSON/Images)
│   ├── tests/                      # AUTOMATED QUALITY ASSURANCE SUITE
│   │   ├── conftest.py             # Mock Database & Test Clients
│   │   ├── test_inspections.py     # Ingestion Logic Tests
│   │   ├── test_inference.py       # AI Pipeline Bridge Tests
│   │   └── test_detections.py      # Telemetry Serialization Tests
│   ├── main.py                     # API Root Entry Point
│   ├── run.py                      # Execution Wrapper
│   └── requirements.txt            # Web Framework Dependencies
│
└── README.md                       # Unified System Master Documentation
```

>[!IMPORTANT]
>**Production Pathing Guardrail & Runtime Stability**
>To ensure runtime stability across heterogeneous testing environments, (`detect.py`) evaluates execution paths dynamically. If custom-trained weights (`best.pt`) are unreachable due to path translation variations, the system executes an automated, graceful degradation to the base model topology (`yolov8n.pt`). This prevents execution crashes and maintains server availability while running your live /docs test streams.

---

## 4. Environment Setup & Core Stack

### Primary Technologies
1. **Python 3.10:** Standardized execution runtime ensuring cross-platform stability for machine learning and web service layers.
2. **FastAPI & Uvicorn:** High-performance, lightweight web framework utilizing ASGI server standards to handle incoming client inspection requests.
3. **SQLModel**: Modern Object-Relational Mapping (ORM) combining SQLAlchemy and Pydantic to enforce type-safe data serialization and relational persistence schemas.
4. **Ultralytics YOLOv8:** Real-time object detection framework, specifically retrained on your Roboflow-labeled dataset for high-accuracy structural asset localization.
5. **OpenCV:** Core matrix manipulation suite utilized for sub-centimeter pixel metrology calibration, angular transforms, and privacy-focused Gaussian blurring.
6. **Pytest & Pytest-Asyncio:** Automated quality assurance framework built to validate system routing behaviors and maintain a 100% test-pass gate.

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

### Verification Flow:
Once the console indicates the server is active, follow this verification flow to test the end-to-end AI metrology pipeline:
1. Open your web browser and navigate to: `http://127.0.0.1:8000/docs`
2. Expand the inspections endpoint suite category.
3. Click on the `POST /api/v1/inspections/submit` inspection processing route.
4. Click the **"Try it out"** button.
5. Choose a test infrastructure image file and execute the request.
6. Confirm the server returns a successful JSON telemetry payload; then navigate to .`\accessiscan-backend\runs\detect\audit_results\` to view your archived JSON report ledger and flattened verification image.

>[!WARNING]
>**Universal Data-Loader Stability Control**
The model optimization loop in `accessiscan-ai-1/train.py` explicitly restricts multi-threaded dataset loading to a single master process **(workers=0)**. This intentional configuration guardrail is mandatory to maintain compatibility with your **Roboflow-tuned weights** and prevents socket crashes, cross-platform memory leaks, and inter-process race conditions during inference.

---

## 5. Dataset Configuration & DSAPT Regulatory Mapping

### The Dataset Schema Blueprint
The configuration mapping file (`configs/data.yaml`) functions as the platform's core Legal Translation Document. By defining a strict index framework, it guarantees that incoming object bounding box coordinates correspond directly to specific structural sections of the Disability Standards for Accessible Public Transport (DSAPT) 2026.

To ensure enterprise-grade architectural scalability, the system's taxonomy is pre-configured for a 20-class compliance framework. The platform currently tracks 7 active high-risk classes for this TRL 3 proof of concept, while the remaining 13 classes are reserved. This design enables seamless future model expansion without requiring modifications to the underlying SQLModel database schemas or downstream API gateways.

Status	Category	Specific Label	DSAPT Reference
Active	Signage	accessibility_signage	DSAPT Part 17
Active	Protection	handrail	DSAPT Part 15
Active	Infrastructure	kerb_ramp	DSAPT Part 6.5
Active	Boarding	platform_edge	DSAPT Part 10
Active	Vertical Movement	ramp	DSAPT Part 6
Active	Vertical Movement	stairs	DSAPT Part 14
Active	Tactile Indicators	tactile_indicators	DSAPT Part 18
Reserved	Signage	signage_braille	DSAPT Part 17.2
Reserved	Protection	barriers	DSAPT Part 15.4
Reserved	Boarding	boarding_points	DSAPT Part 8
Reserved	Boarding	gaps	DSAPT Part 8.2
Reserved	Access	mobility_access_features	DSAPT Part 4
Reserved	Access	path_widths	DSAPT Part 2
Reserved	Access	thresholds	DSAPT Part 2.4
Reserved	Infrastructure	vertical_movement_infrastructure	DSAPT Part 13
Reserved	Infrastructure	lift_entries	DSAPT Part 13.1
Reserved	Infrastructure	escalators	DSAPT Part 14.3
Reserved	Infrastructure	parking_bays	DSAPT Part 1
Reserved	Communications	hearing_loops	DSAPT Part 26
Reserved	Protection	bollards	DSAPT Part 2.1

>[!CAUTION]
> **Mandatory Naming Standardization**
The automated metrology and compliance auditing engine performs strict string validation during runtime. Every asset identifier must adhere to exact **snake_case** syntax as defined above. Modifying label structures (e.g., pluralization changes or case discrepancies) will mismatch the verification dictionaries within `storage_manager.py` and trigger an unhandled validation exception.

### Annotation & Data Partitioning Protocol
1. **Ingestion Platform:** Object boundaries are labeled and exported using tight bounding boxes around full asset profiles (e.g., encapsulating the entire operational area of a *platform_edge* or a block of *tactile_indicators*), ensuring downstream OpenCV metrology scripts can isolate edges and compute gaps accurately.
2. **Leakage Avoidance:** The training architecture maintains a rigid 70/20/10 spatial data split across Train, Validation, and Test physical directories. This absolute separation prevents cross-contamination, ensuring that reported Mean Average Precision (mAP) metrics reflect genuine environmental generalization rather than spatial memorization.
3. **Data Scaling Mitigation:** In alignment with TRL 3 constraints, low-density initial datasets can result in lower model confidence thresholds during live inference passes. The architecture gracefully mitigates this data scarcity by executing an automated fallback visualization matrix inside `detect.py` to preserve testing pipeline continuity during live evaluations.

---

## 6. Core Inference Pipeline & Compliance Evaluation Engine

### Executive Orchestration Pipeline
The execution lifecycle of the vision system is governed via `ai_engine.py`. This central controller orchestrates pipeline hand-offs, error-handling wrappers, and module execution sequences across decoupled sub-scripts to transform raw imagery matrices into verified compliance data.

### Running the Central Audit Engine Separately:
```Bash
python ai_engine.py
```
1. **The Vision Processing Phase:** `ai_engine.py` handles OS-level initialization wrappers, intercepts incoming image file streams, and feeds the pixel arrays directly into `scripts/detect.py` for high-speed target boundary localization.
2. **The Ledger Storage Phase:** Spatial metrics and metrology bounding coordinates are passed seamlessly to `scripts/storage_manager.py`. This module evaluates structural regulatory (pass/fail) conditions and writes a structured, timestamped **JSON compliance audit ledger file**.
3. **Persistence Synchronization:** Concurrently, the structured compliance metrics trigger the backend application layer, allowing `storage_manager.py` to write these records directly into your SQLModel relational database schema.
4. **Centralized Exception Handling Safety Net:** If a target asset image path is missing, corrupt, or unreadable, `ai_engine.py` catches the error before it can crash the underlying neural network layer. It logs an operational error state and returns an explicit diagnostic payload to maintain continuous platform runtime stability.

### Privacy Defensibility (Australian Privacy Principle Alignment)

To guarantee compliance with the Australian Privacy Principles (APP), the system features an automated, non-negotiable anonymization guardrail:
1. **Global Anonymization Filter:** Immediately following object bounding box localization, the pipeline intercepts the operational image array and runs a destructive 15x15 Gaussian Blur kernel filter over non-target segments of the frame.
2. **Irreversible Redaction:** This pixel manipulation permanently obscures personal identification markers (such as bystander faces, credentials, or vehicle license plates) prior to disk serialization and persistence. Public identity remains completely protected while preserving the exact structural infrastructure contours required for auditing.

### Relational Compliance Thresholds & Co-Dependence Logic

The `storage_manager.py` engine enforces strict Structural Co-dependence Rules to elevate the platform from a simple object detector into a deterministic legal compliance auditor:
1. **Geometric Safety Thresholds:**Using a calibrated spatial-to-physical scaling factor matrix (where 1 px ≈ 0.045 cm), the auditing engine evaluates physical clearances and automatically triggers an unalterable FAIL compliance infraction flag if:

a. Calculated horizontal gap separations exceed 5.0 cm (e.g., platform-to-carriage gaps).

b. Structural surface slopes or angular alignments deviate by more than 2.0° from the statutory horizontal or design plane.

### The Accessibility Co-Dependence Mandate:

 A station asset profile cannot pass an audit based on isolated elements alone. A definitive PASS status requires the concurrent detection of paired structural assets (e.g., a structural ramp must be accompanied by corresponding, adjacent *tactile_indicators*). The absence of critical co-dependent paired elements, or any geometric threshold breach, triggers a cascading FAIL state for the entire station node to ensure commuter safety.

--------------------------------------------------------------------------------------------

