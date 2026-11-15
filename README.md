# Optimized Sensor-Based Energy Efficient Smart Classroom

**Team 107 · Amrita Vishwa Vidyapeetham · School of Computing**

A smart-classroom project intended to support occupancy-aware classroom monitoring and energy management. The current demonstrated software workflow is a Raspberry Pi camera image-processing pipeline connected to a FastAPI backend and a React/Vite dashboard.

> **Implementation status:** The current working demonstration described in the project discussions is the Approach B image-to-dashboard workflow. RFID attendance, ESP32 sensor fusion and relay-based automatic appliance control are part of the broader system design and should be marked as integrated only after their hardware tests are completed.

## Current prototype

- **Edge device:** Raspberry Pi 4 Model B.
- **Camera:** Raspberry Pi Camera Module V2 (Sony IMX219, 8 MP).
- **Face detection:** InsightFace using the `buffalo_l` model and ONNX Runtime CPU execution.
- **Detection coverage:** Image upscaling, overlapping image tiles, coordinate restoration and OpenCV Non-Maximum Suppression (NMS).
- **Privacy processing:** Face crops are downsampled, Gaussian-blurred, modified with random noise, enlarged and smoothed before being placed back into the image.
- **Region analysis:** OpenCV GrabCut body-anchor estimation with a geometric fallback; four calibrated image regions are used.
- **Backend:** FastAPI served by Uvicorn on the Raspberry Pi.
- **Frontend:** React 18 and Vite 6, with Recharts and Lucide React for dashboard presentation.
- **Hosting / remote demo:** Frontend on Vercel; Cloudflare Tunnel can expose the local API through HTTPS.

## Approach B processing flow

```text
Raspberry Pi Camera V2 / classroom image
                  |
                  v
             main.py
          Load and validate
                  |
                  v
        face_detector.py
   InsightFace + image scaling
     + overlapping image tiles
          + duplicate NMS
                  |
                  v
          anonymizer.py
   Downsample -> blur -> noise
       -> resize -> smoothing
                  |
                  v
             utils.py
       GrabCut body anchor
        or geometric fallback
                  |
                  v
       Four calibrated regions
 BACK_LEFT | BACK_RIGHT | FRONT_LEFT | FRONT_RIGHT
                  |
                  v
      Images + occupancy.txt
                  |
                  v
          FastAPI backend
                  |
           Cloudflare Tunnel
                  |
                  v
       React / Vite dashboard
             on Vercel
```

### Important interpretation of the current algorithm

The current Approach B source described in the project documentation assigns a region using the estimated **body anchor** produced by GrabCut or the geometric fallback. It does not assign the region from the face centre. The four current polygons are contiguous; the central aisle is not represented as a separate unassigned region. These details should be changed in code and retested if the final project requirement specifies face-centre assignment or an aisle exclusion.

## Dashboard

The dashboard is organized around the stages of the image-processing pipeline:

1. **Overview** — total occupancy, active regions (out of four), camera status, processing status and region-wise distribution.
2. **Face Detection** — input image and face-detection result.
3. **Face Anonymization** — detected image and anonymized result.
4. **Zone Division** — anonymized image with region boundaries and occupancy annotations.
5. **Final Classroom Result** — final annotated classroom image.
6. **Live Monitoring** — periodically refreshed backend data and images.

The frontend uses `VITE_API_BASE_URL` for the backend base URL and `VITE_REFRESH_MS` for the refresh interval (default: 10,000 ms). Vite environment variables are embedded in the public frontend build; do not place secrets in `VITE_*` variables.

## Output files

The Approach B pipeline produces the following files in its configured output directory:

| File | Purpose |
|---|---|
| `input.jpg` | Original input copy |
| `detected.jpg` | Face-detection visualization |
| `anonymized.jpg` | Face-anonymized image |
| `zone_division.jpg` | Region and occupancy visualization |
| `classroom_result.jpg` | Final annotated result |
| `occupancy.txt` | Text occupancy and processing report |

The backend is configured to read the output directory and serve the images and report through its API.

## Repository structure

The repository contains the Python image-processing modules at its root. The FastAPI backend and React/Vite dashboard are now included in this repository under `backend/` and `frontend/`. The deployed dashboard can still use Vercel and a Cloudflare Tunnel to reach the Raspberry Pi API.

