<!-- Status log will go here -->
# RealVsAI - Project Status

## Current State
**Phase:** Phase 0 — Game API implemented (image-only MVP)
**Branch:** `claude/sweet-villani`
**Stack:** Python 3 + FastAPI + SQLAlchemy + SQLite

## What Exists

### Documentation
- `docs/Claude.md` — Project instructions, house rules, multi-agent team workflow
- `docs/PRD.md` — PRD skeleton (awaiting product definition)
- `docs/TechSpec.md` — Phase 0 technical spec (pipeline, schema, services, API)
- `docs/Status.md` — This file

### Server Code (`server/`)
```
server/
  requirements.txt          # fastapi, uvicorn, sqlalchemy, pydantic
  app/
    __init__.py
    config.py               # DB path, SECRET_KEY, game defaults
    database.py             # SQLAlchemy engine + session (SQLite)
    models.py               # ImagePair ORM model
    schemas.py              # Pydantic request/response schemas
    main.py                 # FastAPI app, CORS, lifespan
    seed.py                 # Seeds 20 dummy image pairs for testing
    routes/
      __init__.py
      game.py               # POST /start, POST /guess
```

### API Endpoints

#### `POST /api/v1/game/start`
Start a game session. Returns randomized images without labels.
```
Request:  { "count": 5 }
Response: {
  "session_id": "<signed-token>",
  "total_rounds": 5,
  "rounds": [
    { "round": 1, "image_id": "uuid", "image_url": "https://..." },
    ...
  ]
}
```

#### `POST /api/v1/game/guess`
Submit a guess for one image. Returns the verdict and full reveal.
```
Request:  { "session_id": "...", "image_id": "uuid", "guess": "real" }
Response: {
  "image_id": "uuid",
  "guess": "real",
  "actual": "ai",
  "correct": false,
  "real_image_url": "https://...",
  "ai_image_url": "https://...",
  "prompt_text": "..."
}
```

#### `GET /health`
Returns `{"status": "ok"}`.

### How to Test Quickly
```bash
# Install dependencies
pip install -r server/requirements.txt

# Seed 20 dummy image pairs
python -m server.app.seed

# Start the server
uvicorn server.app.main:app --reload

# Start a game (3 rounds)
curl -X POST http://127.0.0.1:8000/api/v1/game/start \
  -H "Content-Type: application/json" \
  -d '{"count": 3}'

# Submit a guess (use session_id and image_id from start response)
curl -X POST http://127.0.0.1:8000/api/v1/game/guess \
  -H "Content-Type: application/json" \
  -d '{"session_id": "...", "image_id": "...", "guess": "real"}'
```

### Design Notes
- **Stateless sessions:** Session is an HMAC-signed token (no Redis/DB session storage needed). The token encodes which image (real or AI) was shown for each round. Server verifies the signature on every guess — tampered tokens get a 403.
- **No label leaks:** The `/start` response only includes `image_id` and `image_url`. The client cannot tell if the URL is real or AI until it submits a guess.
- **Scoring:** Client-side. Each `/guess` returns `correct: bool`; the frontend tallies the score.

## What Changed (2026-02-15)
- Created full documentation structure
- Defined multi-agent team workflow (CEO, PM, Growth PM, Frontend, Backend, AI Expert, QA, Media)
- Established house rules for code quality, git workflow, and feature request flow
- Added Phase 0 technical spec to `docs/TechSpec.md`
- **Implemented Phase 0 Game API:**
  - Python + FastAPI + SQLAlchemy + SQLite
  - `POST /game/start` — creates session with random image pairs, signed token
  - `POST /game/guess` — validates token, returns verdict + reveal
  - Seed script with 20 dummy pairs
  - All endpoints tested with curl ✓

## Open Bugs
- _None._

## Open Technical Decisions (Phase 0)
- ~~Backend runtime~~ → **Resolved: Python + FastAPI**
- ~~Database~~ → **Resolved: SQLite for dev** (migrate to Postgres for prod)
- Object storage: S3 vs Cloudflare R2
- Pipeline runner: standalone script vs job queue
- Admin UI vs CLI for content moderation
- Verify Together AI FLUX Schnell Free promo is still active

## Open Game Design Questions
- Scoring: should we add streaks, combo bonuses, or time pressure?
- Should there be difficulty levels (easy/medium/hard) that affect which pairs are shown?
- Should the session summary endpoint (`GET /sessions/:id/summary`) be added now?
- Leaderboard: anonymous vs authenticated? Global vs daily?

## Next Tasks
1. Fill in `docs/PRD.md` with Phase 0 product requirements
2. Build the daily image pipeline (Pexels → Gemini → FLUX → storage)
3. Add frontend (web UI for the game)
4. Add session summary endpoint

---
_Last updated: 2026-02-15_
