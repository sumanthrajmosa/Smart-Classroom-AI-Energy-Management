# Deployment Notes

## Raspberry Pi image pipeline

1. Install Raspberry Pi OS 64-bit and connect the Raspberry Pi Camera Module V2.
2. Clone this repository and create a Python virtual environment.
3. Install the dependencies after checking compatibility with the Python version and Raspberry Pi OS image.
4. Place the classroom image in the input location configured by `config.py`.
5. Run `python main.py`.
6. Inspect the configured output directory for the generated images and occupancy report.

```bash
git clone https://github.com/sumanthrajmosa/Smart-Classroom-AI-Energy-Management.git
cd Smart-Classroom-AI-Energy-Management
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The first InsightFace run may download model assets. Ensure network access and sufficient disk space. Check the exact model and package versions on the target Pi before a demonstration.

## FastAPI backend

The dashboard backend is a separate application from the root image-processing scripts. From its backend directory, activate its virtual environment and run:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Check local health:

```bash
curl http://127.0.0.1:8000/api/health
```

The backend must be configured to read the same output directory used by the image pipeline.

## Cloudflare Tunnel demo

In a second terminal on the Pi:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Copy the HTTPS Quick Tunnel URL printed by Cloudflare. Quick Tunnel URLs are temporary and can change after restart. Keep the tunnel and Uvicorn processes running while the dashboard is in use.

## Vercel frontend

Set these environment variables in the Vercel project:

- `VITE_API_BASE_URL`: current HTTPS tunnel URL.
- `VITE_REFRESH_MS`: dashboard refresh interval in milliseconds (for example, `10000`).
- `VITE_API_KEY`: only if backend API-key authentication is enabled.

Redeploy after changing Vite environment variables. Values prefixed with `VITE_` are included in the public frontend bundle; never put private credentials there.

## Security

Do not expose original identifiable classroom images or student records through a public tunnel. Enable authentication and access restrictions before real classroom use. A blank optional API-key setting means API-key authentication is not active.
