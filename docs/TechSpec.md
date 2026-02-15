# RealVsAI - Technical Specification

## 1. Architecture Overview
<!-- High-level system diagram description. -->
_To be defined after PRD is finalized._

## 2. Tech Stack
| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | _TBD_ | |
| Backend | _TBD_ | |
| Database | _TBD_ | |
| AI/ML | _TBD_ | |
| Hosting | _TBD_ | |
| CDN / Media | _TBD_ | |

## 3. Data Models
<!-- Key entities and their relationships. -->
_To be defined._

## 4. API Design
<!-- Endpoints, auth, rate limiting. -->
_To be defined._

## 5. AI Pipeline
<!-- How AI-generated content is created, validated, and served. -->
_To be defined._

## 6. Frontend Architecture
<!-- Component structure, state management, routing. -->
_To be defined._

## 7. Authentication & Authorization
<!-- Auth flow, user roles, session management. -->
_To be defined._

## 8. Media Pipeline
<!-- Video storage, transcoding, delivery. -->
_To be defined._

## 9. Performance & Scalability
<!-- Caching strategy, CDN, load expectations. -->
_To be defined._

## 10. Security Considerations
<!-- OWASP, input validation, content moderation. -->
_To be defined._

## 11. Testing Strategy
<!-- Unit, integration, E2E, load testing. -->
_To be defined._

## 12. DevOps & CI/CD
<!-- Build pipeline, deployment strategy, environments. -->
_To be defined._

---

## Phase 0 – Image-Only Daily Pipeline and Game

### P0.1 Overview

Phase 0 is an image-only MVP. No video, no user accounts, no leaderboard.
A daily pipeline creates 50 real/AI image pairs. A lightweight game API serves
them to players who guess "Real or AI?" one image at a time.

### P0.2 Daily Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  CRON / Scheduled Worker  (runs once per day, e.g. 03:00 UTC)      │
│                                                                      │
│  1. Fetch 50 real photos ──► Pexels or Unsplash API                 │
│              │                                                       │
│  2. For each photo:                                                  │
│     ├─ Send image to Vision LLM ──► Gemini 2.5 Flash-Lite          │
│     │   → returns a descriptive prompt                              │
│     │                                                                │
│     └─ Send prompt to Image Gen API ──► Together AI (FLUX Schnell)  │
│         → returns an AI-generated image                             │
│                                                                      │
│  3. Upload both images to Object Storage (S3 / Cloudflare R2)      │
│                                                                      │
│  4. Write image_pairs row to database                                │
└──────────────────────────────────────────────────────────────────────┘
```

**Pipeline steps in detail:**

| Step | Input | Action | Output |
|------|-------|--------|--------|
| 1 – Fetch real images | Search query (random topic/keyword) | `GET /v1/search/photos` (Pexels) | 50 photo URLs + metadata |
| 2a – Generate prompt | Real image URL | Gemini 2.5 Flash-Lite: "Describe this image in detail suitable as a text-to-image prompt" | Prompt string |
| 2b – Generate AI image | Prompt string | Together AI FLUX.1 Schnell Free endpoint | AI image URL / binary |
| 3 – Store images | Real photo download + AI image binary | Upload to object storage bucket | `real_image_url`, `ai_image_url` |
| 4 – Persist metadata | All of the above | INSERT into `image_pairs` table | Row with UUID |

**Error handling:** If any single pair fails (API timeout, content filter, etc.),
log the error and skip that pair. Aim for ≥45 successful pairs per run. The
pipeline is idempotent — re-running on the same day fills gaps without duplicates
(keyed on `source_image_id + date`).

### P0.3 Database Schema

```sql
CREATE TABLE image_pairs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    real_image_url  TEXT        NOT NULL,
    ai_image_url    TEXT        NOT NULL,
    prompt_text     TEXT        NOT NULL,
    source_provider TEXT        NOT NULL,          -- 'pexels' | 'unsplash'
    source_image_id TEXT        NOT NULL,          -- original ID from provider
    difficulty      SMALLINT    DEFAULT 3,         -- 1 (easy) to 5 (hard), set later
    tags            TEXT[]      DEFAULT '{}',      -- e.g. {'nature','portrait'}
    status          TEXT        NOT NULL DEFAULT 'pending',  -- 'pending' | 'approved' | 'rejected'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_source_per_day UNIQUE (source_image_id, (created_at::date))
);

