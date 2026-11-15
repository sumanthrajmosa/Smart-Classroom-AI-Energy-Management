# React dashboard

## Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Set `VITE_API_BASE_URL` to the local FastAPI URL during local development or to the exact current Cloudflare Quick Tunnel URL for a remote demo.

Build for deployment:

```bash
npm run build
npm run preview
```

Vite variables are public in the browser bundle. Do not store private credentials in `VITE_*` variables. The dashboard periodically fetches the dashboard JSON, image list, image files and occupancy report from the backend.
