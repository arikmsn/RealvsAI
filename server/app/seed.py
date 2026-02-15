"""Seed the database with dummy image pairs for local testing.

Usage:
    python -m server.app.seed
"""

import logging

from server.app.database import Base, SessionLocal, engine
from server.app.models import ImagePair

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

SEED_PAIRS = [
    {
        "source_provider": "pexels",
        "source_image_id": f"seed-{i}",
        "real_image_url": f"https://picsum.photos/seed/real{i}/800/600",
        "ai_image_url": f"https://picsum.photos/seed/ai{i}/800/600",
        "prompt_text": f"Seed image pair {i}: a beautiful landscape photograph",
        "difficulty": (i % 5) + 1,
        "tags": '["seed", "test"]',
        "status": "approved",
    }
    for i in range(1, 21)
]


def seed():
    """Insert 20 dummy image pairs (skip if they already exist)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(ImagePair).count()
        if existing >= 20:
            logger.info("Database already has %d pairs, skipping seed.", existing)
            return

        for data in SEED_PAIRS:
            pair = ImagePair(**data)
            db.add(pair)

        db.commit()
        logger.info("Seeded %d image pairs.", len(SEED_PAIRS))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
