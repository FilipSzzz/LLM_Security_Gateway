import logging
import re

from fastapi import HTTPException

from app.schemas.enum import DetectorDecision

logger = logging.getLogger(__name__)

regex = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"you\s+are\s+now\s+(in\s+)?developer\s+mode",
    r"system\s+override",
    r"reveal\s+prompt",
]
pattern = re.compile("|".join(regex), re.IGNORECASE)


def detector(prompt: str) -> DetectorDecision:
    if pattern.search(prompt):
        return DetectorDecision.BLOCK
    return DetectorDecision.ALLOW


def detector_check(prompt: str) -> None:
    if detector(prompt) == DetectorDecision.BLOCK:
        logger.warning("prompt blocked by injection detector, length=%d", len(prompt))
        raise HTTPException(400, "Prompt blocked by gateway policy")
