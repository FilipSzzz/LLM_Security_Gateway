import pytest

from app.services.email_detector import mask_emails


@pytest.mark.parametrize(
    ("text", "expected", "count"),
    [
        ("john@example.com", "[EMAIL]", 1),
        ("My email is john@example.com, thanks", "My email is [EMAIL], thanks", 1),
        ("a@x.com and b.c+tag@mail.example.pl", "[EMAIL] and [EMAIL]", 2),
        ("Write to John@Example.COM", "Write to [EMAIL]", 1),
        ("Write to a@b.com.", "Write to [EMAIL].", 1),
    ],
)
def test_masks_emails(text, expected, count):
    assert mask_emails(text) == (expected, count)


@pytest.mark.parametrize("text", ["user@localhost", "follow @handle", "no address here"])
def test_leaves_non_emails(text):
    assert mask_emails(text) == (text, 0)
