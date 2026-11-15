# System Architecture

## Current demonstrated workflow

The current software demonstration is an image-based Raspberry Pi pipeline connected to a FastAPI backend and React/Vite dashboard.

1. A classroom image is loaded from the configured input directory.
2. InsightFace (`buffalo_l`) detects faces using ONNX Runtime CPU execution.
3. The detector scales the image, processes overlapping tiles, restores coordinates and applies OpenCV NMS to remove duplicate detections.
4. Face regions are anonymized by downsampling, Gaussian blur, random pixel noise, resizing and bilateral smoothing.
5. OpenCV region analysis estimates a body anchor with GrabCut and a geometric fallback, then assigns the detection to one of four configured regions.
6. The pipeline saves visual outputs and an occupancy report.
7. FastAPI serves the dashboard data, images and occupancy report.
8. React/Vite periodically requests the API and displays the pipeline and occupancy summaries.

## Hardware

- Raspberry Pi 4 Model B.
- Raspberry Pi Camera Module V2 (Sony IMX219, 8 MP).

Other sensors and controller components (ESP32-S3, RFID, PIR, ultrasonic, LDR, temperature sensor, acoustic sensor and relay module) belong to the broader system design. Treat them as planned or partially integrated until physical tests verify their operation.

## Four-region model

The dashboard uses four logical regions:

- BACK_LEFT
- BACK_RIGHT
- FRONT_LEFT
- FRONT_RIGHT

The current root-repository `utils.py` uses configured polygon splits and face-box centre points for its region calculation. The later Approach B body-segmentation implementation discussed in project documentation uses GrabCut/body-anchor estimation and has different behavior. Keep the exact deployed source synchronized with the implementation being demonstrated; do not assume similarly named files in separate working folders are identical.

## Backend and frontend

The integrated dashboard application is maintained separately from this root Python pipeline. The backend is FastAPI/Uvicorn; the frontend is React 18/Vite 6 with Recharts and Lucide React. Cloudflare Tunnel can expose the local API over HTTPS, and the frontend can be hosted on Vercel.

The backend API used by the dashboard includes:

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/classroom-image`
- `GET /api/images`
- `GET /api/images/{image_name}`
- `GET /api/occupancy-report`

## Data flow

```text
Camera / classroom image
        |
        v
Python image-processing pipeline
        |
        +--> detected image
        +--> anonymized image
        +--> zone/final result images
        +--> occupancy report
                    |
                    v
              FastAPI backend
                    |
             HTTPS tunnel (demo)
                    |
                    v
             React dashboard
```

## Privacy and security

Only anonymized classroom imagery and aggregate occupancy should be exposed in a public demo. The earlier demo configuration used a blank optional API key, which means API-key authentication was not enabled. Do not publish original identifiable images, student identities or attendance data. Production use requires authentication, access controls, HTTPS, and a data-retention policy.
