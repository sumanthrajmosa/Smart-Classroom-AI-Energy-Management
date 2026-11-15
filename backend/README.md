# FastAPI backend

This API serves the image-processing outputs already written to disk by the Raspberry Pi pipeline. It does not perform face detection itself.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit CLASSROOM_OUTPUT_DIR to the actual pipeline output directory.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

## Routes

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/classroom-image`
- `GET /api/images`
- `GET /api/images/{image_name}`
- `GET /api/occupancy-report`

If `CLASSROOM_API_KEY` is set, send `Authorization: Bearer <key>` with each request. If it is blank, API-key checking is disabled. Do not expose a public tunnel without appropriate access controls.