CREATE INDEX idx_image_pairs_status   ON image_pairs (status);
CREATE INDEX idx_image_pairs_created  ON image_pairs (created_at);
CREATE INDEX idx_image_pairs_tags     ON image_pairs USING GIN (tags);
```

**Column notes:**
| Column | Purpose |
|--------|---------|
| `id` | Primary key, used in API responses. Never exposes real-vs-AI. |
| `real_image_url` / `ai_image_url` | URLs in our own object storage (not provider hotlinks). |
| `prompt_text` | The prompt generated by the Vision LLM — useful for debugging and future difficulty tuning. |
| `source_provider` | Which free image API the real photo came from. |
| `source_image_id` | The provider's original ID, for attribution and dedup. |
| `difficulty` | Optional. Can be set manually or by a future ML model that scores how hard each pair is. |
| `tags` | Category labels; used for themed game sessions later. |
| `status` | Allows a manual or automated moderation step before images go live. |

### P0.4 External Services

#### Image Source APIs (real photos)

| Service | Free Tier Limits | Pros | Cons |
|---------|-----------------|------|------|
| **Pexels API** (recommended) | 200 req/hr, 20K req/month | High-quality curated photos; generous limits; no attribution required in-app (credit in metadata). Simple REST API. | Smaller library than Unsplash; photos lean editorial. |
| **Unsplash API** | 50 req/hr (demo); 5K req/hr (production) | Massive library (5M+ photos); great search; well-documented. | Demo mode very restrictive (50/hr = barely 50 images/day with search + download). Must apply for production. Attribution required. |

**Recommendation:** Start with **Pexels**. 200 req/hr is enough for 50 images/day
with headroom. Apply for Unsplash production access in parallel as a backup.

#### Vision LLM (image → prompt)

| Service | Free Tier Limits | Pros | Cons |
|---------|-----------------|------|------|
| **Gemini 2.5 Flash-Lite** (recommended) | 1,000 req/day, rate-limited per minute | Generous daily quota (50 images/day = 5% of limit). Fast. Accepts image URLs directly. | Quota resets at midnight PT. Google may change limits without notice (happened Dec 2025). |

**Note:** 50 req/day uses only 5% of the 1,000 daily limit, leaving ample room
for retries and future growth to 200 pairs/day.

#### Text-to-Image API (prompt → AI image)

| Service | Free Tier Limits | Pros | Cons |
|---------|-----------------|------|------|
| **Together AI – FLUX.1 Schnell Free** (recommended) | Free unlimited access via `FLUX.1-schnell-Free` endpoint | Truly free; fast (~315ms/image); high quality for a free model. Simple REST API. | "Free" promo may end (was announced as 3-month offer — verify current status). Quality below FLUX Pro / DALL-E 3. |
| **Stability AI – SD 3.5 API** | Pay-per-credit (~$0.01/credit) | High quality; self-host option for $0 under Community License (<$1M revenue). | No real free API tier — only self-hosted is free, which needs GPU infra. |

**Recommendation:** Start with **Together AI FLUX Schnell Free**. It is the only
option with a genuinely free API tier that doesn't require self-hosting. Keep
Stability AI as a paid fallback if the promo ends.

### P0.5 Game API Endpoints

All endpoints are public (no auth in Phase 0). Rate-limited by IP.

#### `POST /api/v1/game/sessions`

Start a new game session. Returns a randomized sequence of image pair IDs.

```
Request:  { "count": 10 }          // optional, default 10, max 20
Response: {
    "session_id": "uuid",
    "rounds": [
        { "round": 1, "image_pair_id": "uuid" },
        { "round": 2, "image_pair_id": "uuid" },
        ...
    ]
}
```

**Logic:** Selects `count` random pairs where `status = 'approved'`. Stores
session in DB or cache (Redis / in-memory) with TTL of 30 minutes.

#### `GET /api/v1/game/rounds/:image_pair_id`

Fetch a single round. Returns **one** image at a time without revealing which
type it is.

```
Request:  GET /api/v1/game/rounds/{image_pair_id}?pick=left
Response: {
    "image_pair_id": "uuid",
    "left":  { "image_url": "https://cdn.../img_a.jpg" },
    "right": { "image_url": "https://cdn.../img_b.jpg" }
}
```

**Logic:** Randomly assigns `real` and `ai` to left/right positions. The
assignment is stored in the session so it's consistent if the client re-fetches.
No metadata about which is real is ever sent to the client.

#### `POST /api/v1/game/rounds/:image_pair_id/guess`

Submit a guess for one round.

```
Request:  { "session_id": "uuid", "guess": "left" }   // "left" or "right"
Response: {
    "correct": true,
    "real_side": "right",
    "real_image_url": "https://cdn.../real.jpg",
    "ai_image_url": "https://cdn.../ai.jpg",
    "prompt_text": "A serene mountain lake at sunset..."
}
```

**Logic:** Compares `guess` against the session's stored assignment. Returns
the answer plus both URLs and the generation prompt (fun reveal moment).
Each round can only be guessed once per session.

#### `GET /api/v1/game/sessions/:session_id/summary`

Get final score after all rounds are played.

```
Response: {
    "session_id": "uuid",
    "total_rounds": 10,
    "correct": 7,
    "accuracy_pct": 70.0,
    "rounds": [
        { "round": 1, "image_pair_id": "uuid", "guessed": "left", "correct": true },
        ...
    ]
}
```

### P0.6 Open Technical Questions (Phase 0)

- [ ] Confirm Together AI FLUX Schnell Free is still available (verify current promo status).
- [ ] Decide on object storage: S3 vs Cloudflare R2 (R2 has free egress).
- [ ] Decide on database: PostgreSQL (Supabase free tier? Neon free tier? Local Docker?).
- [ ] Decide on backend runtime: Node/Express vs Python/FastAPI.
- [ ] Should the pipeline be a standalone script or a proper job queue (e.g. BullMQ)?
- [ ] Do we need an admin UI for `status` moderation, or is a CLI/script enough for Phase 0?

## 13. Open Technical Questions
<!-- Unresolved technical decisions. -->
- See Phase 0 open questions above.

---
_Last updated: 2026-02-15_
