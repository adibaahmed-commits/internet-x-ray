# XTrace Backend

FastAPI backend for uploading apartment building photos and getting Gemini-powered analysis.

## Setup

1. `cd backend`
2. Create and activate a virtual environment:
   - Windows: `python -m venv venv && venv\Scripts\activate`
   - Mac/Linux: `python -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in real values (see Environment Variables below)
5. `uvicorn main:app --reload`

Server runs at `http://localhost:8000`. Interactive API docs (Swagger UI) at `http://localhost:8000/docs`.

## Environment Variables

| Var | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | API key for Gemini analysis calls. Server will not start without this set. |
| `DATABASE_URL` | No | `sqlite:///./buildings.db` | Database connection string |
| `UPLOAD_FOLDER` | No | `uploads` | Local folder where uploaded images are stored |

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Root/home check |
| GET | `/health` | Health check |
| GET | `/buildings/ping` | Building routes liveness check |
| POST | `/buildings/upload` | Upload a building image (JPG/PNG, max 10MB) |
| GET | `/buildings` | List all buildings |
| GET | `/buildings/{building_id}` | Get a single building's detail, including analysis if complete |
| POST | `/buildings/{building_id}/analyze` | Run Gemini analysis on a building's uploaded image |

All error responses share a consistent shape: `{"error": "..."}`.

## Testing

```bash
pytest -v
```

Tests cover the upload flow, analyze flow (with Gemini calls mocked), list/detail endpoints, and invalid file handling.

## Notes for frontend integration

- `POST /buildings/upload` expects `multipart/form-data` with a `file` field. Only `.jpg`/`.jpeg`/`.png`, max 10MB.
- `analysis_json` on a building is `null` until `/analyze` has been run successfully; after that it's populated with structured analysis data (`building_type`, `condition`, `notable_features`, etc.).
- Building `status` moves through: `pending` → `analyzing` → `complete` (or `failed` if analysis errors out).
- Uploaded images are served statically at `/uploads/{filename}`.

## Deployed

Live at: https://xtrace-backend.onrender.com
