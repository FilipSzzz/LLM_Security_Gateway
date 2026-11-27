import re

EMAIL_PLACEHOLDER = "[EMAIL]"

# RFC 5322 "practical" pattern without ^ and $, so it finds addresses inside a prompt.
# The domain needs at least one dot, so "user@localhost" is not masked.
EMAIL_RE = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
    re.IGNORECASE,
)


def mask_emails(text: str) -> tuple[str, int]:
    """Replace every e-mail address with a placeholder. Return the new text and the count."""
    return EMAIL_RE.subn(EMAIL_PLACEHOLDER, text)
