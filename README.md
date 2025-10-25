# Lumera

Full‑stack AI facial analysis application combining a FastAPI backend with a Next.js (TypeScript + Tailwind) frontend. The backend loads a ConvNeXt‑Tiny model for attribute prediction and uses Google Gemini to generate rich, human‑readable summaries and an HTML report. Large model artifacts are not stored in Git; they’re downloaded automatically from Google Drive on first run.

## Monorepo layout

```
Lumera/
├─ backend/        # FastAPI service (AI inference, Gemini summaries, reports)
│  ├─ app.py       # API: /predict, /consent, /health
│  ├─ model/       # Model files (ignored by git; downloaded at runtime)
│  ├─ static/      # Saved user images and generated reports
│  ├─ utils/       # Helpers (cropping, etc.)
│  ├─ requirements.txt
│  └─ QUICKSTART.md · MODEL_DEPLOYMENT.md · MODEL_LOADER_SETUP.md
└─ frontend/       # Next.js (App Router, TS, Tailwind)
	├─ src/ | public/
	└─ package.json | next.config.ts | tailwind.config.ts
```

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm (or pnpm/yarn/bun)
- A Google Gemini API key
- A Google Drive link for the model (.pth) and the model loader code

## Quick start

### 1) Backend setup (FastAPI)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create your environment
copy .env.example .env
# Then edit .env and fill:
# GEMINI_API_KEY=your_key
# MODEL_DOWNLOAD_URL=https://drive.google.com/file/d/<file_id>/view?usp=sharing
# MODEL_LOADER_URL=https://drive.google.com/file/d/<file_id>/view?usp=sharing

# Optional helper to set MODEL_DOWNLOAD_URL quickly
python setup_model_url.py "<your_google_drive_model_link>"

# (Optional) Test model download
python download_model.py

# Run the API
uvicorn app:app --reload --port 8000
```

API endpoints:
- POST `/predict` – upload an image (form-data file) to analyze; returns attributes, summary, and a link to an HTML report under /static/reports
- POST `/consent` – body: `{ "filename": "<cropped_filename>.jpg" }` to persist a user’s image
- GET `/health` – health check

### 2) Frontend setup (Next.js)

```powershell
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

Ensure the frontend uses the backend base URL (e.g., http://localhost:8000). If you use environment variables, create `frontend/.env.local` and set `NEXT_PUBLIC_API_URL` accordingly.

## Large files are ignored (no big pushes)

This repo is configured to avoid committing large artifacts:
- `*.pth` and `backend/model/*.pth` are ignored
- `static/uploads/`, `static/accepted/`, and generated reports are ignored
- Node build artifacts (`frontend/.next/`, `node_modules/`) are ignored

If a large file was previously committed, removing it from history requires a rewrite (we can help run `git filter-repo` on request). Going forward, `.gitignore` prevents new large files from being tracked.

## Deployment notes

- The model and loader code are downloaded from Google Drive on first run; ensure `.env` is configured in your hosting platform (Render/Railway/etc.) with `GEMINI_API_KEY`, `MODEL_DOWNLOAD_URL`, and `MODEL_LOADER_URL`.
- The backend writes images and HTML reports to `backend/static/*`. Use persistent storage in production if you need to retain them.
- Frontend can be deployed to Vercel/Netlify; set `NEXT_PUBLIC_API_URL` to your backend URL.

## Security

- Do not commit API keys; use `.env` and host environment variables.
- The model loader code can be stored outside Git and fetched from Google Drive; see `backend/MODEL_LOADER_SETUP.md`.
- Uploaded images are saved under `backend/static/user_images/`; ensure consent and data retention policies are followed.

## Scripts you’ll use

- `backend/setup_model_url.py` – quickly configure the model URL in `.env`
- `backend/download_model.py` – fetch and cache the model (manual test)
- `backend/QUICKSTART.md` – one-page guide
- `backend/MODEL_DEPLOYMENT.md` – detailed docs

## Troubleshooting

- Model fails to load: verify Google Drive link is public and `.env` values are present
- 400 “face is not visible”: upload a clear face image; the backend performs face cropping and throws if none is detected
- CORS: ensure your frontend origin is allowed in `app.py`

---

Lumera – AI-powered facial attribute insights with shareable HTML reports 🚀