```text
Smart-Classroom-AI-Energy-Management/
├── main.py
├── config.py
├── face_detector.py
├── anonymizer.py
├── utils.py
├── requirements.txt
├── input/                       # Add local classroom images; not committed
├── output/                      # Generated outputs; not committed
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI routes
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── README.md
└── docs/
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT.md
    └── IMPLEMENTATION_STATUS.md
```

See the documentation files in `docs/` for architecture, setup/deployment notes and implementation status.

## Python pipeline setup

Use a Python environment compatible with the installed InsightFace and ONNX Runtime wheels on the Raspberry Pi OS image. The exact Python version and package versions should be verified on the target Pi.

```bash
git clone https://github.com/sumanthrajmosa/Smart-Classroom-AI-Energy-Management.git
cd Smart-Classroom-AI-Energy-Management

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Place the classroom image at the path configured by `config.py` (the current uploaded Approach B configuration uses an input directory and supports the configured classroom image names), then run:

```bash
python main.py
```

Inspect the generated images and occupancy report in the output directory. The first InsightFace run may need to download model assets; ensure the Pi has network access and enough free storage.

> **Dependency note:** Review `requirements.txt` against the exact target Raspberry Pi OS/Python version before installation. Deep-learning packages and model dependencies can be platform-sensitive. Do not assume every optional package listed in the file is required by the current Approach B pipeline.

## FastAPI backend and dashboard deployment

The dashboard/backend application is maintained separately from the root Python pipeline. The deployed demonstration uses:

- FastAPI backend running on the Raspberry Pi at `127.0.0.1:8000`.
- Uvicorn to serve the FastAPI application.
- Cloudflare Tunnel for remote HTTPS access to the local backend.
- React/Vite frontend deployed on Vercel.

Typical backend launch command (from the backend project directory, after activating its virtual environment):

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the temporary Cloudflare Quick Tunnel in another terminal:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Set the exact generated tunnel URL as `VITE_API_BASE_URL` in the Vercel project and redeploy the frontend. A Quick Tunnel URL can change after restarting the tunnel, so update the environment variable when that happens. Keep both Uvicorn and the tunnel process running during the demonstration.

The backend endpoints used by the dashboard are:

- `/api/health`
- `/api/dashboard`
- `/api/classroom-image`
- `/api/images`
- `/api/images/{image_name}`
- `/api/occupancy-report`

## Broader smart-classroom design

The overall project design also considers:

- Teacher-created timetable slots.
- RFID reader and tags for student/slot validation.
- ESP32-S3 as a sensor/controller node.
- PIR-based presence sensing and ultrasonic backup sensing.
- Light-intensity and temperature sensing.
- Acoustic/noise monitoring.
- Relay modules for electrical appliance switching.
- Occupancy and energy analytics for administrators.

These are extension/integration targets unless the corresponding hardware workflow has been physically connected and verified. The camera dashboard by itself does not prove automatic energy savings.

## Privacy and security

- Expose anonymized images rather than original identifiable classroom images.
- The described demo configuration had an empty `CLASSROOM_API_KEY`; optional API-key protection is therefore not active in that setup.
- Do not expose student identities, attendance records or original classroom photographs through a public tunnel.
- Use authentication, HTTPS, access restrictions and an appropriate retention policy before deployment in a real classroom.
- Visual blurring/pixel modification is a privacy measure, not a mathematical guarantee of irreversible anonymization.

## Known limitations and validation

- Face detection can miss small, occluded or turned faces.
- Overlapping tiles improve coverage but increase inference work.
- GrabCut can select desks/background/nearby people in crowded scenes.
- The geometric fallback is approximate.
- Body-anchor region assignment can differ from face-centre-based manual calibration.
- Current image processing should not be described as validated real-time video tracking without measured throughput.
- Detection accuracy, region-assignment accuracy, latency and energy savings must be measured on a labelled test set and physical power measurements before numerical claims are made.

## Contributors

**Team 107 — Amrita Vishwa Vidyapeetham, School of Computing**

- MEDAPATI NAGA VENKATA CHARAN REDDY
- MOSA SUMANTHRAJ
- KUDIRELLA SAI TEJASH
- PALASANI RAMA VENKATA LATHAN
- ASWIN POTTA

**Project Guide:** Dr. R. Karthi

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE).
