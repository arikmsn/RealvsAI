"""Pydantic request/response schemas for the Game API."""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# POST /api/v1/game/start
# ---------------------------------------------------------------------------

class GameStartRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=20, description="Number of rounds")


class RoundItem(BaseModel):
    round: int
    image_id: str
    image_url: str


class GameStartResponse(BaseModel):
    session_id: str
    total_rounds: int
    rounds: list[RoundItem]


# ---------------------------------------------------------------------------
# POST /api/v1/game/guess
# ---------------------------------------------------------------------------

class GuessRequest(BaseModel):
    session_id: str
    image_id: str
    guess: str = Field(pattern=r"^(real|ai)$", description="Must be 'real' or 'ai'")


class GuessResponse(BaseModel):
    image_id: str
    guess: str
    actual: str
    correct: bool
    real_image_url: str
    ai_image_url: str
    prompt_text: str
