"""Game API endpoints for the image-only Real vs AI game."""

import base64
import hashlib
import hmac
import json
import logging
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.app.config import DEFAULT_ROUND_COUNT, MAX_ROUND_COUNT, SECRET_KEY
from server.app.database import get_db
from server.app.models import ImagePair
from server.app.schemas import (
    GameStartRequest,
    GameStartResponse,
    GuessRequest,
    GuessResponse,
    RoundItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/game", tags=["game"])


# ---------------------------------------------------------------------------
# Session token helpers (stateless HMAC-signed JSON)
# ---------------------------------------------------------------------------

def _sign_token(payload: dict) -> str:
    """Encode payload as base64 JSON and append an HMAC signature."""
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode()
    signature = hmac.new(
        SECRET_KEY.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()
    return f"{payload_b64}.{signature}"


def _verify_token(token: str) -> dict:
    """Verify HMAC signature and return decoded payload. Raises on tamper."""
    parts = token.rsplit(".", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid session token format")

    payload_b64, signature = parts
    try:
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session token encoding")

    expected = hmac.new(
        SECRET_KEY.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=403, detail="Session token signature mismatch")

    return json.loads(payload_bytes)


# ---------------------------------------------------------------------------
# POST /api/v1/game/start
# ---------------------------------------------------------------------------

@router.post("/start", response_model=GameStartResponse)
def start_game(body: GameStartRequest, db: Session = Depends(get_db)):
    """Start a new game session with a random set of image pairs."""
    count = min(body.count, MAX_ROUND_COUNT)

    # Select random approved pairs
    pairs = (
        db.query(ImagePair)
        .filter(ImagePair.status == "approved")
        .order_by(func.random())
        .limit(count)
        .all()
    )

    if not pairs:
        raise HTTPException(status_code=404, detail="No approved image pairs available")

    # For each pair, randomly decide which image (real or ai) to show
    rounds: list[RoundItem] = []
    token_map: dict[str, str] = {}  # image_id -> "real" | "ai"

    for idx, pair in enumerate(pairs, start=1):
        shown_type = random.choice(["real", "ai"])
        image_url = pair.real_image_url if shown_type == "real" else pair.ai_image_url
        token_map[pair.id] = shown_type
        rounds.append(RoundItem(round=idx, image_id=pair.id, image_url=image_url))

    session_id = _sign_token({"rounds": token_map})
    logger.info("Game started with %d rounds", len(rounds))

    return GameStartResponse(
        session_id=session_id,
        total_rounds=len(rounds),
        rounds=rounds,
    )


# ---------------------------------------------------------------------------
# POST /api/v1/game/guess
# ---------------------------------------------------------------------------

@router.post("/guess", response_model=GuessResponse)
def submit_guess(body: GuessRequest, db: Session = Depends(get_db)):
    """Submit a guess for a single image and get the result."""
    payload = _verify_token(body.session_id)
    round_map: dict[str, str] = payload.get("rounds", {})

    if body.image_id not in round_map:
        raise HTTPException(
            status_code=400,
            detail=f"image_id '{body.image_id}' not found in this session",
        )

    actual = round_map[body.image_id]  # "real" or "ai"
    correct = body.guess == actual

    # Fetch the full pair for the reveal
    pair = db.query(ImagePair).filter(ImagePair.id == body.image_id).first()
    if not pair:
        raise HTTPException(status_code=404, detail="Image pair not found in database")

    logger.info(
        "Guess for %s: guessed=%s actual=%s correct=%s",
        body.image_id, body.guess, actual, correct,
    )

    return GuessResponse(
        image_id=body.image_id,
        guess=body.guess,
        actual=actual,
        correct=correct,
        real_image_url=pair.real_image_url,
        ai_image_url=pair.ai_image_url,
        prompt_text=pair.prompt_text,
    )
