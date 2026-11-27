import re

from app.services.email_detector import mask_emails
from app.services.pesel_checksum import check_validation

PESEL_RE = re.compile(r"(?<!\d)\d{11}(?!\d)")
CARD_RE = re.compile(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)")


def _luhn(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0


def _mask(pattern: re.Pattern[str], text: str, placeholder: str, is_valid) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        if not is_valid(re.sub(r"[ -]", "", match.group())):
            return match.group()
        count += 1
        return placeholder

    return pattern.sub(repl, text), count


def mask_pesels(text: str) -> tuple[str, int]:
    return _mask(PESEL_RE, text, "[PESEL]", check_validation)


def mask_cards(text: str) -> tuple[str, int]:
    return _mask(CARD_RE, text, "[CARD]", _luhn)


def mask_pii(text: str) -> tuple[str, dict[str, int]]:
    """Mask cards, PESELs and e-mails. Return the new text and the count per kind."""
    text, cards = mask_cards(text)
    text, pesels = mask_pesels(text)
    text, emails = mask_emails(text)
    return text, {"card": cards, "pesel": pesels, "email": emails}
