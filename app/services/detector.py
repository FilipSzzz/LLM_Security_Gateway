import logging
import re
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException

from app.schemas.enum import DetectorDecision

logger = logging.getLogger(__name__)

RULES_FILE = Path(__file__).parent / "rules" / "injection.toml"


@dataclass(frozen=True)
class Rule:
    reason: str
    pattern: re.Pattern[str]
    raw: bool


@dataclass(frozen=True)
class DetectorResult:
    decision: DetectorDecision
    reason: str | None = None


def load_rules(path: Path) -> tuple[str, list[Rule]]:
    with path.open("rb") as f:
        data = tomllib.load(f)
    rules = []
    for reason, group in data["rules"].items():
        for p in group.get("patterns", []):
            rules.append(Rule(reason, re.compile(rf"\b(?:{p})\b", re.IGNORECASE), raw=False))
        for p in group.get("raw_patterns", []):
            rules.append(Rule(reason, re.compile(p, re.IGNORECASE), raw=True))
    return data["version"], rules


def strip_invisible(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if unicodedata.category(c) not in ("Mn", "Cf"))


def simplify(text: str) -> str:
    text = re.sub(r"['’]", "", text.lower())
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return re.sub(r"\b(\w) (?=\w\b)", r"\1", text)


class RegexInjectionDetector:
    name = "regex-injection"

    def __init__(self, rules_file: Path) -> None:
        self.version, self.rules = load_rules(rules_file)

    def check(self, text: str) -> DetectorResult:
        raw = strip_invisible(text)
        simple = simplify(raw)
        for rule in self.rules:
            if rule.pattern.search(raw if rule.raw else simple):
                return DetectorResult(DetectorDecision.BLOCK, rule.reason)
        return DetectorResult(DetectorDecision.ALLOW)


regex_detector = RegexInjectionDetector(RULES_FILE)


def detector_check(prompt: str) -> None:
    result = regex_detector.check(prompt)
    if result.decision == DetectorDecision.BLOCK:
        logger.warning(
            "prompt blocked: detector=%s version=%s reason=%s length=%d",
            regex_detector.name,
            regex_detector.version,
            result.reason,
            len(prompt),
        )
        raise HTTPException(400, "Prompt blocked by gateway policy")
